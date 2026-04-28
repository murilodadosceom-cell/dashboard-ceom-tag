import pandas as pd
import numpy as np
import os

def load_data():
    # 1. Load General Injection Data (Murilo)
    try:
        df_murilo = pd.read_excel("PACIENTES INJEÇOES MURILO (1).xlsx")
        df_murilo.columns = [c.strip() for c in df_murilo.columns]
        session_cols = [c for c in df_murilo.columns if 'SESSAO' in c]
        df_murilo['N° DE INJEÇÕES'] = df_murilo[session_cols].notnull().sum(axis=1)
    except Exception as e:
        print(f"Error loading Murilo data: {e}")
        df_murilo = pd.DataFrame()

    # 2. Load Quantitative Data
    try:
        df_tag_quant = pd.read_excel("PLANILHA TAG - OUTUBRO A MARÇO (1) (1).xlsx")
    except Exception as e:
        print(f"Error loading TAG quantitative data: {e}")
        df_tag_quant = pd.DataFrame()

    # 3. Load Financial Complications Data
    fin_path = "ACOMPANHAMENTO PROTOCOLOS PACIENTES/Relatório de Controle Financeiro_ Tratamento Oftalmológico.xlsx"
    all_complications = []
    patient_totals = []
    
    try:
        xl = pd.ExcelFile(fin_path)
        for sheet_name in xl.sheet_names:
            df_sheet = pd.read_excel(fin_path, sheet_name=sheet_name, header=None)
            if df_sheet.empty or len(df_sheet) < 2: continue
            
            patient_name = sheet_name 
            if sheet_name.startswith("Table"):
                possible_names = df_sheet.iloc[1:5, 2].dropna().unique()
                for name in possible_names:
                    if name not in ["Recebedor", "Paciente", "Centro de Especialidades", "COMPROVAÇÕES", "Data"]:
                        patient_name = name
                        break
            
            # Extract Official Total
            official_total = 0
            for r in range(len(df_sheet)):
                for c in range(df_sheet.shape[1]):
                    if str(df_sheet.iloc[r, c]).upper().strip() == "TOTAL":
                        if r + 1 < len(df_sheet):
                            try:
                                official_total = float(df_sheet.iloc[r+1, c])
                            except:
                                pass
                        break
                if official_total > 0: break
            
            patient_totals.append({'Patient': patient_name, 'TotalOfficial': official_total})
            
            # Extract Individual Expenses
            header_row = 0
            for i in range(len(df_sheet)):
                if str(df_sheet.iloc[i, 0]).lower() == 'data':
                    header_row = i
                    break
            
            expenses = df_sheet.iloc[header_row+1:, [0, 1, 2, 3]].copy()
            expenses.columns = ['Data', 'Valor', 'Recebedor', 'Categoria']
            expenses['Patient'] = patient_name
            expenses = expenses[expenses['Valor'].notnull() & (expenses['Valor'] != '--')]
            
            # --- DATE CORRECTION LOGIC ---
            def fix_date(d):
                if pd.isnull(d): return d
                try:
                    # If it's already a datetime, check if month is impossible (>4)
                    if isinstance(d, pd.Timestamp):
                        if d.month > 4:
                            # Swap day and month
                            return pd.Timestamp(year=d.year, month=d.day, day=d.month)
                        return d
                    # If it's a string, try dayfirst
                    dt = pd.to_datetime(d, dayfirst=True, errors='coerce')
                    if pd.notnull(dt) and dt.month > 4:
                         return pd.Timestamp(year=dt.year, month=dt.day, day=dt.month)
                    return dt
                except:
                    return d

            expenses['Data'] = expenses['Data'].apply(fix_date)
            
            # STRICT MASTER CATEGORY MAPPING
            def map_master_category(cat_row):
                orig_cat = str(cat_row).upper()
                if 'ENTREGA' in orig_cat: return 'ENTREGA DE MEDICAM.'
                if any(x in orig_cat for x in ['CIRURGIA', 'VITRECTOMIA', 'FACO', 'ANESTESISTA', 'LIO', 'SILICONE', 'MEDIC', 'CONSULTA', 'EXAME', 'USG', 'OCULOS', 'OTICA']):
                    return 'CIRURGIAS/PROCED.'
                if any(x in orig_cat for x in ['ALIMENTA', 'REFEI']): return 'ALIMENTAÇÃO'
                if any(x in orig_cat for x in ['MEDICAM', 'MEDICA', 'FARMACIA', 'INSUMO', 'ATB']): return 'FARMACIA'
                if any(x in orig_cat for x in ['HOSPEDAGEM', 'POUSADA', 'HOTEL']): return 'HOSPEDAGEM'
                if any(x in orig_cat for x in ['COMBUSTIVEL', 'TRANSPORTE', 'UBER', 'PASSAGEM', 'LOCOMO', 'VIAGEM', 'DESLOCA']):
                    return 'COMBUSTIVEL/LOGIST.'
                return 'DIVERSOS/OUTROS'
            
            if not expenses.empty:
                expenses['Categoria Master'] = expenses['Categoria'].apply(map_master_category)
                all_complications.append(expenses)
            
        df_complications = pd.concat(all_complications, ignore_index=True) if all_complications else pd.DataFrame()
        df_patient_totals = pd.DataFrame(patient_totals)
        
        if not df_complications.empty:
            df_complications['Valor'] = pd.to_numeric(df_complications['Valor'], errors='coerce').fillna(0)

    except Exception as e:
        print(f"Error consolidating financial data: {e}")
        df_complications = pd.DataFrame()
        df_patient_totals = pd.DataFrame()

    return df_murilo, df_tag_quant, df_complications, df_patient_totals
