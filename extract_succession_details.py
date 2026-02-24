import pandas as pd
import numpy as np

excel_file = "bareme.xls"
sheet_name = "SUCCESSION"

try:
    # Read the sheet, skipping first few rows if necessary or just reading all
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    print(f"--- FULL EXTRACT: {sheet_name} ---")
    # Set display options to see everything
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    
    # We clean the columns for better analysis
    df.columns = [f"Col_{i}" for i in range(len(df.columns))]
    
    print(df)

except Exception as e:
    print(f"Error: {e}")
