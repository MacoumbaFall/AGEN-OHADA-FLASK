import pandas as pd
import sys

excel_file = "bareme.xls"
sheet_name = "SUCCESSION"

try:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(f"--- Content of sheet: {sheet_name} ---")
    print(df.to_string())
    print("\n--- Column Names ---")
    print(df.columns.tolist())
except Exception as e:
    print(f"Error: {e}")
