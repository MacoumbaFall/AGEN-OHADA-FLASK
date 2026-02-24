import pandas as pd
import os

file_path = r'c:\Users\Admin\Documents\Repository\AGEN-OHADA-flask\AGEN-OHADA-FLASK\BAREME.xlsm'
if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit(1)

try:
    xl = pd.ExcelFile(file_path)
    print("Sheets:", xl.sheet_names)
except Exception as e:
    print(f"Error: {e}")
