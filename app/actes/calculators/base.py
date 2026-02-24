"""
Base abstraite commune à tous les calculateurs de barème OHADA.

Les paramètres fiscaux (TVA, Conservation Foncière, droits de mutation, débours)
sont lus depuis ParametreService qui les charge depuis la base de données.
Un fallback sur les valeurs par défaut (DEFAULTS) garantit le fonctionnement
même avant initialisation de la DB.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, Any


class BaseCalculator(ABC):
    """
    Contrat commun pour tous les calculateurs de barème notarial OHADA.

    Accès aux paramètres configurables via des méthodes de classe :
        BaseCalculator.tva_rate()          → Decimal('0.18')
        BaseCalculator.cf_taux()           → Decimal('0.01')
        BaseCalculator.mutation_amount(v)  → montant droits de mutation selon valeur

    Tous ces paramètres sont modifiables via l'interface admin sans redéploiement.
    La constante TVA_RATE est conservée pour la rétrocompatibilité avec SharedCalculator.
    """

    # ------------------------------------------------------------------ #
    #  Accès au service de paramètres                                     #
    # ------------------------------------------------------------------ #

    @classmethod
    def _p(cls):
        """Accès lazy au ParametreService (évite les imports circulaires)."""
        from app.actes.services.parametres import ParametreService
        return ParametreService

    # ------------------------------------------------------------------ #
    #  Taux et paramètres fiscaux — appelés comme méthodes                #
    # ------------------------------------------------------------------ #

    @classmethod
    def tva_rate(cls) -> Decimal:
        """Taux TVA (ex: Decimal('0.18') pour 18%)."""
        return cls._p().get_decimal('taux_tva', Decimal('0.18'))

    # Alias statique pour rétrocompatibilité avec SharedCalculator.TVA_RATE
    TVA_RATE: Decimal = Decimal('0.18')  # Valeur par défaut — surchargée à l'exécution

    @classmethod
    def cf_taux(cls) -> Decimal:
        """Taux proportionnel de Conservation Foncière (ex: Decimal('0.01'))."""
        return cls._p().get_decimal('taux_cf_proportionnel', Decimal('0.01'))

    @classmethod
    def cf_fixe(cls) -> Decimal:
        """Frais fixes de Conservation Foncière standard (ex: Decimal('6500'))."""
        return cls._p().get_decimal('frais_cf_fixe_standard', Decimal('6500'))

    @classmethod
    def cf_fixe_double(cls) -> Decimal:
        """Frais fixes CF pour acte d'échange (2 titres) (ex: Decimal('14000'))."""
        return cls._p().get_decimal('frais_cf_fixe_double', Decimal('14000'))

    @classmethod
    def frais_expeditions(cls) -> Decimal:
        return cls._p().get_decimal('frais_expeditions_base', Decimal('50000'))

    @classmethod
    def frais_publicite(cls) -> Decimal:
        return cls._p().get_decimal('frais_publicite_base', Decimal('55000'))

    @classmethod
    def frais_divers(cls) -> Decimal:
        return cls._p().get_decimal('frais_divers_base', Decimal('50000'))

    @classmethod
    def frais_morcellement(cls) -> Decimal:
        return cls._p().get_decimal('frais_morcellement', Decimal('22500'))
        
    @classmethod
    def seuil_bareme(cls, tranche: int) -> Decimal:
        """Retourne dynamiquement les montants des tranches (0->20M, ->60M, ->220M...)"""
        if tranche == 1:
            return cls._p().get_decimal('seuil_bareme_tranche1', Decimal('20000000'))
        elif tranche == 2:
            return cls._p().get_decimal('seuil_bareme_tranche2', Decimal('60000000'))
        elif tranche == 3:
            return cls._p().get_decimal('seuil_bareme_tranche3', Decimal('220000000'))
        return None

    # ------------------------------------------------------------------ #
    #  Méthodes utilitaires de calcul partagées                          #
    # ------------------------------------------------------------------ #

    @classmethod
    def apply_tva(cls, amount_ht: Decimal) -> Decimal:
        """Calcule la TVA à appliquer sur un montant HT."""
        return amount_ht * cls.tva_rate()

    @staticmethod
    def roundup_thousand(amount: Decimal) -> Decimal:
        """Arrondit un montant au millier supérieur (FCFA)."""
        return (amount / 1000).quantize(Decimal('1'), rounding='ROUND_UP') * 1000

    @classmethod
    def mutation_amount(cls, valeur: Decimal) -> Decimal:
        """
        Calcule les droits de mutation selon la valeur du bien.
        Les seuils et montants sont configurables via l'interface admin.
        """
        p = cls._p()
        seuil_haut  = p.get_decimal('seuil_mutation_haut',  Decimal('2500000'))
        seuil_moyen = p.get_decimal('seuil_mutation_moyen', Decimal('1500000'))
        frais_haut  = p.get_decimal('frais_mutation_haut',  Decimal('20000'))
        frais_moyen = p.get_decimal('frais_mutation_moyen', Decimal('10000'))
        frais_bas   = p.get_decimal('frais_mutation_bas',   Decimal('5000'))

        if valeur > seuil_haut:
            return frais_haut
        elif valeur > seuil_moyen:
            return frais_moyen
        return frais_bas

    @classmethod
    def conservation_fonciere(cls, valeur: Decimal, double: bool = False) -> Decimal:
        """
        Calcule la taxe de Conservation Foncière.
        Args:
            valeur: montant de base (arrondi au millier inférieur automatiquement)
            double: True pour les actes d'échange (2 titres → frais fixes doublés)
        """
        cf_fixe = cls.cf_fixe_double() if double else cls.cf_fixe()
        return (valeur // 1000 * 1000) * cls.cf_taux() + cf_fixe

    # ------------------------------------------------------------------ #
    #  Contrat obligatoire                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    @abstractmethod
    def calculate(**params) -> Dict[str, Any]:
        """
        Effectue le calcul du barème et retourne un dictionnaire de résultats.

        Le dict retourné DOIT contenir au minimum :
            - ``total_general`` (float) : total arrondi au millier FCFA
        """
        ...
