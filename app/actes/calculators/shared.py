from decimal import Decimal
from typing import Dict, Any, List, Tuple

from app.actes.calculators.base import BaseCalculator


class _TVARateDescriptor:
    """Descripteur qui résout TVA_RATE depuis ParametreService à l'exécution."""
    def __get__(self, obj, objtype=None) -> Decimal:
        try:
            from app.actes.services.parametres import ParametreService
            return ParametreService.get_decimal('taux_tva', Decimal('0.18'))
        except Exception:
            return Decimal('0.18')


class SharedCalculator(BaseCalculator):
    """
    Utilitaires partagés par tous les calculateurs de barème.

    Hérite de BaseCalculator :
      - tva_rate()          → taux TVA lu depuis la DB (ex. 0.18)
      - apply_tva(ht)       → ht * tva_rate()
      - roundup_thousand()  → arrondi au millier supérieur FCFA
      - mutation_amount()   → droits de mutation configurés
      - conservation_fonciere() → taxe CF configurée

    TVA_RATE est également accessible comme attribut (descripteur dynamique)
    pour la rétrocompatibilité avec le code existant :
        tva = honoraires_ht * SharedCalculator.TVA_RATE
    """
    # Descripteur dynamique : résout le taux depuis la DB à chaque accès
    TVA_RATE = _TVARateDescriptor()

    @classmethod
    def get_standard_brackets(cls, rate1: str, rate2: str, rate3: str, rate4: str) -> List[Tuple[Any, Decimal, str]]:
        """
        Génère un barème standard à 4 tranches en utilisant les seuils configurables 
        (typiquement: 20M, 60M, 220M, reste).
        """
        s1 = cls.seuil_bareme(1)
        s2 = cls.seuil_bareme(2)
        s3 = cls.seuil_bareme(3)
        
        m1 = int(s1 / Decimal('1000000'))
        m2 = int((s1 + s2) / Decimal('1000000'))
        m3 = int((s1 + s2 + s3) / Decimal('1000000'))
        
        return [
            (s1, Decimal(rate1), f"0 à {m1} Millions"),
            (s2, Decimal(rate2), f"{m1} à {m2} Millions"),
            (s3, Decimal(rate3), f"{m2} à {m3} Millions"),
            (None, Decimal(rate4), f"Plus de {m3} Millions")
        ]

    @staticmethod
    def calculate_brackets(
        amount: Decimal,
        brackets: List[Tuple[Any, Decimal, str]],
        min_first_tranche: Decimal = Decimal('0')
    ) -> Tuple[Decimal, List[Dict]]:
        """
        Calcule les honoraires selon un barème à tranches.

        Args:
            amount: Montant de base.
            brackets: Liste de tuples (limite, taux, libellé).
                      Si limite est None → tranche sans plafond.
            min_first_tranche: Honoraires minimaux sur la première tranche.

        Returns:
            (total, details) : total Decimal, détails par tranche.
        """
        remaining = amount
        total = Decimal('0')
        details = []

        for limit, rate, label in brackets:
            if remaining <= 0:
                break

            tranche_base = remaining if limit is None else min(remaining, limit)
            amt = tranche_base * rate

            # Appliquer le minimum uniquement sur la première tranche
            if label == brackets[0][2] and amt < min_first_tranche:
                amt = min_first_tranche

            total += amt
            details.append({
                'tranche': label,
                'taux': f"{float(rate) * 100}%",
                'base': float(tranche_base),
                'montant': float(amt)
            })

            if limit is not None:
                remaining -= tranche_base
            else:
                remaining = Decimal('0')

        return total, details

    # ------------------------------------------------------------------
    # Implémentation requise par BaseCalculator (non utilisée directement
    # ici — SharedCalculator est une classe utilitaire, pas un calculateur
    # concret, mais ABC l'exige)
    # ------------------------------------------------------------------
    @staticmethod
    def calculate(**params) -> Dict[str, Any]:  # type: ignore[override]
        raise NotImplementedError(
            "SharedCalculator est une classe utilitaire. "
            "Utilisez un calculateur concret (VenteCalculator, BailCalculator, ...)."
        )
