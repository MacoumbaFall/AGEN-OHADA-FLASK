from decimal import Decimal
from datetime import datetime
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class SuccessionCalculator:
    """
    Service de calcul pour la provision sur frais et honoraires d'une SUCCESSION.
    Basé sur le barème extrait du fichier Excel.
    """

    @staticmethod
    def calculate(
        valeur_immeuble: float = 0,
        reste_actif: float = 0,
        passif: float = 0,
        mois_penalite: int = 0,
        inclure_conservation: bool = True,
        lieu_deces: int = 1,  # 1: Sénégal, 2: Étranger
        parente: int = 1      # 1: Epoux/Directe, 2: Autres
    ) -> Dict[str, Any]:
        
        # Inputs Conversion
        val_immeuble = Decimal(str(valeur_immeuble))
        val_reste_actif = Decimal(str(reste_actif))
        val_passif = Decimal(str(passif))
        
        # 1. Base Honoraires (H23 + H24 in Excel)
        # Note: Excel formulas for honoraires use Imm + Actif without subtracting passif
        base_honoraires = val_immeuble + val_reste_actif
        
        # 2. Émoluments (Honoraires HT) - Tranches dégressives
        honoraires_ht = Decimal(0)
        remaining = base_honoraires
        honoraires_details = []
        
        # Tranche 1: 0 à 10M (1.5%)
        t1 = min(remaining, Decimal('10000000'))
        if t1 > 0:
            amt1 = t1 * Decimal('0.015')
            honoraires_ht += amt1
            honoraires_details.append({'tranche': '0 à 10M', 'taux': '1.5%', 'base': float(t1), 'montant': float(amt1)})
            remaining -= t1
        
        # Tranche 2: 10M à 40M (1.0%)
        if remaining > 0:
            t2 = min(remaining, Decimal('30000000'))
            amt2 = t2 * Decimal('0.01')
            honoraires_ht += amt2
            honoraires_details.append({'tranche': '10M à 40M', 'taux': '1.0%', 'base': float(t2), 'montant': float(amt2)})
            remaining -= t2
            
        # Tranche 3: 40M à 150M (0.75%)
        if remaining > 0:
            t3 = min(remaining, Decimal('110000000'))
            amt3 = t3 * Decimal('0.0075')
            honoraires_ht += amt3
            honoraires_details.append({'tranche': '40M à 150M', 'taux': '0.75%', 'base': float(t3), 'montant': float(amt3)})
            remaining -= t3
            
        # Tranche 4: Plus de 150M (0.5%)
        if remaining > 0:
            amt4 = remaining * Decimal('0.005')
            honoraires_ht += amt4
            honoraires_details.append({'tranche': 'Plus de 150M', 'taux': '0.5%', 'base': float(remaining), 'montant': float(amt4)})
            
        # TVA (18%)
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 3. Droits de Succession (Fisc)
        # Base is same as honoraires base
        total_base = base_honoraires
        droits_fisc = Decimal(0)
        penalites_fisc = Decimal(0)
        
        if total_base <= Decimal('200000000'):
            # Case <= 200M: 0.25% with 25,000 minimum
            droit_simple = max(Decimal('25000'), total_base * Decimal('0.0025'))
            droits_fisc = droit_simple
        else:
            # Case > 200M: Proportionnal on excess
            # 3% if Directe (parente=1), 10% if Others (parente=2)
            excess = total_base - Decimal('200000000')
            rate = Decimal('0.03') if parente == 1 else Decimal('0.10')
            droit_simple = excess * rate
            droits_fisc = droit_simple
            
        # Pénalités logic (1% per month after delay limit)
        # Delay limit: 6 months (local), 12 months (foreign)
        delay_limit = 6 if lieu_deces == 1 else 12
        retard_mois = max(0, mois_penalite - delay_limit)
        if retard_mois > 0:
            # 1% per month
            raw_penalty = droits_fisc * Decimal(str(retard_mois)) * Decimal('0.01')
            # Capped at 50% of the principal
            penalites_fisc = min(raw_penalty, droits_fisc / Decimal('2'))
        
        # 4. Conservation Foncière
        # Base = Imm - Passif (as per formula H23-H25)
        conservation_totale = Decimal(0)
        if inclure_conservation and val_immeuble > 0:
            cf_base = max(Decimal(0), val_immeuble - val_passif)
            # floor to thousands then 1%
            conservation_totale = SharedCalculator.conservation_fonciere(cf_base)

        # 5. Débours et Frais Fixes
        # Droit Mutation (Bracketed)
        droit_mutation = Decimal(0)
        droit_mutation = SharedCalculator.mutation_amount(val_immeuble)
            
        debours = {
            'droit_mutation': droit_mutation,
            'notoriete': Decimal('40000'),
            'procuration': Decimal('40000'),
            'exequatur': Decimal('40000'),
            'frais_generaux': Decimal('50000')
        }
        total_debours = sum(debours.values())
        
        # Final Sum
        subtotal = total_honoraires + droits_fisc + penalites_fisc + conservation_totale + total_debours
        # Excel uses ROUNDUP(..., -3) which means round up to nearest 1000
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'actif_net': float(base_honoraires), # This is base for honoraires
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': honoraires_details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            'droits_fisc': float(droits_fisc),
            'penalites_fisc': float(penalites_fisc),
            'conservation_fonciere': float(conservation_totale),
            'debours_details': {k: float(v) for k, v in debours.items()},
            'total_debours': float(total_debours),
            'total_general': float(total_general)
        }
