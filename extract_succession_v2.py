import pandas as pd

excel_file = "bareme.xls"
sheet_name = "SUCCESSION"

try:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    print(f"Rules extraction for {sheet_name}:")
    for i, row in df.iterrows():
        # Clean the row to show only non-NaN values with their column index
        clean_row = {idx: val for idx, val in enumerate(row) if pd.notnull(val)}
        if clean_row:
            print(f"Row {i}: {clean_row}")

except Exception as e:
    print(f"Error: {e}")
