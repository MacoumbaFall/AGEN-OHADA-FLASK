from decimal import Decimal
import pytest
from app.actes.calculators.vente import VenteCalculator
from app.actes.calculators.societe import SarlCalculator
from app.actes.calculators.donation_partage import PartageCalculator
from app.actes.calculators.succession import SuccessionCalculator

class TestBaremesCalculators:

    def test_vente_calculator_standard(self):
        # Case: 10,000,000 CFA, 10% registration, with morcellement
        # Honoraires: 10M * 4.5% = 450,000
        # TVA: 450,000 * 18% = 81,000
        # Enregistrement: 10M * 10% = 1,000,000
        # CF: 10M * 1% = 100,000 (no fixed fee because morcellement=True)
        # Morcellement: 22,500
        # Mutation: 10,000 (val > 1.5M, <= 2.5M ? No, 10M > 2.5M so 20,000)
        # Debours: 50,000 (exp) + 50,000 (div) = 100,000
        # Mutation fix: Vente uses SharedCalculator.mutation_amount(10M) -> 20,000
        
        res = VenteCalculator.calculate(prix=10000000, taux_enregistrement=10, morcellement=True)
        
        assert res['base'] == 10000000.0
        assert res['honoraires_ht'] == 450000.0
        assert res['tva'] == 81000.0
        assert res['enregistrement'] == 1000000.0
        assert res['conservation_fonciere'] == 100000.0
        assert res['frais_morcellement'] == 22500.0
        assert res['total_debours'] == 100000.0 + 20000.0 + 22500.0 # 142500
        
        # Subtotal: 450k + 81k + 1M + 100k + 142.5k = 1,773,500
        # Roundup to 1000: 1,774,000
        assert res['total_general'] == 1774000.0

    def test_sarl_calculator(self):
        # Case: 1,000,000 CFA (Min honoraires check)
        # Honoraires: 1M * 2% = 20,000. Min is 100,000.
        # TVA: 100,000 * 18% = 18,000
        # Enregistrement: 25,000 (cap <= 100M)
        # Greffe: 32,090
        # Debours SARL: 55,000 (pub) + 50,000 (exp) + 59,000 (drc) = 164,000
        # Total Debours = 164,000 + 32,090 = 196,090
        
        res = SarlCalculator.calculate(capital=1000000)
        assert res['honoraires_ht'] == 100000.0
        assert res['tva'] == 18000.0
        assert res['enregistrement'] == 25000.0
        assert res['greffe'] == 32090.0
        assert res['total_debours'] == 196090.0
        
        # Subtotal: 100k + 18k + 25k + 196,090 = 339,090
        # Roundup: 340,000
        assert res['total_general'] == 340000.0

    def test_partage_calculator(self):
        # Fixed the bug earlier, let's test.
        # Case: 100,000,000 CFA Actif Net, no debt, no soulte
        # Honoraires: 
        #   10M * 4% = 400,000
        #   30M * 3% = 900,000
        #   60M * 1.5% = 900,000
        # Total: 2,200,000
        # TVA: 2.2M * 18% = 396,000
        # Enregistrement: 100M * 1% = 1,000,000
        # Mutation: 100M > 2.5M -> 20,000
        # Debours: 50,000 (exp) + 50,000 (div) = 100,000
        # Total Debours = 100,000 + 20,000 = 120,000 (no morcellement)
        
        res = PartageCalculator.calculate(actif_brut=100000000, passif=0, soulte=0)
        assert res['honoraires_ht'] == 2200000.0
        assert res['tva'] == 396000.0
        assert res['droits_detail']['total_enregistrement'] == 1000000.0
        assert res['total_debours'] == 120000.0
        
        # Subtotal: 2.2M + 396k + 1M + 120k = 3,716,000
        assert res['total_general'] == 3716000.0

    def test_succession_calculator(self):
        # Case: 50,000,000 CFA Imm, 0 Actif, 0 Passif
        # Honoraires:
        #   10M * 1.5% = 150,000
        #   30M * 1.0% = 300,000
        #   10M * 0.75% = 75,000
        # Total: 525,000
        # TVA: 525k * 18% = 94,500
        # Droits Fisc: 50M * 0.25% = 125,000 (>= 25,000)
        # CF: 50M * 1% + 6500 = 506,500
        # Debours: 40k(not) + 40k(proc) + 40k(exe) + 50k(gen) + 20k(mutation) = 190,000
        
        res = SuccessionCalculator.calculate(valeur_immeuble=50000000, reste_actif=0, passif=0)
        assert res['honoraires_ht'] == 525000.0
        assert res['tva'] == 94500.0
        assert res['droits_fisc'] == 125000.0
        assert res['conservation_fonciere'] == 506500.0
        assert res['total_debours'] == 190000.0
        
        # Subtotal: 525k + 94.5k + 125k + 506.5k + 190k = 1,441,000
        assert res['total_general'] == 1441000.0
