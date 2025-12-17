from decimal import Decimal
import pytest
from app.formalites.calculator import FormaliteCalculator, estimer_delai_formalite

class TestFormaliteCalculator:
    
    def test_enregistrement(self):
        # Normal case: 1,000,000 * 0.05 = 50,000
        res = FormaliteCalculator.calculer_enregistrement(1000000)
        assert res['total'] == Decimal('50000')
        
        # Minimum case: 100 * 0.05 = 5. Min is 10,000
        res = FormaliteCalculator.calculer_enregistrement(100)
        assert res['total'] == Decimal('10000')
        
        # Maximum case: 200,000,000 * 0.05 = 10,000,000. Max is 5,000,000
        res = FormaliteCalculator.calculer_enregistrement(200000000)
        assert res['total'] == Decimal('5000000')

    def test_hypotheque(self):
        # Case using Minimum: 1,000,000 * 0.02 = 20,000. Min is 25,000.
        # Fixed fees = 15,000. Total = 25,000 + 15,000 = 40,000.
        res = FormaliteCalculator.calculer_hypotheque(1000000)
        assert res['total'] == Decimal('40000') 

        # Normal Case: 10,000,000 * 0.02 = 200,000. 
        # Total = 200,000 + 15,000 = 215,000.
        res = FormaliteCalculator.calculer_hypotheque(10000000)
        assert res['total'] == Decimal('215000')

    def test_rccm(self):
        assert FormaliteCalculator.calculer_rccm('creation')['total'] == Decimal('50000')
        assert FormaliteCalculator.calculer_rccm('modification')['total'] == Decimal('25000')
        assert FormaliteCalculator.calculer_rccm('radiation')['total'] == Decimal('15000')
        # Default
        assert FormaliteCalculator.calculer_rccm('unknown')['total'] == Decimal('50000')

    def test_journal(self):
        # 10 lines * 5000 = 50,000
        assert FormaliteCalculator.calculer_journal(10)['total'] == Decimal('50000')
        # 2 lines * 5000 = 10,000. Min 30,000.
        assert FormaliteCalculator.calculer_journal(2)['total'] == Decimal('30000')

    def test_cadastre(self):
        assert FormaliteCalculator.calculer_cadastre('immatriculation')['total'] == Decimal('100000')
        assert FormaliteCalculator.calculer_cadastre('morcellement')['total'] == Decimal('75000')

    def test_generic_method(self):
        # Test routing via calculer_formalite
        res = FormaliteCalculator.calculer_formalite('ENREGISTREMENT', montant_acte=1000000)
        assert res['total'] == Decimal('50000')
        
        res = FormaliteCalculator.calculer_formalite('UNKNOWN_TYPE')
        assert res['total'] == Decimal('50000') # Default fallback

def test_delais():
    assert estimer_delai_formalite('ENREGISTREMENT')['jours'] == 3
    assert estimer_delai_formalite('CADASTRE')['jours'] == 45
    assert estimer_delai_formalite('UNKNOWN')['jours'] == 10 # Default
