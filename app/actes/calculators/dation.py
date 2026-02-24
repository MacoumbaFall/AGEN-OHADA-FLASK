from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class DationCalculator:
    @staticmethod
    def calculate(prix: float = 0, taux_enregistrement: int = 10, morcellement: bool = True, plus_value: bool = False) -> Dict[str, Any]:
        val_prix = Decimal(str(prix))
        
        # 1. Honoraires
        if plus_value:
            brackets = SharedCalculator.get_standard_brackets('0.0225', '0.015', '0.0075', '0.00375')
        else:
            brackets = SharedCalculator.get_standard_brackets('0.045', '0.03', '0.015', '0.0075')
            
        honoraires_ht, details = SharedCalculator.calculate_brackets(val_prix, brackets)
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement
        enregistrement = val_prix * (Decimal(str(taux_enregistrement)) / Decimal('100'))
        
        # 3. Conservation Fonciere
        cf = SharedCalculator.conservation_fonciere(val_prix)
        
        # 4. Morcellement
        frais_morcellement = Decimal('20000') if morcellement else Decimal('0')
        
        # 5. Droits sur Mutation
        mutation = SharedCalculator.mutation_amount(val_prix)
            
        # 6. Debours
        debours = {
            'mutation': mutation,
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values()) + frais_morcellement
        
        subtotal = total_honoraires + enregistrement + cf + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(val_prix),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'conservation_fonciere': float(cf),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'frais_morcellement': float(frais_morcellement),
            'total_debours': float(total_debours),
            'total_general': float(total_general)
        }
