from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class SocieteModifCalculator:
    # Most of these are fixed fees or standard OHADA brackets
    
    @staticmethod
    def calculate_dissolution(capital: float = 0) -> Dict[str, Any]:
        cap = Decimal(str(capital))
        
        # 1. Honoraires (Fixed for Dissolution usually 20k)
        honoraires_ht = Decimal('20000')
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement
        # Minute (5k) + Annexe (often around 20k) + Penalties (15k)
        enregistrement = Decimal('5000') + Decimal('20000') + Decimal('15000')
        
        # 3. Greffe
        if cap > 1000000:
            greffe = Decimal('32000') + (cap // 1000000) * Decimal('90')
        else:
            greffe = Decimal('32090')
        # Standard added for modif
        total_greffe = greffe + Decimal('10000')
            
        # 4. Debours
        debours = {
            'publicite': SharedCalculator.frais_publicite(),
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values()) + total_greffe
        
        subtotal = total_honoraires + enregistrement + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(cap),
            'honoraires_ht': float(honoraires_ht),
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'greffe': float(total_greffe),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }

    @staticmethod
    def calculate_transformation(capital: float = 0) -> Dict[str, Any]:
        cap = Decimal(str(capital))
        
        # 1. Honoraires (Fixed or tiered but dump shows 20k)
        honoraires_ht = Decimal('20000')
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement (Fixed 25k if cap <= 10M, then tiered)
        if cap <= Decimal('10000000'):
            reg_fixe = Decimal('25000')
        else:
            reg_fixe = cap * Decimal('0.01') # Tiered in reality but simplifying based on common cases
            
        enregistrement = reg_fixe + Decimal('5000') + Decimal('20000') + Decimal('5000')
        
        # 3. Greffe
        if cap > 1000000:
            greffe = Decimal('32000') + (cap // 1000000) * Decimal('90')
        else:
            greffe = Decimal('32090')
        total_greffe = greffe + Decimal('10000')
            
        # 4. Debours
        debours = {
            'publicite': SharedCalculator.frais_publicite(),
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values()) + total_greffe
        
        subtotal = total_honoraires + enregistrement + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(cap),
            'honoraires_ht': float(honoraires_ht),
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'greffe': float(total_greffe),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }

class FondsCommerceCalculator:
    BRACKETS = [
        (Decimal('20000000'), Decimal('0.045'), "1 à 20 millions"),
        (Decimal('60000000'), Decimal('0.03'), "20 à 80 millions"),
        (Decimal('220000000'), Decimal('0.015'), "80 à 300 millions"),
        (None, Decimal('0.0075'), "Plus de 300 millions")
    ]

    @staticmethod
    def calculate(prix_cession: float = 0, valeur_fonds: float = 0, marchandises: float = 0) -> Dict[str, Any]:
        prix = Decimal(str(prix_cession))
        val_fonds = Decimal(str(valeur_fonds))
        val_march = Decimal(str(marchandises))
        
        # 1. Honoraires (On total price)
        honoraires_ht, details = SharedCalculator.calculate_brackets(prix, FondsCommerceCalculator.BRACKETS)
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 2. Enregistrement (10% on business assets, 1% on new goods)
        reg_fonds = val_fonds * Decimal('0.1')
        reg_march = val_march * Decimal('0.01')
        enregistrement = reg_fonds + reg_march
        
        # 3. Debours
        debours = {
            'greffe_mod': Decimal('20000'),
            'publicite': SharedCalculator.frais_publicite(),
            'expeditions': SharedCalculator.frais_expeditions(),
            'divers': SharedCalculator.frais_divers()
        }
        total_debours = sum(debours.values())
        
        subtotal = total_honoraires + enregistrement + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(prix),
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'enregistrement': float(enregistrement),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_general': float(total_general)
        }
