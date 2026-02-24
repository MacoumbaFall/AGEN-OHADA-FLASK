from typing import Dict, Any, Type
from flask import request

# Import all calculators
from .societe import SarlCalculator, SciCalculator, SaCalculator
from .vente import VenteCalculator
from .bail import BailCalculator
from .cession_parts import CessionPartsCalculator
from .donation_partage import DonationCalculator, PartageCalculator
from .vente_divers import AdjudicationCalculator, AugmentationCapitalCalculator
from .garanties import MainleveeCalculator, MortgageCalculator
from .echange import EchangeCalculator
from .societe_divers import SocieteModifCalculator, FondsCommerceCalculator
from .dation import DationCalculator
from .divers import DiversCalculator
from .tpv import TPVCalculator
from .ao import AOCalculator
from .succession import SuccessionCalculator

def extract_float(key, default=0):
    val = request.form.get(key, default)
    try:
        return float(val) if val else default
    except ValueError:
        return default

def extract_int(key, default=0):
    val = request.form.get(key, default)
    try:
        return int(val) if val else default
    except ValueError:
        return default

def extract_bool(key):
    return request.form.get(key) == 'on'

# Configuration Registry
# Key: slug (used in URL)
# Value: Dict with configuration
CALCULATOR_REGISTRY = {
    'vente': {
        'class': VenteCalculator,
        'template': 'actes/bareme_vente.html',
        'type_acte': 'VENTE',
        'params_extractor': lambda: {
            'prix': extract_float('prix'),
            'taux_enregistrement': extract_float('taux_enregistrement', 10),
            'morcellement': extract_bool('morcellement')
        }
    },
    'sarl': {
        'class': SarlCalculator,
        'template': 'actes/bareme_sarl.html',
        'type_acte': 'SARL',
        'params_extractor': lambda: {
            'capital': extract_float('capital')
        }
    },
    'sci': {
        'class': SciCalculator,
        'template': 'actes/bareme_sci.html',
        'type_acte': 'SCI',
        'params_extractor': lambda: {
            'capital': extract_float('capital')
        }
    },
    'sa': {
        'class': SaCalculator,
        'template': 'actes/bareme_sa.html',
        'type_acte': 'SA',
        'params_extractor': lambda: {
            'capital': extract_float('capital')
        }
    },
    'bail': {
        'class': BailCalculator,
        'template': 'actes/bareme_bail.html',
        'type_acte': 'BAIL',
        'params_extractor': lambda: {
            'loyer_mensuel': extract_float('loyer_mensuel'),
            'duree_mois': extract_int('duree_mois', 12)
        }
    },
    'cession_parts': {
        'class': CessionPartsCalculator,
        'template': 'actes/bareme_cession_parts.html',
        'type_acte': 'CESSION_PARTS',
        'params_extractor': lambda: {
            'prix': extract_float('prix')
        }
    },
    'succession': {
        'class': SuccessionCalculator,
        'template': 'actes/bareme_succession.html',
        'type_acte': 'SUCCESSION',
        'params_extractor': lambda: {
            'valeur_immeuble': extract_float('valeur_immeuble'),
            'reste_actif': extract_float('reste_actif'),
            'passif': extract_float('passif'),
            'mois_penalite': extract_int('mois_penalite'),
            'inclure_conservation': extract_bool('inclure_conservation'),
            'lieu_deces': extract_int('lieu_deces', 1),
            'parente': extract_int('parente', 1)
        }
    },
     'donation': {
        'class': DonationCalculator,
        'template': 'actes/bareme_donation.html',
        'type_acte': 'DONATION',
        'params_extractor': lambda: {
            'valeur': extract_float('valeur'),
            'parente': extract_int('parente', 1)
        }
    },
    'partage': {
        'class': PartageCalculator,
        'template': 'actes/bareme_partage.html',
        'type_acte': 'PARTAGE',
        'params_extractor': lambda: {
            'actif_brut': extract_float('actif_brut'),
            'passif': extract_float('passif'),
            'soulte': extract_float('soulte'),
            'avec_morcellement': extract_bool('avec_morcellement'),
            'nb_parcelles': extract_int('nb_parcelles', 1),
            'cout_par_parcelle': extract_float('cout_par_parcelle', 20000),
            'avec_cf': extract_bool('avec_cf'),
            'valeur_immeuble_cf': extract_float('valeur_immeuble_cf'),
            'cout_expeditions': extract_float('cout_expeditions', 80000), # Default 80k if empty
            'cout_divers': extract_float('cout_divers')
        }
    },
    'adjudication': {
        'class': AdjudicationCalculator,
        'template': 'actes/bareme_adjudication.html',
        'type_acte': 'ADJUDICATION',
        'params_extractor': lambda: {
            'prix': extract_float('prix'),
            'morcellement': extract_bool('morcellement')
        }
    },
    'augmentation': {
        'class': AugmentationCapitalCalculator,
        'template': 'actes/bareme_augmentation.html',
        'type_acte': 'AUGMENTATION_CAPITAL',
        'params_extractor': lambda: {
            'ancien_capital': extract_float('ancien_capital'),
            'nouveau_capital': extract_float('nouveau_capital')
        }
    },
    'mainlevee': {
        'class': MainleveeCalculator,
        'template': 'actes/bareme_mainlevee.html',
        'type_acte': 'MAINLEVEE',
        'params_extractor': lambda: {
            'montant': extract_float('montant')
        }
    },
    'mortgage': {
        'class': MortgageCalculator,
        'template': 'actes/bareme_mortgage.html',
        'type_acte': 'HYPOTHEQUE',
        'params_extractor': lambda: {
            'montant': extract_float('montant')
        }
    },
    'echange': {
        'class': EchangeCalculator,
        'template': 'actes/bareme_echange.html',
        'type_acte': 'ECHANGE',
        'params_extractor': lambda: {
            'valeur_base': extract_float('valeur_base'),
            'soulte': extract_float('soulte')
        }
    },
    # Special Handler for Dissolution/Transformation which are methods on same class
    'dissolution': {
        'class': None, # Special handling
        'calculator_func': SocieteModifCalculator.calculate_dissolution,
        'template': 'actes/bareme_dissolution.html',
        'type_acte': 'DISSOLUTION',
        'params_extractor': lambda: { 'capital': extract_float('capital') }
    },
     'transformation': {
        'class': None,
        'calculator_func': SocieteModifCalculator.calculate_transformation,
        'template': 'actes/bareme_transformation.html',
        'type_acte': 'TRANSFORMATION',
        'params_extractor': lambda: { 'capital': extract_float('capital') }
    },
    'fonds_commerce': {
        'class': FondsCommerceCalculator,
        'template': 'actes/bareme_fonds_commerce.html',
        'type_acte': 'FONDS_COMMERCE',
        'params_extractor': lambda: {
            'prix_cession': extract_float('prix_cession'),
            'valeur_fonds': extract_float('valeur_fonds'),
            'marchandises': extract_float('marchandises')
        }
    },
    'dation': {
        'class': DationCalculator,
        'template': 'actes/bareme_dation.html',
        'type_acte': 'DATION_PAIEMENT',
        'params_extractor': lambda: {
            'prix': extract_float('prix'),
            'taux_enregistrement': extract_int('taux_enregistrement', 10),
            'morcellement': extract_bool('morcellement')
        }
    },
    # Divers methods
    'location_gerance': {
        'class': None,
        'calculator_func': DiversCalculator.calculate_location_gerance,
        'template': 'actes/bareme_location_gerance.html',
        'type_acte': 'LOCATION_GERANCE',
        'params_extractor': lambda: {
            'loyer_mensuel': extract_float('loyer_mensuel'),
            'duree_mois': extract_int('duree_mois', 1)
        }
    },
    'copropriete': {
        'class': None,
        'calculator_func': DiversCalculator.calculate_copropriete,
        'template': 'actes/bareme_copropriete.html',
        'type_acte': 'COPROPRIETE',
        'params_extractor': lambda: {
            'valeur_immeuble': extract_float('valeur_immeuble'),
            'nb_titres': extract_int('nb_titres', 1)
        }
    },
    'mandat_sequestre': {
        'class': None,
        'calculator_func': DiversCalculator.calculate_mandat_sequestre,
        'template': 'actes/bareme_mandat_sequestre.html',
        'type_acte': 'MANDAT_SEQUESTRE',
        'params_extractor': lambda: {
             'montant': extract_float('montant')
        }
    },
    'acte_depot': {
        'class': None,
        'calculator_func': DiversCalculator.calculate_acte_depot,
        'template': 'actes/bareme_acte_depot.html',
        'type_acte': 'ACTE_DEPOT',
        'params_extractor': lambda: {
            'nb_annexes': extract_int('nb_annexes', 1),
            'penalites_mois': extract_int('penalites_mois')
        }
    },
    'cession_creances': {
        'class': None,
        'calculator_func': DiversCalculator.calculate_cession_creances,
        'template': 'actes/bareme_cession_creances.html',
        'type_acte': 'CESSION_CREANCES',
        'params_extractor': lambda: {
             'montant': extract_float('montant')
        }
    },
    'nantissement': {
        'class': None,
        'calculator_func': DiversCalculator.calculate_nantissement,
        'template': 'actes/bareme_nantissement.html',
        'type_acte': 'NANTISSEMENT',
        'params_extractor': lambda: {
             'montant': extract_float('montant')
        }
    },
    'tpv': {
        'class': TPVCalculator,
        'template': 'actes/bareme_tpv.html',
        'type_acte': 'TPV',
        'params_extractor': lambda: {
            'prix_acquisition': extract_float('prix_acquisition'),
            'annee_acquisition': extract_int('annee_acquisition'),
            'annee_vente': extract_int('annee_vente'),
            'prix_vente': extract_float('prix_vente'),
            'depenses_travaux': extract_float('depenses_travaux')
        }
    },
    'ao': {
        'class': AOCalculator,
        'template': 'actes/bareme_ao.html',
        'type_acte': 'AUTORISATION D\'OCCUPER',
        'params_extractor': lambda: {
            'valeur': extract_float('valeur'),
            'taux_enregistrement': extract_float('taux_enregistrement', 10.0),
            'include_cf': extract_bool('include_cf')
        }
    }
}
