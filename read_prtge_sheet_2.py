import pandas as pd

file_path = r'c:\Users\Admin\Documents\Repository\AGEN-OHADA-flask\AGEN-OHADA-FLASK\BAREME.xlsm'
try:
    df = pd.read_excel(file_path, sheet_name='PRTGE IMMEUBLE', header=None, skiprows=19)
    print(df.head(20).to_string())
except Exception as e:
    print(f"Error: {e}")
