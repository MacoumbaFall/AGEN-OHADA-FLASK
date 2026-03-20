import sys
import os
import json
from decimal import Decimal

# Add project root to path
sys.path.append(os.getcwd())

from app import create_app, db
from app.actes.calculators.dynamic_engine import DynamicCalculatorEngine

app = create_app()

def test_vente_15m():
    with app.app_context():
        print("--- TEST DYNAMIQUE : VENTE 15M FCFA ---")
        
        inputs = {
            'prix_vente': 15000000,
            'taux_enreg': 5,
            'morcellement': True
        }
        
        try:
            result = DynamicCalculatorEngine.calculate('VENTE', inputs)
            
            print("\nInputs validés :", result['inputs'])
            print("\nLignes de frais générées :")
            for ligne in result['lignes']:
                print(f" - {ligne['libelle']} : {ligne['montant']:,.0f} FCFA")
            
            print(f"\nTOTAL GÉNÉRAL : {result['total_general']:,.0f} FCFA")
            
            # Vérification basique
            # Honoraires 4.5% de 15M = 675,000
            # Enreg 5% de 15M = 750,000
            # Consrv 1% de 15M = 150,000
            # Morc = 22,500
            # Mut = 20,000
            # Exp = 50,000
            # Div = 50,000
            # TVA 18% sur 675,000 = 121,500
            # Total = 1,839,000
            
            expected = 1839000
            if result['total_general'] == expected:
                print("\n✅ SUCCÈS : Le calcul est conforme à 100% !")
            else:
                print(f"\n❌ ERREUR : Attendu {expected:,.0f}, obtenu {result['total_general']:,.0f}")
                
        except Exception as e:
            print(f"Erreur fatale de calcul : {e}")

if __name__ == "__main__":
    test_vente_15m()
