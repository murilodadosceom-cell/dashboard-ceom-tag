import pandas as pd

def get_info(path):
    print(f"\nFILE: {path}")
    try:
        xl = pd.ExcelFile(path)
        print(f"Sheets: {xl.sheet_names}")
        df = pd.read_excel(path, sheet_name=xl.sheet_names[0])
        print(f"Columns: {df.columns.tolist()}")
        print(f"Sample:\n{df.head(3).to_string()}")
    except Exception as e:
        print(f"Error: {e}")

get_info("PACIENTES INJEÇOES MURILO (1).xlsx")
get_info("PLANILHA TAG - OUTUBRO A MARÇO (1) (1).xlsx")
get_info("ACOMPANHAMENTO PROTOCOLOS PACIENTES/Relatório de Controle Financeiro_ Tratamento Oftalmológico.xlsx")
