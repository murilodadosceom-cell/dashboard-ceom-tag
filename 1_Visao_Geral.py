import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Adiciona o diretório pai ao sys.path para importar data_loader_cloud
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader_cloud import load_clinica_data

if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("⚠️ Faça login na página principal para acessar este módulo.")
    st.stop()

st.title("📊 Visão Geral Clínica")
st.markdown("Análise automática da base de dados de pacientes da clínica.")

with st.spinner("Sincronizando dados com a nuvem..."):
    df_original = load_clinica_data()

if df_original is None:
    st.error("Erro ao carregar os dados da nuvem. Verifique a conexão ou a URL do Google Drive.")
    st.stop()

df = df_original.copy()

# FILTROS
st.sidebar.header("🔍 Filtros (Visão Geral)")
if "cidade" in df.columns:
    cidades = sorted([str(c) for c in df["cidade"].unique() if str(c) not in ["nan", "None", "Não Informada"]])
    cidades_selecionadas = st.sidebar.multiselect("Filtrar por cidade", options=cidades, placeholder="Selecione Cidades")
    if cidades_selecionadas:
        df = df[df["cidade"].isin(cidades_selecionadas)]
        
if "genero" in df.columns:
    generos_disponiveis = df["genero"].unique()
    genero_selecionado = st.sidebar.multiselect("Filtrar por Gênero", options=generos_disponiveis, default=generos_disponiveis)
    if genero_selecionado:
        df = df[df["genero"].isin(genero_selecionado)]

# KPIS
st.subheader("Indicadores Gerais")
col_kpi1, col_kpi2 = st.columns(2)
with col_kpi1:
    st.metric(label="Total de Pacientes Filtrados", value=f"{len(df):,}".replace(',', '.'))
with col_kpi2:
    idade_media = int(df["idade"].mean()) if "idade" in df.columns and not df["idade"].dropna().empty else 0
    st.metric(label="Idade Média", value=str(idade_media) + " anos")

st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Distribuição por Gênero")
    if "genero" in df.columns:
        genero_counts = df["genero"].value_counts().reset_index()
        genero_counts.columns = ["Gênero", "Quantidade"]
        cores_verdes_pizza = ["#2e7d32", "#66bb6a", "#a5d6a7", "#c8e6c9", "#1b5e20"]
        if not genero_counts.empty:
            fig_genero = px.pie(genero_counts, names="Gênero", values="Quantidade", color_discrete_sequence=cores_verdes_pizza, hole=0.4)
            fig_genero.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_genero, use_container_width=True)
        else:
            st.info("Sem dados para o filtro aplicado.")

with col2:
    st.subheader("Ranking das 10 Maiores Cidades")
    if "cidade" in df.columns:
        cidades_counts = df["cidade"].value_counts().head(10).reset_index()
        cidades_counts.columns = ["Cidade", "Quantidade"]
        if not cidades_counts.empty:
            fig_cidades = px.bar(cidades_counts, x="Quantidade", y="Cidade", orientation='h', color_discrete_sequence=["#2e7d32"] * len(cidades_counts))
            fig_cidades.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_cidades, use_container_width=True)
        else:
            st.info("Sem dados para o filtro aplicado.")

if "idade" in df.columns and not df.empty:
    st.subheader("Distribuição por Faixa Etária")
    bins = [0, 12, 18, 30, 45, 60, 75, 120]
    labels = ["0-12", "13-18", "19-30", "31-45", "46-60", "61-75", "76+"]
    df_idade_valida = df.dropna(subset=['idade']).copy()
    if not df_idade_valida.empty:
        df_idade_valida["faixa_etaria"] = pd.cut(df_idade_valida["idade"], bins=bins, labels=labels, right=False)
        faixa_counts = df_idade_valida["faixa_etaria"].value_counts().sort_index().reset_index()
        faixa_counts.columns = ["Faixa Etária", "Quantidade"]
        fig_faixa = px.bar(faixa_counts, x="Faixa Etária", y="Quantidade", color_discrete_sequence=["#4caf50"])
        fig_faixa.update_layout(margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig_faixa, use_container_width=True)
