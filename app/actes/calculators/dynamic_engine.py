import json
from decimal import Decimal
from typing import Dict, Any, List
import simpleeval

from app.models import BaremeModele, BaremeLigneCalcul
from app.actes.calculators.shared import SharedCalculator

class DynamicCalculatorEngine:
    
    @staticmethod
    def _evaluate_condition(condition_str: str, context: Dict[str, Any]) -> bool:
        """Evalue une condition logique (ex: 'taux_enreg == 1' ou 'avec_morcellement')"""
        if not condition_str or condition_str.strip() == '':
            return True
        try:
            # We allow basic comparisons and logic
            result = simpleeval.simple_eval(condition_str, names=context)
            return bool(result)
        except Exception as e:
            # Log error in real app
            print(f"Erreur évaluation condition '{condition_str}': {e}")
            return False

    @staticmethod
    def _evaluate_formula(formula_str: str, context: Dict[str, Any]) -> Decimal:
        """Evalue une formule mathématique basée sur les variables du contexte"""
        if not formula_str or formula_str.strip() == '':
            return Decimal('0')
            
        functions = {
            'min': min,
            'max': max,
            'arrondi_mille': SharedCalculator.roundup_thousand,
        }
        try:
            result = simpleeval.simple_eval(formula_str, names=context, functions=functions)
            return Decimal(str(result))
        except Exception as e:
            print(f"Erreur évaluation formule '{formula_str}': {e}")
            return Decimal('0')

    @staticmethod
    def _calculate_tranches(base: Decimal, tranches: List[Dict[str, Any]]) -> Decimal:
        """
        Calcule les tranches cumulatives
        Format attendu des tranches: 
        [
            {"max": 3000000, "taux": 2.25}, 
            {"max": 10000000, "taux": 1.5},
            {"max": None, "taux": 0.75}
        ]
        """
        if not tranches:
            return Decimal('0')
            
        total = Decimal('0')
        restant = base
        borne_precedente = Decimal('0')
        
        # Sort just in case it's not ordered
        def tranche_sort_key(t):
            return t.get('max') if t.get('max') is not None else float('inf')
            
        tranches_triees = sorted(tranches, key=tranche_sort_key)
        
        for tranche in tranches_triees:
            tranche_max = tranche.get('max')
            taux = Decimal(str(tranche.get('taux', 0))) / Decimal('100')
            
            plafond = Decimal(str(tranche_max)) if tranche_max is not None else Decimal('Infinity')
            
            if restant <= 0:
                break
                
            # Calculer la part de la base qui tombe dans cette tranche
            taille_tranche = plafond - borne_precedente
            if base > plafond:
                montant_tranche = taille_tranche
            else:
                montant_tranche = base - borne_precedente
                
            if montant_tranche > 0:
                total += montant_tranche * taux
                
            borne_precedente = plafond
            
        return total

    @classmethod
    def calculate(cls, bareme_code: str, user_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exécute le moteur de règles pour un type de barème donné.
        user_inputs doit être un dictionnaire des variables (par ex. {'prix_vente': 15000000, 'morcellement': False})
        """
        modele = BaremeModele.query.filter_by(code=bareme_code).first()
        if not modele:
            raise ValueError(f"Barème {bareme_code} introuvable.")
            
        # 1. Préparation du contexte d'évaluation
        # Normalisation des inputs utilisateur en majuscules pour correspondre aux codes variables
        input_map = {str(k).upper(): v for k, v in user_inputs.items()}
        
        context = {
            'TVA_RATE': float(SharedCalculator.TVA_RATE)  # 0.18
        }
        
        # Injection des saisies utilisateur dans le contexte
        for var in modele.variables:
            code_upper = var.code.upper()
            val = input_map.get(code_upper, var.valeur_defaut)
            
            # Conversion intelligente selon le type de champ
            if var.type_champ in ['MONTANT', 'ENTIER', 'POURCENTAGE', 'CHOIX']:
                try:
                    # On tente la conversion numérique (float) pour tous ces types
                    context[code_upper] = float(val) if val is not None else 0.0
                except (ValueError, TypeError):
                    context[code_upper] = 0.0
            elif var.type_champ == 'BOOLEEN':
                # Gestion souple du booléen (string "True", bool réel, ou "y" du form HTML)
                if isinstance(val, bool):
                    context[code_upper] = val
                else:
                    context[code_upper] = str(val).lower() in ['true', '1', 'y', 'on', 'yes']
            else:
                context[code_upper] = val
                
        # 2. Exécution Ligne par Ligne
        resultats_lignes = []
        somme_ht_tva = Decimal('0')  # Base soumise à TVA (généralement Honoraires)
        total_general = Decimal('0')
        
        lignes = sorted(modele.lignes, key=lambda l: l.ordre)
        
        for ligne in lignes:
            # Vérifier la condition d'affichage/exécution
            if ligne.condition_affichage and not cls._evaluate_condition(ligne.condition_affichage, context):
                continue
                
            montant_ligne = Decimal('0')
            
            # Calculer le montant selon le type de ligne
            if ligne.type_ligne == 'TRANCHES':
                # Base de calcul de la tranche (souvent une simple variable comme 'prix_vente' mais on permet une formule)
                base_calc = cls._evaluate_formula(ligne.formule_ou_montant, context)
                if ligne.tranches_json:
                    montant_ligne = cls._calculate_tranches(base_calc, ligne.tranches_json)
                    
            elif ligne.type_ligne in ['FORFAIT', 'FORMULE']:
                montant_ligne = cls._evaluate_formula(ligne.formule_ou_montant, context)
                
            # Cumul
            total_general += montant_ligne
            if ligne.soumis_tva:
                somme_ht_tva += montant_ligne
                
            # Exposer ce résultat dans le contexte pour l'utiliser dans la ligne d'après (ex: calcul de la TVA)
            # Normaliser le nom de la ligne (ex: "Droits d'Enregistrement" -> "droits_enregistrement")
            nom_variable_ligne = ligne.code.lower()
            context[nom_variable_ligne] = float(montant_ligne)
            
            resultats_lignes.append({
                'code': ligne.code,
                'libelle': ligne.libelle,
                'montant': float(montant_ligne),
                'soumis_tva': ligne.soumis_tva
            })
            
        # 3. Traitement global final (TVA globale, Arrondi)
        montant_tva_global = somme_ht_tva * SharedCalculator.TVA_RATE
        
        # S'il y a déjà une ligne qui calcule spécifiquement la TVA dans le constructeur,
        # on n'a pas besoin de l'ajouter magiquement, le constructeur aura fait (TVA_LIGNE)
        # Mais pour la simplicité, on inclut le calcul TVA sur les lignes marquées `soumis_tva`
        
        # Vérifions si le barème a calculé la TVA explicitement
        a_tva_explicite = any(l.code == 'TVA' for l in lignes)
        if not a_tva_explicite and montant_tva_global > 0:
            resultats_lignes.append({
                'code': 'TVA',
                'libelle': 'TVA (18%)',
                'montant': float(montant_tva_global),
                'soumis_tva': False
            })
            total_general += montant_tva_global
            
        # Arrondir le total final aux 1000FCFA supérieurs (règle OHADA commune)
        total_arrondi = SharedCalculator.roundup_thousand(total_general)
        
        return {
            'inputs': context,
            'lignes': resultats_lignes,
            'total_general': float(total_arrondi)
        }
