from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class MainleveeCalculator:
    # Brackets for Mainlevée (often half of standard)


    @staticmethod
    def calculate(montant: float = 0) -> Dict[str, Any]:
        val = Decimal(str(montant))
        
        # 1. Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(
            val, 
            SharedCalculator.get_standard_brackets('0.0075', '0.005', '0.0025', '0.00125')
        )
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement (Fixed 5k as per common practice for discharge)
        enregistrement = Decimal('5000')
        
        # 3. Conservation Foncière (1% of amount + 7000 fixed)
        cf = (val // 1000 * 1000) * Decimal('0.01') + Decimal('7000')
        
        # 4. Debours
        debours = {
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values())
        
        subtotal = total_honoraires + enregistrement + cf + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(val),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'conservation_fonciere': float(cf),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }

class MortgageCalculator:
    # Brackets for Mortgage/Obligation Caution (Standard 3, 2, 1, 0.5)
    BRACKETS = [
        (Decimal('10000000'), Decimal('0.03'), "0 à 10 millions"),
        (Decimal('30000000'), Decimal('0.02'), "10 à 40 millions"),
        (Decimal('110000000'), Decimal('0.01'), "40 à 150 millions"),
        (None, Decimal('0.005'), "Plus de 150 millions")
    ]

    @staticmethod
    def calculate(montant: float = 0) -> Dict[str, Any]:
        val = Decimal(str(montant))
        
        # 1. Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(val, MortgageCalculator.BRACKETS)
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement (Fixed 5k for loan/mortgage usually)
        enregistrement = Decimal('5000')
        
        # 3. Conservation Foncière (Inscription) (1% + 7500)
        cf = (val // 1000 * 1000) * Decimal('0.01') + Decimal('7500')
        
        # 4. Droits sur Inscription (Mutation style)
        if val > Decimal('2500000'):
            inscription = Decimal('20000')
        elif val > Decimal('1500000'):
            inscription = Decimal('10000')
        else:
            inscription = Decimal('0')
            
        # 5. Debours
        debours = {
            'inscription': inscription,
            'expeditions': SharedCalculator.frais_expeditions(),
            'frais_generaux': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values())
        
        subtotal = total_honoraires + enregistrement + cf + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(val),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'conservation_fonciere': float(cf),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }
