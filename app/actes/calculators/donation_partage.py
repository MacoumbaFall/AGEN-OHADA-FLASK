from decimal import Decimal
from typing import Dict, Any
from app.actes.calculators.shared import SharedCalculator

class DonationCalculator:
    # ... (unchanged code for DonationCalculator, keeping it here for context if reusing same file, 
    # but I will only overwrite PartageCalculator logic if I can target it specificially. 
    # Since I'm rewriting the file to ensure cleanliness with new imports/structure)


    @staticmethod
    def calculate(valeur: float = 0, parente: int = 1) -> Dict[str, Any]:
        val = Decimal(str(valeur))
        honoraires_ht, details = SharedCalculator.calculate_brackets(
            val, 
            SharedCalculator.get_standard_brackets('0.045', '0.03', '0.015', '0.0075')
        )
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        rate = Decimal('0.03') if parente == 1 else Decimal('0.10')
        enregistrement = (val * Decimal('0.5')) * rate
        cf = SharedCalculator.conservation_fonciere(val)
        mutation = SharedCalculator.mutation_amount(val)
        debours = {
            'mutation': mutation,
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
            'total_debours': float(total_debours),
            'total_general': float(total_general)
        }

class PartageCalculator:
    # Note: L'UEMOA utilise un barème 1->10M, 10->40M, 40->150M pour le partage
    # On va utiliser get_standard_brackets mais avec les vrais taux et ajuster manuellement
    @classmethod
    def get_partage_brackets(cls):
        return [
            (Decimal('10000000'), Decimal('0.04'), "1 à 10 millions"),
            (Decimal('30000000'), Decimal('0.03'), "10 à 40 millions"),
            (Decimal('110000000'), Decimal('0.015'), "40 à 150 millions"),
            (None, Decimal('0.0075'), "Plus de 150 millions")
        ]

    @staticmethod
    def calculate(actif_brut: float = 0, passif: float = 0, soulte: float = 0,
                 avec_morcellement: bool = False, nb_parcelles: int = 1, cout_par_parcelle: float = 20000,
                 avec_cf: bool = False, valeur_immeuble_cf: float = 0,
                 cout_expeditions: float = 0, cout_divers: float = 0) -> Dict[str, Any]:
        
        val_actif = Decimal(str(actif_brut))
        val_passif = Decimal(str(passif))
        val_soulte = Decimal(str(soulte))
        val_expeditions = Decimal(str(cout_expeditions))
        val_divers = Decimal(str(cout_divers))
        
        # 1. Calcul Actif Net (Masse Partageable)
        val_actif_net = max(val_actif - val_passif, Decimal('0'))
        
        # 2. Honoraires globaux sur total actif - total passif (Actif Net)
        honoraires_ht, details = SharedCalculator.calculate_brackets(
            val_actif_net, 
            PartageCalculator.get_partage_brackets()
        )
        tva = honoraires_ht * SharedCalculator.TVA_RATE
        total_honoraires = honoraires_ht + tva
        
        # 3. Enregistrement
        reg_partage = val_actif_net * Decimal('0.01')
        reg_soulte = val_soulte * Decimal('0.15') # TODO: Confirmer ce taux 15% (Souvent 1% si entre héritiers)
        enregistrement = reg_partage + reg_soulte
        
        # 4. Conservation Foncière (CF)
        cf = Decimal('0')
        val_base_cf = Decimal(str(valeur_immeuble_cf)) if valeur_immeuble_cf > 0 else val_actif_net
        
        if avec_cf:
            cf = SharedCalculator.conservation_fonciere(val_base_cf)
        
        # 5. Morcellement (Débours cadastre / géomètre)
        cout_morcellement = Decimal('0')
        if avec_morcellement:
            COUT_PAR_PARCELLE = Decimal(str(cout_par_parcelle))
            cout_morcellement = Decimal(nb_parcelles) * COUT_PAR_PARCELLE

        # 6. Débours & Divers
        # Mutation (Frais fixes d'état)
        mutation = SharedCalculator.mutation_amount(val_base_cf)

        debours_detail = {
            'mutation': mutation,
            'expeditions': SharedCalculator.frais_expeditions() if val_expeditions == 0 else val_expeditions,
            'divers': SharedCalculator.frais_divers() if val_divers == 0 else val_divers,
            'morcellement': cout_morcellement
        }
        total_debours = sum(debours_detail.values())
        
        subtotal = total_honoraires + enregistrement + cf + total_debours
        total_general = SharedCalculator.roundup_thousand(subtotal)
        
        return {
            'base': float(val_actif_net),
            'actif_brut': float(val_actif),
            'passif': float(val_passif),
            'soulte': float(val_soulte),
            
            'honoraires_ht': float(honoraires_ht),
            'honoraires_details': details,
            'tva': float(tva),
            'total_honoraires': float(total_honoraires),
            
            'droits_detail': {
                'enregistrement_partage': float(reg_partage),
                'enregistrement_soulte': float(reg_soulte),
                'total_enregistrement': float(enregistrement),
                'conservation_fonciere': float(cf)
            },
            
            'debours_detail': {k: float(v) for k, v in debours_detail.items()},
            'total_debours': float(total_debours),
            'total_general': float(total_general)
        }
