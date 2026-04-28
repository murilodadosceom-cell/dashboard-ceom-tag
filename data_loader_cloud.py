import pandas as pd
import streamlit as st
import requests
from io import BytesIO
import datetime

@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_clinica_data():
    """Carrega dados do dashboard-clinica (Google Drive CSV)"""
    url = "https://drive.google.com/uc?export=download&id=1PDrNuPhwAbCseytVgpKaa0LvPJhoH2Ds"
    try:
        df = pd.read_csv(url, sep=";", encoding="latin-1", on_bad_lines='skip', dtype={'NUMCPF': str, 'NUMTELEFONE': str, 'NUCELULAR': str})
        
        # Normalização básica
        df = df.rename(columns={"CDSEXO": "genero", "NMCIDADE": "cidade", "DTNASCIMENTO": "data_nascimento"})
        if "data_nascimento" in df.columns:
            df["data_nascimento"] = pd.to_datetime(df["data_nascimento"], format="%d.%m.%Y", errors="coerce")
            hoje = datetime.datetime.today()
            df["idade"] = df["data_nascimento"].apply(lambda x: hoje.year - x.year - ((hoje.month, hoje.day) < (x.month, x.day)) if pd.notnull(x) else None)
        
        if "genero" in df.columns: df["genero"] = df["genero"].fillna("Não Informado")
        if "cidade" in df.columns: df["cidade"] = df["cidade"].fillna("Não Informada")
        
        return df
    except Exception as e:
        print(f"Erro ao carregar Clínica: {e}")
        return None

@st.cache_data(ttl=600)
def load_ceom_tag_data():
    """Carrega dados do dashboard-ceom-tag (Excel do GitHub)"""
    url_murilo = "https://raw.githubusercontent.com/murilodadosceom-cell/dashboard-ceom-tag/main/PACIENTES%20INJE%C3%87OES%20MURILO%20(1).xlsx"
    url_quant = "https://raw.githubusercontent.com/murilodadosceom-cell/dashboard-ceom-tag/main/PLANILHA%20TAG%20-%20OUTUBRO%20A%20MAR%C3%87O%20(1)%20(1).xlsx"
    url_evo = "https://raw.githubusercontent.com/murilodadosceom-cell/dashboard-ceom-tag/main/EVOLUCA%CC%83O%20PACIENTES%20TAG.xlsx"
    
    try:
        r_murilo = requests.get(url_murilo)
        df_murilo = pd.read_excel(BytesIO(r_murilo.content))
        
        r_quant = requests.get(url_quant)
        df_tag_quant = pd.read_excel(BytesIO(r_quant.content))
        
        r_evo = requests.get(url_evo)
        df_evo = pd.read_excel(BytesIO(r_evo.content))
        df_evo.columns = [c.strip() for c in df_evo.columns]
        
        # Lógica de finanças/complicações embutida (mesma do data_loader antigo)
        complications = []
        patient_totals = {}
        for index, row in df_murilo.iterrows():
            patient_name = row['PACIENTE'] if 'PACIENTE' in df_murilo.columns else "Desconhecido"
            for col in df_murilo.columns:
                if isinstance(col, str) and (col.startswith('VALOR ') or ' CUSTO ' in col or col.startswith('CUSTO ')):
                    val = row[col]
                    if pd.notnull(val) and val != 0 and str(val).strip() != '':
                        cat_master = ' '.join(col.split()[1:]) if col.startswith('VALOR ') else col
                        complications.append({'Patient': patient_name, 'Data': row.get('DATA', pd.NaT), 'Categoria Master': cat_master, 'Valor': val})
            total_val = row.get('TOTAL GASTO', 0)
            if pd.notnull(total_val) and total_val != 0:
                patient_totals[patient_name] = total_val
                
        df_complications = pd.DataFrame(complications)
        df_patient_totals = pd.DataFrame(list(patient_totals.items()), columns=['Patient', 'TotalOfficial'])
        
        return df_murilo, df_tag_quant, df_complications, df_patient_totals, df_evo
    except Exception as e:
        print(f"Erro ao carregar TAG: {e}")
        return None, None, None, None, None

@st.cache_data(ttl=600)
def load_reguladora_data():
    """Carrega dados do dashboard-ceom (Banco Reguladora Excel do GitHub)"""
    url_banco = "https://raw.githubusercontent.com/murilodadosceom-cell/dashboard-ceom/main/BANCO%20PACIENTES%20APLICACOES.xlsx"
    try:
        r_banco = requests.get(url_banco)
        df = pd.read_excel(BytesIO(r_banco.content), header=None)
        df = df.iloc[1:].reset_index(drop=True)
        
        mapeamento = {
            0: "CONTATO", 1: "PACIENTE", 2: "genero", 3: "MUNICIPIO", 4: "OLHO",
            5: "CNS", 6: "DN", 7: "LISTA_UNICA_CONSULTA", 8: "OBS_STATUS", 9: "TELEFONE",
            10: "DATA_CONSULTA", 11: "CID", 12: "1_INDICACAO", 13: "STATUS_S1", 14: "DATA_S1",
            15: "STATUS_S2", 16: "DATA_S2", 17: "STATUS_S3", 18: "DATA_S3", 19: "2_INDICACAO",
            20: "OLHO_2", 21: "STATUS_S4", 22: "DATA_S4", 23: "STATUS_S5", 24: "DATA_S5",
            25: "STATUS_S6", 26: "DATA_S6", 28: "DATA_FATURADO", 29: "COMPETENCIA", 30: "MEDICO",
            31: "2_APLIC_LISTA", 32: "3_SESSAO", 33: "DATA_ORIGINAL_EXTRA", 34: "DATA_FATURADO_EXTRA",
            35: "COMPETENCIA_EXTRA", 36: "MEDICO_EXTRA", 37: "3_APLIC_LISTA", 38: "AUTORIZACAO",
            39: "VENCIMENTO", 40: "OBS"
        }
        df = df.rename(columns=mapeamento)
        df["PACIENTE"] = df["PACIENTE"].fillna("").astype(str).str.strip()
        df = df[df["PACIENTE"] != ""]
        
        def formatar_genero(v):
            v = str(v).upper().strip()
            if v == "M": return "Masculino"
            if v == "F": return "Feminino"
            return v if v != "NAN" else "Não Informado"
        df["genero"] = df["genero"].apply(formatar_genero)
        
        for col in ["DN", "DATA_CONSULTA"]:
            if col in df.columns: df[col] = pd.to_datetime(df[col], errors='coerce')
            
        hoje = datetime.datetime.today()
        df["Idade"] = df["DN"].apply(lambda x: hoje.year - x.year - ((hoje.month, hoje.day) < (x.month, x.day)) if pd.notnull(x) else None)
        bins = [0, 18, 40, 60, 75, 120]
        labels = ["0-18", "19-40", "41-60", "61-75", "76+"]
        df["Faixa Etária"] = pd.cut(df["Idade"], bins=bins, labels=labels, right=False)
        
        colunas_status = ["STATUS_S1", "STATUS_S2", "STATUS_S3", "STATUS_S4", "STATUS_S5", "STATUS_S6"]
        df["QTD_APLICACOES"] = df[colunas_status].apply(lambda row: row.map(lambda v: 1 if "OK" in str(v).upper() else 0).sum(), axis=1)
        
        return df
    except Exception as e:
        print(f"Erro ao carregar Reguladora: {e}")
        return None
