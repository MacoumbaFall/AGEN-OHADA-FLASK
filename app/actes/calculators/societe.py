from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class SocieteCalculator:
    # OHADA Standard Brackets for Company Constitution
    OHADA_BRACKETS = [
        (Decimal('20000000'), Decimal('0.02'), "0 à 20 Millions"),
        (Decimal('60000000'), Decimal('0.015'), "20 à 80 Millions"),
        (Decimal('220000000'), Decimal('0.01'), "80 à 300 Millions"),
        (Decimal('300000000'), Decimal('0.005'), "300 à 600 Millions"),
        (Decimal('600000000'), Decimal('0.003'), "600 à 1200 Millions"),
        (Decimal('300000000'), Decimal('0.002'), "1200 a 1500 Millions"),
        (None, Decimal('0.001'), "Plus de 1500 Millions")
    ]

    @staticmethod
    def calculate_base_societe(capital: float, type_societe: str) -> Dict[str, Any]:
        cap = Decimal(str(capital))
        
        # 1. Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(cap, SocieteCalculator.OHADA_BRACKETS, min_first_tranche=Decimal('100000'))
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement (Fixed 25k if <= 100M, else 1%)
        if cap <= Decimal('100000000'):
            enregistrement = Decimal('25000')
        else:
            enregistrement = cap * Decimal('0.01')
            
        # 3. Greffe
        if cap > 0:
            if cap > Decimal('1000000'):
                greffe = Decimal('32000') + (cap // Decimal('1000000')) * Decimal('90')
            else:
                greffe = Decimal('32090')
        else:
            greffe = Decimal('0')
            
        # 4. Debours specific to type
        if type_societe == 'SARL':
            debours = {
                'publicite': SharedCalculator.frais_publicite(),
                'expeditions': SharedCalculator.frais_expeditions(),
                'drc': Decimal('59000'), # Declaration regularite
            }
        elif type_societe == 'SA':
            debours = {
                'publicite': SharedCalculator.frais_publicite(),
                'expeditions': SharedCalculator.frais_expeditions(),
                'divers': SharedCalculator.frais_divers()
            }
        elif type_societe == 'SCI':
            debours = {
                'expeditions': Decimal('60000'),
            }
        else:
            debours = {}
            
        total_debours = sum(debours.values()) + greffe
        
        subtotal = total_honoraires + enregistrement + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(cap),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'greffe': float(greffe),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_debours': float(total_debours),
            'total_general': float(total_general)
        }

class SarlCalculator:
    @staticmethod
    def calculate(capital: float = 0) -> Dict[str, Any]:
        return SocieteCalculator.calculate_base_societe(capital, 'SARL')

class SciCalculator:
    @staticmethod
    def calculate(capital: float = 0) -> Dict[str, Any]:
        return SocieteCalculator.calculate_base_societe(capital, 'SCI')

class SaCalculator:
    @staticmethod
    def calculate(capital: float = 0) -> Dict[str, Any]:
        return SocieteCalculator.calculate_base_societe(capital, 'SA')
