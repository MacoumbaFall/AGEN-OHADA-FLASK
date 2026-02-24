import pandas as pd

file_path = r'c:\Users\Admin\Documents\Repository\AGEN-OHADA-flask\AGEN-OHADA-FLASK\BAREME.xlsm'
try:
    # Lire toute la feuille
    df = pd.read_excel(file_path, sheet_name='PRTGE IMMEUBLE', header=None)
    
    # Afficher les lignes 17 à 30 pour voir toutes les tranches
    print("=== TRANCHES HONORAIRES ===")
    for i in range(17, min(30, len(df))):
        row = df.iloc[i]
        # Afficher les colonnes pertinentes (généralement colonnes 1, 3, 5, 6)
        print(f"Ligne {i}: {row[1]} | {row[3]} | {row[5]} | {row[6]}")
    
    print("\n=== AUTRES PARAMETRES ===")
    # Afficher les lignes 30-50 pour voir enregistrement, soulte, etc.
    for i in range(30, min(50, len(df))):
        row = df.iloc[i]
        if pd.notna(row[1]) or pd.notna(row[3]):
            print(f"Ligne {i}: {row[1]} | {row[2]} | {row[3]} | {row[5]}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
