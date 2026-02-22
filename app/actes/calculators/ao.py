from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class AOCalculator:
    """Calculator for Autorisation d'occuper (Permis d'occuper)."""
    

    @staticmethod
    def calculate(valeur: float, taux_enregistrement: float = 10.0, include_cf: bool = False) -> Dict[str, Any]:
        val = Decimal(str(valeur))
        
        # 1. Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(
            val, 
            SharedCalculator.get_standard_brackets('0.045', '0.03', '0.015', '0.0075')
        )
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        
        # 2. Enregistrement
        enregistrement = val * (Decimal(str(taux_enregistrement)) / Decimal('100'))
        
        # 3. Conservation Foncière (Optional, 1% + 6500)
        cf = Decimal('0')
        if include_cf:
            cf = (val // 1000 * 1000) * Decimal('0.01') + Decimal('6500')
            
        # 4. Debours
        debours = {
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values())
        
        total_general = SharedCalculator.roundup_thousand(honoraires_ht + tva + enregistrement + cf + total_debours)
        
        return {
            'base': float(val),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(honoraires_ht + tva),
            'enregistrement': float(enregistrement),
            'conservation_fonciere': float(cf),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }
