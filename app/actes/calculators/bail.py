from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class BailCalculator:


    @staticmethod
    def calculate(loyer_mensuel: float = 0, duree_mois: int = 12) -> Dict[str, Any]:
        loyer = Decimal(str(loyer_mensuel))
        duree = Decimal(str(duree_mois))
        base = loyer * duree
        
        # 1. Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(
            base, 
            SharedCalculator.get_standard_brackets('0.045', '0.03', '0.015', '0.0075')
        )
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement (5%)
        enregistrement = base * Decimal('0.05')
        
        # 3. Debours
        debours = {
            'publicite': SharedCalculator.frais_publicite(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values())
        
        subtotal = total_honoraires + enregistrement + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(base),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_debours': float(total_debours),
            'total_general': float(total_general)
        }
