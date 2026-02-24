from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class TPVCalculator:
    # Simplified coefficients based on holding years (usually provided by tax authorities)
    # This is a sample implementation as real coefficients vary by decree
    COEFFICIENTS = {
        0: Decimal('1.0'),
        1: Decimal('1.05'),
        2: Decimal('1.10'),
        3: Decimal('1.15'),
        4: Decimal('1.20'),
        5: Decimal('1.25'),
        # ... simplified mapping
    }

    @staticmethod
    def calculate(prix_acquisition: float, annee_acquisition: int, annee_vente: int, prix_vente: float, depenses_travaux: float = 0) -> Dict[str, Any]:
        acq = Decimal(str(prix_acquisition))
        vte = Decimal(str(prix_vente))
        travaux = Decimal(str(depenses_travaux))
        holding_years = max(0, annee_vente - annee_acquisition)
        
        # 1. Valeur d'acquisition revalorisée
        # Excel shows "TAUX FORFAITAIRE 120%" for a specific case.
        # Often it's (Acq + 15% fixed cost) * Coefficient
        valeur_acq_base = acq * Decimal('1.15') # 15% estimated acquisition costs
        
        # Sample coefficient logic
        coef = Decimal('1.0') + (Decimal(str(holding_years)) * Decimal('0.05')) # 5% per year revalorization
        valeur_revalorisee = valeur_acq_base * coef + travaux
        
        # 2. Plus Value
        plus_value = max(Decimal('0'), vte - valeur_revalorisee)
        
        # 3. Taxe (10% usually)
        taxe = plus_value * Decimal('0.10')
        
        return {
            'prix_acquisition': float(acq),
            'annee_acquisition': annee_acquisition,
            'annee_vente': annee_vente,
            'prix_vente': float(vte),
            'depenses_travaux': float(travaux),
            'valeur_acquisition_revalorisee': float(valeur_revalorisee),
            'plus_value': float(plus_value),
            'taxe_tpv': float(taxe)
        }
