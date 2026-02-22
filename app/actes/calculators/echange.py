from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class EchangeCalculator:
    # Standard Property Brackets

    @staticmethod
    def calculate(valeur_base: float = 0, soulte: float = 0) -> Dict[str, Any]:
        val = Decimal(str(valeur_base))
        val_soulte = Decimal(str(soulte))
        
        # 1. Honoraires (Sur la plus haute valeur)
        honoraires_ht, details = SharedCalculator.calculate_brackets(
            val, 
            SharedCalculator.get_standard_brackets('0.045', '0.03', '0.015', '0.0075')
        )
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement (5% on value + 15% on soulte)
        reg_valeur = val * Decimal('0.05')
        reg_soulte = val_soulte * Decimal('0.15')
        enregistrement = reg_valeur + reg_soulte
        
        # CF double pour échange
        cf = SharedCalculator.conservation_fonciere(val, double=True)
        
        # 4. Debours
        debours = {
            'mutation': Decimal('20000'),
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values())
        
        subtotal = total_honoraires + enregistrement + cf + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(val),
            'soulte': float(val_soulte),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'conservation_fonciere': float(cf),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }
