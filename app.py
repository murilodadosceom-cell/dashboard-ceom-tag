import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_loader import load_data
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="CEOM TAG Dashboard", page_icon="👁️", layout="wide", initial_sidebar_state="expanded")
# --- AUTHENTICATION ---
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] == "admin" and st.session_state["password"] == "admin":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.title("Acesso Restrito ao Sistema")
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.title("Acesso Restrito ao Sistema")
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Entrar", on_click=password_entered)
        st.error("😕 Usuário ou senha incorretos")
        return False
    else:
        # Password correct.
        return True

if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Orbitron:wght@400;700&display=swap');
    
    .main { background-color: #0e1117; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricValue"] { font-family: 'Orbitron', sans-serif; color: #00ffcc; text-shadow: 0 0 10px rgba(0, 255, 204, 0.5); }
    .stMetric { background: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(0, 255, 204, 0.2); }
    h1, h2, h3 { font-family: 'Orbitron', sans-serif; color: #00ffcc !important; text-transform: uppercase; letter-spacing: 2px; }
    .sidebar .sidebar-content { background-color: #161b22; }
    
    .detail-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 255, 204, 0.1);
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    .detail-card:hover {
        border: 1px solid rgba(0, 255, 204, 0.4);
        background: rgba(0, 255, 204, 0.02);
        transform: translateY(-2px);
    }
    .detail-label { 
        color: #00ffcc; 
        font-weight: bold; 
        font-size: 0.75em; 
        text-transform: uppercase; 
        letter-spacing: 1px;
        margin-bottom: 5px;
    }
    .detail-value { 
        color: #ffffff; 
        font-size: 1.1em; 
        font-family: 'Inter', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
df_murilo, df_tag_quant, df_complications, df_patient_totals = load_data()

# --- LOAD EVOLUTION DATA ---
@st.cache_data
def load_evolution():
    try:
        df_evo = pd.read_excel("EVOLUCÃO PACIENTES TAG.xlsx")
        df_evo.columns = [c.strip() for c in df_evo.columns]
        return df_evo
    except:
        return pd.DataFrame()

df_evolution = load_evolution()

# --- FORMATTING HELPERS ---
def format_currency(val):
    try:
        val = float(val)
        return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(val)

def format_date_resilient(dt):
    if pd.isnull(dt): return "N/A"
    if isinstance(dt, (pd.Timestamp, pd.DatetimeIndex)):
        return dt.strftime("%d/%m/%Y")
    return str(dt)

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("LOGO.png"):
        st.image("LOGO.png", width="stretch")
    st.title("TAG CONTROL")
    st.markdown("---")
    
    patient_col = 'PACIENTE' if 'PACIENTE' in df_murilo.columns else (df_murilo.columns[0] if not df_murilo.empty else None)
    all_patients = sorted(df_murilo[patient_col].dropna().unique()) if patient_col else []
    selected_patient = st.selectbox("Filtrar Paciente", ["Todos"] + all_patients)
    
    st.markdown("---")
    st.info("Painel de controle de alta complexidade para procedimentos TAG.")

# --- DATA FILTERING ---
def normalize(s):
    return str(s).strip().upper()

if selected_patient != "Todos":
    df_murilo_disp = df_murilo[df_murilo[patient_col] == selected_patient]
    sel_norm = normalize(selected_patient)
    df_complications_disp = df_complications[df_complications['Patient'].apply(normalize).str.contains(sel_norm, na=False)]
    df_evolution_disp = df_evolution[df_evolution['PACIENTE'].apply(normalize).str.contains(sel_norm, na=False)] if not df_evolution.empty else pd.DataFrame()
    df_totals_disp = df_patient_totals[df_patient_totals['Patient'].apply(normalize).str.contains(sel_norm, na=False)]
else:
    df_murilo_disp = df_murilo
    df_complications_disp = df_complications
    df_evolution_disp = df_evolution
    df_totals_disp = df_patient_totals

# --- MAIN DASHBOARD ---
st.title("DASHBOARD ESTRATÉGICO TAG - CEOM")

# Row 1: Key Metrics
col1, col2, col3 = st.columns(3)

with col1:
    total_injections = df_murilo_disp['N° DE INJEÇÕES'].sum() if not df_murilo_disp.empty else 0
    st.metric("Total de Injeções", f"{int(total_injections)}")

with col2:
    total_patients = len(df_murilo_disp) if not df_murilo_disp.empty else 0
    st.metric("Pacientes Atendidos", f"{total_patients}")

with col3:
    # USE OFFICIAL TOTAL FROM SHEETS
    total_cost = df_totals_disp['TotalOfficial'].sum() if not df_totals_disp.empty else 0
    st.metric("Custo Complicações", format_currency(total_cost))

st.markdown("---")

# Row 2: Complications and Costs
st.subheader("Impacto Financeiro de Complicações (Pós-Operatório)")
if not df_complications_disp.empty:
    col_table, col_chart = st.columns([1.2, 0.8])
    
    with col_table:
        df_comp_view = df_complications_disp[['Data', 'Patient', 'Categoria Master', 'Valor']].sort_values('Data', ascending=False).copy()
        df_comp_view['Data'] = df_comp_view['Data'].apply(format_date_resilient)
        df_comp_view['Valor'] = df_comp_view['Valor'].apply(format_currency)
        st.dataframe(df_comp_view, width="stretch", hide_index=True)
    
    with col_chart:
        # We still use the individual categories for the chart distribution
        cost_cat = df_complications_disp.groupby('Categoria Master')['Valor'].sum().reset_index()
        fig_cost = px.bar(cost_cat, x='Categoria Master', y='Valor', color='Valor',
                          color_continuous_scale='Greens', text_auto=False)
        fig_cost.update_traces(texttemplate='R$ %{y:,.2f}')
        fig_cost.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="#e0e0e0",
                              xaxis_title="", yaxis_title="Custo Total (R$)")
        st.plotly_chart(fig_cost, width="stretch")
else:
    st.info("Nenhuma complicação financeira registrada para os filtros selecionados.")

# --- SECTION: PRONTUÁRIO INTERATIVO ---
st.markdown("---")
st.subheader("Prontuário de Evolução Clínica")

if selected_patient != "Todos" and not df_evolution_disp.empty:
    evo = df_evolution_disp.iloc[0]
    st.markdown(f"**Prontuário Digital: {selected_patient}**")
    
    h1, h2, h3, h4 = st.columns(4)
    lat_reacao_col = [c for c in evo.index if 'LATERALIDADE' in c.upper() and 'REA' in c.upper()]
    lat_reacao = evo.get(lat_reacao_col[0], 'N/A') if lat_reacao_col else 'N/A'
    
    h1.info(f"**Lateralidade:**\n{evo.get('LATERALIDADE', 'N/A')}")
    h2.warning(f"**Lateralidade Reação:**\n{lat_reacao}")
    h3.info(f"**Lote:**\n{evo.get('LOTES', 'N/A')}")
    h4.info(f"**Idade:**\n{evo.get('IDADE', 'N/A')}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.write("**Detalhamento Completo do Prontuário**")
    
    cols = st.columns(4)
    for i, (label, value) in enumerate(evo.items()):
        if pd.notnull(value) and str(value).strip() != '' and value != 'N/A':
            display_value = value
            if isinstance(value, (pd.Timestamp, pd.DatetimeIndex)):
                display_value = value.strftime("%d/%m/%Y")
            
            with cols[i % 4]:
                st.markdown(f"""
                    <div class="detail-card">
                        <div class="detail-label">{label}</div>
                        <div class="detail-value">{display_value}</div>
                    </div>
                """, unsafe_allow_html=True)

elif selected_patient != "Todos":
    st.info("Dados de evolução não encontrados para este paciente.")
else:
    st.info("Selecione um paciente para visualizar o prontuário completo.")

# Row 4: Small Evolution Chart at the Bottom
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.subheader("Evolução Quantitativa Mensal")
if not df_tag_quant.empty:
    try:
        quant_clean = df_tag_quant.iloc[2:8, [1, 2, 3]].copy()
        quant_clean.columns = ['Mês', 'Pacientes', 'Olhos']
        _, mid_col, _ = st.columns([0.2, 0.6, 0.2])
        with mid_col:
            fig_evol = px.line(quant_clean, x='Mês', y=['Pacientes', 'Olhos'], 
                              markers=True, color_discrete_sequence=['#00ffcc', '#0099ff'], height=250)
            fig_evol.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
                                   font_color="#e0e0e0", xaxis_title="", yaxis_title="Qtd",
                                   margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_evol, width="stretch")
    except:
        st.write("Erro ao processar dados quantitativos.")
