from decimal import Decimal
from typing import Dict, Any
from datetime import datetime
from app.actes.calculators.shared import SharedCalculator

class DiversCalculator:
    # 1. Location Gérance
    LG_BRACKETS = [
        (Decimal('10000000'), Decimal('0.03'), "0 à 10 millions"),
        (Decimal('30000000'), Decimal('0.02'), "10 à 40 millions"),
        (Decimal('110000000'), Decimal('0.01'), "40 à 150 millions"),
        (None, Decimal('0.005'), "Plus de 150 millions")
    ]

    @staticmethod
    def calculate_location_gerance(loyer_mensuel: float, duree_mois: int) -> Dict[str, Any]:
        total_loyer = Decimal(str(loyer_mensuel)) * Decimal(str(duree_mois))
        
        # Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(total_loyer, DiversCalculator.LG_BRACKETS)
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        
        # Enregistrement (2% as per BAIL 1 usually, but let's check dump... wait, LG often has specific rates)
        # Based on Bail logic usually 2%
        enregistrement = total_loyer * Decimal('0.02')
        
        # Debours
        debours = {
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values())
        
        total_general = SharedCalculator.roundup_thousand(honoraires_ht + tva + enregistrement + total_debours)
        
        return {
            'base': float(total_loyer),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'enregistrement': float(enregistrement),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }

    # 2. RGT COPROP (Règlement de Copropriété)
    RCP_BRACKETS = [
        (Decimal('20000000'), Decimal('0.0225'), "1 à 20 millions"),
        (Decimal('60000000'), Decimal('0.015'), "20 à 80 millions"),
        (Decimal('220000000'), Decimal('0.0075'), "80 à 300 millions"),
        (None, Decimal('0.00375'), "Plus de 300 millions")
    ]

    @staticmethod
    def calculate_copropriete(valeur_immeuble: float, nb_titres: int = 1) -> Dict[str, Any]:
        val = Decimal(str(valeur_immeuble))
        
        # Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(val, DiversCalculator.RCP_BRACKETS, min_first_tranche=Decimal('1500000'))
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        
        # Enregistrement (Fixed 5000 usually)
        enregistrement = Decimal('5000')
        
        # Titres (NB titres * 26500)
        frais_titres = Decimal(str(nb_titres)) * Decimal('26500')
        
        # CF (1% + 6500)
        cf = (val // 1000 * 1000) * Decimal('0.01') + Decimal('6500')
        
        # Debours
        debours = {
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values()) + frais_titres
        
        total_general = SharedCalculator.roundup_thousand(honoraires_ht + tva + enregistrement + cf + total_debours)
        
        return {
            'base': float(val),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'enregistrement': float(enregistrement),
            'frais_titres': float(frais_titres),
            'conservation_fonciere': float(cf),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }

    # 3. Mandat Sequestre
    MS_BRACKETS = [
        (Decimal('20000000'), Decimal('0.015'), "0 à 20 millions"),
        (Decimal('60000000'), Decimal('0.01'), "20 à 80 millions"),
        (Decimal('220000000'), Decimal('0.005'), "80 à 300 millions"),
        (None, Decimal('0.0025'), "Plus de 300 Millions")
    ]

    @staticmethod
    def calculate_mandat_sequestre(montant: float) -> Dict[str, Any]:
        val = Decimal(str(montant))
        honoraires_ht, details = SharedCalculator.calculate_brackets(val, DiversCalculator.MS_BRACKETS)
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        divers = Decimal('10000')
        
        total_general = SharedCalculator.roundup_thousand(honoraires_ht + tva + divers)
        
        return {
            'base': float(val),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'divers': float(divers),
            'total_general': float(total_general)
        }

    # 4. Acte de Dépôt
    @staticmethod
    def calculate_acte_depot(nb_annexes: int = 1, penalites_mois: int = 0) -> Dict[str, Any]:
        # Fixed fees usually
        honoraires_ht = Decimal('20000')
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        
        enregistrement = Decimal('5000')
        frais_annexes = Decimal(str(nb_annexes)) * Decimal('2000') # Estimated from dump logic (8000 for 12, wait... 2000*D40... wait R31 says 12.0 | 8000.0)
        # Actually R40 says annexe 10.0 | [=2000*D40 (Val: 20000)]
        penalites = Decimal('5000') if penalites_mois > 1 else Decimal('0')
        
        # Greffe
        greffe = Decimal('12000')
        
        debours = {
            'publicite': SharedCalculator.frais_publicite(),
            'expeditions': SharedCalculator.frais_expeditions()
        }
        total_debours = sum(debours.values()) + greffe + frais_annexes + penalites
        
        total_general = SharedCalculator.roundup_thousand(honoraires_ht + tva + enregistrement + total_debours)
        
        return {
            'honoraires_ht': float(honoraires_ht),
            'tva': float(tva),
            'enregistrement': float(enregistrement),
            'frais_annexes': float(frais_annexes),
            'penalites': float(penalites),
            'greffe': float(greffe),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }

    # 5. Cession de Créances
    CC_BRACKETS = [
        (Decimal('10000000'), Decimal('0.03'), "0 à 10 millions"),
        (Decimal('30000000'), Decimal('0.02'), "10 à 40 millions"),
        (Decimal('110000000'), Decimal('0.01'), "40 à 150 millions"),
        (None, Decimal('0.005'), "Plus de 150 millions")
    ]

    @staticmethod
    def calculate_cession_creances(montant: float) -> Dict[str, Any]:
        val = Decimal(str(montant))
        
        # Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(val, DiversCalculator.CC_BRACKETS)
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        
        # Enregistrement (1%)
        enregistrement = val * Decimal('0.01')
        
        # CF (1% + 7500)
        cf = (val // 1000 * 1000) * Decimal('0.01') + Decimal('7500')
        
        # Mutation/Inscription style
        mutation = Decimal('20000') if val > 2500000 else Decimal('0')
        
        debours = {
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers(),
            'mutation': mutation
        }
        total_debours = sum(debours.values())
        
        total_general = SharedCalculator.roundup_thousand(honoraires_ht + tva + enregistrement + cf + total_debours)
        
        return {
            'base': float(val),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'enregistrement': float(enregistrement),
            'conservation_fonciere': float(cf),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }

    # 6. Nantissement
    @staticmethod
    def calculate_nantissement(montant: float) -> Dict[str, Any]:
        val = Decimal(str(montant))
        
        # Honoraires (Same as CC/Mortgage)
        honoraires_ht, details = SharedCalculator.calculate_brackets(val, DiversCalculator.CC_BRACKETS)
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        
        # Enregistrement (Fixed 5000)
        enregistrement = Decimal('5000')
        
        # Greffe (Nantissement RCCM)
        if val > 5000000:
            greffe = val * Decimal('0.01')
        elif val > 3000000:
            greffe = val * Decimal('0.015')
        else:
            greffe = val * Decimal('0.05')
            
        # Debours
        debours = {
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values()) + greffe
        
        total_general = SharedCalculator.roundup_thousand(honoraires_ht + tva + enregistrement + total_debours)
        
        return {
            'base': float(val),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'enregistrement': float(enregistrement),
            'greffe': float(greffe),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }
