import pandas as pd

def check_columns(path):
    print(f"\nFILE: {path}")
    try:
        df = pd.read_excel(path)
        print(f"Columns: {df.columns.tolist()}")
        print(f"First 2 rows:\n{df.head(2)}")
    except Exception as e:
        print(f"Error: {e}")

check_columns("PACIENTES INJEÇOES MURILO (1).xlsx")
