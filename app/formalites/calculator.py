"""
Module de calcul des frais et émoluments selon les barèmes OHADA.
Ce module fournit des fonctions pour calculer les coûts des différentes formalités.
"""

from decimal import Decimal
from typing import Dict, Optional

class FormaliteCalculator:
    """Calculateur de frais pour les formalités notariales OHADA."""
    
    # Barèmes de base (à ajuster selon la législation locale)
    BAREME_ENREGISTREMENT = {
        'taux_base': Decimal('0.05'),  # 5% du montant de l'acte
        'minimum': Decimal('10000'),    # Minimum 10,000 FCFA
        'maximum': Decimal('5000000')   # Maximum 5,000,000 FCFA
    }
    
    BAREME_HYPOTHEQUE = {
        'taux_base': Decimal('0.02'),  # 2% du montant garanti
        'minimum': Decimal('25000'),
        'frais_fixes': Decimal('15000')  # Frais de dossier
    }
    
    BAREME_RCCM = {
        'creation': Decimal('50000'),
        'modification': Decimal('25000'),
        'radiation': Decimal('15000')
    }
    
    BAREME_JOURNAL = {
        'par_ligne': Decimal('5000'),
        'minimum': Decimal('30000')
    }
    
    BAREME_CADASTRE = {
        'immatriculation': Decimal('100000'),
        'morcellement': Decimal('75000'),
        'bornage': Decimal('50000')
    }
    
    @staticmethod
    def calculer_enregistrement(montant_acte: float) -> Dict[str, Decimal]:
        """
        Calcule les frais d'enregistrement aux impôts.
        
        Args:
            montant_acte: Montant de l'acte en FCFA
            
        Returns:
            Dict contenant le détail des frais
        """
        montant = Decimal(str(montant_acte))
        bareme = FormaliteCalculator.BAREME_ENREGISTREMENT
        
        frais = montant * bareme['taux_base']
        
        # Application du minimum et maximum
        if frais < bareme['minimum']:
            frais = bareme['minimum']
        elif frais > bareme['maximum']:
            frais = bareme['maximum']
        
        return {
            'montant_acte': montant,
            'taux_applique': bareme['taux_base'],
            'frais_enregistrement': frais,
            'total': frais
        }
    
    @staticmethod
    def calculer_hypotheque(montant_garanti: float) -> Dict[str, Decimal]:
        """
        Calcule les frais d'inscription hypothécaire.
        
        Args:
            montant_garanti: Montant du crédit garanti en FCFA
            
        Returns:
            Dict contenant le détail des frais
        """
        montant = Decimal(str(montant_garanti))
        bareme = FormaliteCalculator.BAREME_HYPOTHEQUE
        
        frais_proportionnels = montant * bareme['taux_base']
        
        if frais_proportionnels < bareme['minimum']:
            frais_proportionnels = bareme['minimum']
        
        total = frais_proportionnels + bareme['frais_fixes']
        
        return {
            'montant_garanti': montant,
            'frais_proportionnels': frais_proportionnels,
            'frais_fixes': bareme['frais_fixes'],
            'total': total
        }
    
    @staticmethod
    def calculer_rccm(type_operation: str = 'creation') -> Dict[str, Decimal]:
        """
        Calcule les frais de dépôt au RCCM.
        
        Args:
            type_operation: 'creation', 'modification', ou 'radiation'
            
        Returns:
            Dict contenant le détail des frais
        """
        bareme = FormaliteCalculator.BAREME_RCCM
        
        frais = bareme.get(type_operation, bareme['creation'])
        
        return {
            'type_operation': type_operation,
            'frais_rccm': frais,
            'total': frais
        }
    
    @staticmethod
    def calculer_journal(nombre_lignes: int = 10) -> Dict[str, Decimal]:
        """
        Calcule les frais de publication au Journal Officiel.
        
        Args:
            nombre_lignes: Nombre de lignes à publier
            
        Returns:
            Dict contenant le détail des frais
        """
        bareme = FormaliteCalculator.BAREME_JOURNAL
        
        frais = Decimal(nombre_lignes) * bareme['par_ligne']
        
        if frais < bareme['minimum']:
            frais = bareme['minimum']
        
        return {
            'nombre_lignes': nombre_lignes,
            'tarif_ligne': bareme['par_ligne'],
            'frais_publication': frais,
            'total': frais
        }
    
    @staticmethod
    def calculer_cadastre(type_operation: str = 'immatriculation') -> Dict[str, Decimal]:
        """
        Calcule les frais de formalités cadastrales.
        
        Args:
            type_operation: 'immatriculation', 'morcellement', ou 'bornage'
            
        Returns:
            Dict contenant le détail des frais
        """
        bareme = FormaliteCalculator.BAREME_CADASTRE
        
        frais = bareme.get(type_operation, bareme['immatriculation'])
        
        return {
            'type_operation': type_operation,
            'frais_cadastre': frais,
            'total': frais
        }
    
    @staticmethod
    def calculer_formalite(type_formalite: str, **kwargs) -> Dict[str, Decimal]:
        """
        Calcule les frais pour n'importe quel type de formalité.
        
        Args:
            type_formalite: Type de formalité (ENREGISTREMENT, HYPOTHEQUE, etc.)
            **kwargs: Paramètres spécifiques au type de formalité
            
        Returns:
            Dict contenant le détail des frais
        """
        # Normalisation du type pour le matching (gestion des codes et des noms complets)
        t_upper = type_formalite.upper()
        
        calculateurs = {
            'ENREGISTREMENT': FormaliteCalculator.calculer_enregistrement,
            'ENREGISTREMENT IMPÔTS': FormaliteCalculator.calculer_enregistrement,
            'HYPOTHEQUE': FormaliteCalculator.calculer_hypotheque,
            'INSCRIPTION HYPOTHÉCAIRE': FormaliteCalculator.calculer_hypotheque,
            'RCCM': FormaliteCalculator.calculer_rccm,
            'DÉPÔT RCCM': FormaliteCalculator.calculer_rccm,
            'JOURNAL': FormaliteCalculator.calculer_journal,
            'PUBLICATION JOURNAL OFFICIEL': FormaliteCalculator.calculer_journal,
            'CADASTRE': FormaliteCalculator.calculer_cadastre,
            'FORMALITÉS CADASTRALES': FormaliteCalculator.calculer_cadastre
        }
        
        calculateur = calculateurs.get(t_upper)
        
        if calculateur:
            return calculateur(**kwargs)
        else:
            # Pour les types non définis, ou si on a passé le cout_base
            cout_base = kwargs.get('cout_base', Decimal('50000'))
            return {
                'type_formalite': type_formalite,
                'estimation': Decimal(str(cout_base)),
                'total': Decimal(str(cout_base)),
                'note': 'Estimation basée sur le coût de base du type'
            }


def estimer_delai_formalite(type_formalite: str) -> Dict[str, any]:
    """
    Estime le délai moyen pour une formalité.
    
    Args:
        type_formalite: Type de formalité
        
    Returns:
        Dict avec le délai en jours et des informations complémentaires
    """
    t_upper = type_formalite.upper()
    
    delais = {
        'ENREGISTREMENT': {'jours': 3, 'description': 'Délai moyen pour enregistrement aux impôts'},
        'ENREGISTREMENT IMPÔTS': {'jours': 3, 'description': 'Délai moyen pour enregistrement aux impôts'},
        'HYPOTHEQUE': {'jours': 15, 'description': 'Délai moyen pour inscription hypothécaire'},
        'INSCRIPTION HYPOTHÉCAIRE': {'jours': 15, 'description': 'Délai moyen pour inscription hypothécaire'},
        'RCCM': {'jours': 7, 'description': 'Délai moyen pour dépôt au RCCM'},
        'DÉPÔT RCCM': {'jours': 7, 'description': 'Délai moyen pour dépôt au RCCM'},
        'JOURNAL': {'jours': 30, 'description': 'Délai moyen pour publication au Journal Officiel'},
        'PUBLICATION JOURNAL OFFICIEL': {'jours': 30, 'description': 'Délai moyen pour publication au Journal Officiel'},
        'CADASTRE': {'jours': 45, 'description': 'Délai moyen pour formalités cadastrales'},
        'FORMALITÉS CADASTRALES': {'jours': 45, 'description': 'Délai moyen pour formalités cadastrales'},
        'DIVERS': {'jours': 10, 'description': 'Délai estimé pour autres formalités'}
    }
    
    return delais.get(t_upper, delais['DIVERS'])
