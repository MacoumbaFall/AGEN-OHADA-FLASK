from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class VenteCalculator:


    @staticmethod
    def calculate(prix: float = 0, taux_enregistrement: float = 10, morcellement: bool = True) -> Dict[str, Any]:
        val_prix = Decimal(str(prix))
        
        # 1. Honoraires
        if taux_enregistrement == 1:
            brackets = SharedCalculator.get_standard_brackets('0.0225', '0.015', '0.0075', '0.00375')
        else:
            brackets = SharedCalculator.get_standard_brackets('0.045', '0.03', '0.015', '0.0075')
            
        honoraires_ht, details = SharedCalculator.calculate_brackets(val_prix, brackets)
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement
        enregistrement = val_prix * (Decimal(str(taux_enregistrement)) / Decimal('100'))
        
        # 3. Conservation Fonciere
        # Rounded down price to thousand * 1%
        cf_proportionnelle = (val_prix // 1000 * 1000) * SharedCalculator.cf_taux()
        cf_fixe = Decimal('0') if morcellement else SharedCalculator.cf_fixe()
        total_cf = cf_proportionnelle + cf_fixe
        
        # 4. Morcellement
        frais_morcellement = SharedCalculator.frais_morcellement() if morcellement else Decimal('0')
        
        # 5. Droits sur Mutation (Bracketed)
        droit_mutation = SharedCalculator.mutation_amount(val_prix)
            
        # 6. Debours
        debours = {
            'mutation': droit_mutation,
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values()) + frais_morcellement
        
        subtotal = total_honoraires + enregistrement + total_cf + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(val_prix),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'conservation_fonciere': float(total_cf),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'frais_morcellement': float(frais_morcellement),
            'total_debours': float(total_debours),
            'total_general': float(total_general)
        }
