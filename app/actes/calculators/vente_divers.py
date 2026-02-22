from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class AdjudicationCalculator:
    # High brackets for Adjudication
    

    @staticmethod
    def calculate(prix: float = 0, morcellement: bool = True) -> Dict[str, Any]:
        val_prix = Decimal(str(prix))
        
        # 1. Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(
            val_prix, 
            SharedCalculator.get_standard_brackets('0.09', '0.03', '0.015', '0.0075')
        )
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement (10%)
        enregistrement = val_prix * Decimal('0.10')
        
        # 3. Conservation Fonciere
        cf = SharedCalculator.conservation_fonciere(val_prix)
        
        # 4. Morcellement
        frais_morcellement = SharedCalculator.frais_morcellement() if morcellement else Decimal('0')
        
        # 5. Droits sur Mutation
        mutation = SharedCalculator.mutation_amount(val_prix)
            
        # 6. Debours
        debours = {
            'mutation': mutation,
            'expeditions': SharedCalculator.frais_expeditions(),
            'huissier_pub': Decimal('150000')
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

class AugmentationCapitalCalculator:
    # OHADA Standard Brackets
    BRACKETS = [
        (Decimal('20000000'), Decimal('0.02'), "0 à 20 Millions"),
        (Decimal('60000000'), Decimal('0.015'), "20 à 80 Millions"),
        (Decimal('220000000'), Decimal('0.01'), "80 à 300 Millions"),
        (Decimal('300000000'), Decimal('0.005'), "300 à 600 Millions"),
        (Decimal('600000000'), Decimal('0.003'), "600 à 1200 Millions"),
        (Decimal('300000000'), Decimal('0.002'), "1200 a 1500 Millions"),
        (None, Decimal('0.001'), "Plus de 1500 Millions")
    ]

    @staticmethod
    def calculate(ancien_capital: float = 0, nouveau_capital: float = 0) -> Dict[str, Any]:
        ancien = Decimal(str(ancien_capital))
        nouveau = Decimal(str(nouveau_capital))
        augmentation = nouveau - ancien
        if augmentation < 0:
            augmentation = Decimal('0')
            
        # 1. Honoraires
        honoraires_ht, details = SharedCalculator.calculate_brackets(augmentation, AugmentationCapitalCalculator.BRACKETS, min_first_tranche=Decimal('100000'))
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement
        if augmentation <= Decimal('100000000'):
            enregistrement = Decimal('25000')
        else:
            enregistrement = augmentation * Decimal('0.01')
            
        # 3. Greffe
        if augmentation > 0:
            if augmentation > Decimal('1000000'):
                greffe = Decimal('32000') + (augmentation // Decimal('1000000')) * Decimal('90')
            else:
                greffe = Decimal('32090')
        else:
            greffe = Decimal('0')
            
        # 4. Debours
        debours = {
            'publicite': SharedCalculator.frais_publicite(),
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values()) + greffe
        
        subtotal = total_honoraires + enregistrement + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'augmentation': float(augmentation),
            'ancien_capital': float(ancien),
            'nouveau_capital': float(nouveau),
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
