from app.actes.calculators.succession import SuccessionCalculator
import json

def test_succession():
    # Case from the Excel dump:
    # Imm = 100M
    # Actif = 190M
    # Passif = 90M
    # Total Base = 290M
    # Delay = ? (Excel says ROUNDDOWN((C18-C17)/30, 0))
    # Duration = 7 months (from dump R42)
    # Lieu = 1 (Senegal) -> Delay limit 6
    # Delay = 7 - 6 = 1 month
    # Parente = 2 (Autres -> 10%)
    
    params = {
        'valeur_immeuble': 100000000,
        'reste_actif': 190000000,
        'passif': 90000000,
        'mois_penalite': 7,
        'inclure_conservation': True,
        'lieu_deces': 1,
        'parente': 2
    }
    
    result = SuccessionCalculator.calculate(**params)
    print(json.dumps(result, indent=2))

    # Expected from Excel:
    # Honoraires: 1,975,000
    # TVA: 355,500
    # Droit Succession (>200M): (290M-200M)*10% = 9,000,000
    # Penalties: Delay 1 month -> 1% of 9M = 90,000
    # Conservation Fonciere: (100M-90M)*1% + 6500 = 106,500
    # Droit Mutation: H23 > 2.5M -> 20,000
    # Other debours: 40k+40k+40k+50k = 170,000
    # Total debours = 20k + 170k = 190,000
    # Subtotal = 1,975,000 + 355,500 + 9,000,000 + 90,000 + 106,500 + 190,000 = 11,717,000
    # Roundup to thousands: 11,717,000
    
    expected_total = 11717000
    if result['total_general'] == expected_total:
        print("\nSUCCESS: Matches Excel exactly!")
    else:
        print(f"\nFAILURE: Expected {expected_total}, got {result['total_general']}")

if __name__ == "__main__":
    # We need a dummy app context or just run the calculator directly (it doesn't use DB)
    test_succession()
