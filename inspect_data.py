import pandas as pd
import os

files = [
    "PACIENTES INJEÇOES MURILO (1).xlsx",
    "PLANILHA TAG - OUTUBRO A MARÇO (1) (1).xlsx",
    "ACOMPANHAMENTO PROTOCOLOS PACIENTES/Relatório de Controle Financeiro_ Tratamento Oftalmológico.xlsx"
]

for file in files:
    print(f"\n{'='*50}\nFILE: {file}\n{'='*50}")
    try:
        xl = pd.ExcelFile(file)
        print(f"Sheets: {xl.sheet_names[:5]}") # Print first 5 sheet names
        for sheet in xl.sheet_names[:2]: # Only first 2 sheets
            print(f"\n--- Sheet: {sheet} ---")
            df = pd.read_excel(file, sheet_name=sheet)
            print(f"Columns: {df.columns.tolist()}")
            print("First 5 rows:")
            print(df.head(5).to_string())
    except Exception as e:
        print(f"Error reading {file}: {e}")
