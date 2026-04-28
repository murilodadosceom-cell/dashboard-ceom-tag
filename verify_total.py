import pandas as pd

def calculate_total():
    fin_path = "ACOMPANHAMENTO PROTOCOLOS PACIENTES/Relatório de Controle Financeiro_ Tratamento Oftalmológico.xlsx"
    xl = pd.ExcelFile(fin_path)
    grand_total = 0
    for sheet_name in xl.sheet_names:
        df = pd.read_excel(fin_path, sheet_name=sheet_name, header=None)
        # Find cell with "TOTAL"
        found = False
        for r in range(len(df)):
            for c in range(df.shape[1]):
                if str(df.iloc[r, c]).upper().strip() == "TOTAL":
                    # Value is likely in the row below
                    if r + 1 < len(df):
                        val = df.iloc[r+1, c]
                        try:
                            val_num = float(val)
                            grand_total += val_num
                            # print(f"Sheet: {sheet_name} | Total: {val_num}")
                            found = True
                            break
                        except:
                            pass
            if found: break
    return grand_total

if __name__ == "__main__":
    t = calculate_total()
    print(f"Grand Total: {t}")
