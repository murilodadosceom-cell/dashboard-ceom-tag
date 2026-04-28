import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys

# Adiciona o diretório pai ao sys.path para importar data_loader_cloud
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_loader_cloud import load_reguladora_data, load_ceom_tag_data

if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("⚠️ Faça login na página principal para acessar este módulo.")
    st.stop()

# -----------------------------
# ESTILIZAÇÃO CUSTOMIZADA (CSS)
# -----------------------------
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #e0f2f1 0%, #ffffff 100%); }
    [data-testid="stMetricValue"] { color: #00509d; font-weight: bold; }
    div.stExpander, div.stForm { background-color: rgba(255, 255, 255, 0.8) !important; border: 1px solid #25b1b1; border-radius: 12px; box-shadow: 2px 4px 8px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

st.title("📊 Painel da Reguladora - Aplicações Oculares")

with st.spinner("Sincronizando dados com a nuvem..."):
    df = load_reguladora_data()
    _, _, _, _, df_tag = load_ceom_tag_data()  # Reutiliza o loader para pegar apenas a tabela TAG

if df is None or df.empty:
    st.error("Erro ao carregar o Banco da Reguladora da nuvem.")
    st.stop()

# --- KPIs NO TOPO DO DASHBOARD ---
st.markdown("### 📈 Visão Geral do Banco")
col_g1, col_g2, col_g3 = st.columns(3)

with col_g1:
    st.markdown("##### Gênero Atendido")
    gen_counts = df["genero"].value_counts().reset_index()
    gen_counts.columns = ["Gênero", "Quantidade"]
    sesab_palette = ["#25b1b1", "#00509d", "#ffc20e", "#f39200", "#e6007e", "#e30613", "#a6ce39"]
    fig_gen = px.pie(gen_counts, names="Gênero", values="Quantidade", hole=0.4, color_discrete_sequence=sesab_palette)
    fig_gen.update_layout(height=280, margin=dict(t=20, b=0, l=0, r=0))
    st.plotly_chart(fig_gen, use_container_width=True)

with col_g2:
    st.markdown("##### Distribuição por Faixa Etária")
    if "Faixa Etária" in df.columns:
        faixa_counts = df["Faixa Etária"].value_counts().sort_index().reset_index()
        faixa_counts.columns = ["Faixa", "Qtd"]
        fig_faixa = px.bar(faixa_counts, x="Faixa", y="Qtd", color_discrete_sequence=["#25b1b1"])
        fig_faixa.update_layout(height=280, margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig_faixa, use_container_width=True)

with col_g3:
    st.markdown("##### Total Banco")
    st.metric("Total de Pacientes no Sistema", value=f"{len(df):,}".replace(',', '.'))
    total_aplicacoes_ok = int(df["QTD_APLICACOES"].sum()) if "QTD_APLICACOES" in df.columns else 0
    st.metric("Total de Sessões 'OK'", value=f"{total_aplicacoes_ok:,}".replace(',', '.'))

st.markdown("---")
st.markdown("### 🔍 Filtros e Busca")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    lista_cidades = sorted([c for c in df["MUNICIPIO"].unique() if c and pd.notna(c)])
    cidade_selecionada = st.multiselect("Filtre pelo Município:", lista_cidades, placeholder="Selecione os Municípios")
if cidade_selecionada:
    df = df[df["MUNICIPIO"].isin(cidade_selecionada)]

with col_f3:
    if "DATA_CONSULTA" in df.columns:
        lista_datas_obj = sorted([d for d in df["DATA_CONSULTA"].dropna().unique() if pd.notna(d)], reverse=True)
        lista_datas_fmt = [pd.to_datetime(d).strftime('%d/%m/%Y') for d in lista_datas_obj]
        data_selecionada_fmt = st.multiselect("Filtrar Data da Consulta:", lista_datas_fmt, placeholder="Todas as Datas")
        if data_selecionada_fmt:
            df = df[df["DATA_CONSULTA"].dt.strftime('%d/%m/%Y').isin(data_selecionada_fmt)]

with col_f2:
    lista_pacientes = sorted([p for p in df["PACIENTE"].unique() if p and pd.notna(p)])
    paciente_selecionado = st.selectbox("Busca de Paciente (digite o nome):", ["-- Selecione --"] + list(lista_pacientes))

st.markdown("---")
if paciente_selecionado and paciente_selecionado != "-- Selecione --":
    df_paciente = df[df["PACIENTE"] == paciente_selecionado].iloc[0]
    
    st.markdown(f"### 📋 Histórico Completo: **{paciente_selecionado}**")
    
    with st.expander("👤 Dados do Paciente e Contato", expanded=True):
        c1, c2, c3, c4 = st.columns(4)
        dn_str = pd.to_datetime(df_paciente["DN"]).strftime('%d/%m/%Y') if pd.notna(df_paciente["DN"]) else "-"
        c1.markdown(f"**Nascimento:** {dn_str}")
        c1.markdown(f"**Gênero:** {df_paciente.get('genero', '-')}")
        c2.markdown(f"**Contato:** {df_paciente.get('CONTATO', '-')}")
        c2.markdown(f"**Telefone:** {df_paciente.get('TELEFONE', '-')}")
        c3.markdown(f"**CNS:** {df_paciente.get('CNS', '-')}")
        c3.markdown(f"**Município:** {df_paciente.get('MUNICIPIO', '-')}")
        c4.markdown(f"**Olho Princ.:** {df_paciente.get('OLHO', '-')}")

    with st.expander("👁️ Detalhes Clínicos e Sessões", expanded=True):
        c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
        c_kpi1.metric("🏥 Total Aplicações OK", value=int(df_paciente.get("QTD_APLICACOES", 0)))
        c_kpi2.metric("📋 1ª Indicação", value=str(df_paciente.get("1_INDICACAO", "-")))
        c_kpi3.metric("📅 Data Consulta", value=pd.to_datetime(df_paciente["DATA_CONSULTA"]).strftime('%d/%m/%Y') if pd.notna(df_paciente.get("DATA_CONSULTA")) else "-")
        c_kpi4.metric("⚖️ Lateralidade S4", value=str(df_paciente.get("OLHO_2", "-")))
        
        st.markdown("---")
        c_sessao1, c_sessao2 = st.columns(2)
        with c_sessao1:
            st.markdown("**📌 1ª Indicação (Sessões 1-3):**")
            sessoes_1_3 = []
            pares_1_3 = [("1ª Sessão", "STATUS_S1", "DATA_S1"), ("2ª Sessão", "STATUS_S2", "DATA_S2"), ("3ª Sessão", "STATUS_S3", "DATA_S3")]
            for nome, cs, cd in pares_1_3:
                sv = str(df_paciente.get(cs, '')).upper() if pd.notna(df_paciente.get(cs)) else "PENDENTE"
                dv = df_paciente.get(cd)
                ds = pd.to_datetime(dv).strftime('%d/%m/%Y') if pd.notna(dv) else "-"
                ic = "✅" if "OK" in sv else ("⏳" if "PENDENTE" in sv or sv == "" else "⚠️")
                sessoes_1_3.append({"Sessão": f"{ic} {nome}", "Data": ds, "Status": sv})
            st.table(pd.DataFrame(sessoes_1_3))

        with c_sessao2:
            st.markdown("**📍 2ª Indicação (Sessões 4-6):**")
            sessoes_4_6 = []
            pares_4_6 = [("4ª Sessão", "STATUS_S4", "DATA_S4"), ("5ª Sessão", "STATUS_S5", "DATA_S5"), ("6ª Sessão", "STATUS_S6", "DATA_S6")]
            for nome, cs, cd in pares_4_6:
                sv = str(df_paciente.get(cs, '')).upper() if pd.notna(df_paciente.get(cs)) else "PENDENTE"
                dv = df_paciente.get(cd)
                ds = pd.to_datetime(dv).strftime('%d/%m/%Y') if pd.notna(dv) else "-"
                ic = "✅" if "OK" in sv else ("⏳" if "PENDENTE" in sv or sv == "" else "⚠️")
                sessoes_4_6.append({"Sessão": f"{ic} {nome}", "Data": ds, "Status": sv})
            st.table(pd.DataFrame(sessoes_4_6))

elif paciente_selecionado == "-- Selecione --":
    st.info("👈 Selecione um paciente no filtro acima para carregar as datas cirúrgicas.")
    st.subheader(f"Visão Geral (Mostrando {len(df)} registros)")
    
    resumo_df = df[["PACIENTE", "MUNICIPIO", "DATA_CONSULTA", "QTD_APLICACOES", "OLHO"]].copy()
    if "DATA_CONSULTA" in resumo_df.columns:
        resumo_df["DATA_CONSULTA"] = pd.to_datetime(resumo_df["DATA_CONSULTA"]).dt.strftime('%d/%m/%Y').fillna("-")
    resumo_df.columns = ["Nome do Paciente", "Município", "Data da Consulta", "Nº de Aplicações", "Lateralidade"]
    st.dataframe(resumo_df, use_container_width=True, hide_index=True)

    # --- NOVA TABELA: PACIENTES COM COMPLICAÇÕES ---
    st.markdown("---")
    st.markdown("""<div style="background-color: #0d4d4d; color: white; padding: 10px; border-radius: 8px; margin-bottom: 15px;"><h3 style="margin: 0; font-size: 20px;">🧬 PACIENTES COM COMPLICAÇÕES (EVOLUÇÃO TAG)</h3></div>""", unsafe_allow_html=True)
    
    if df_tag is not None and not df_tag.empty:
        resumo_tag = df_tag.copy()
        colunas_reais = [c for c in resumo_tag.columns if "Unnamed" not in str(c)]
        for col in resumo_tag.columns:
            if resumo_tag[col].dtype == 'datetime64[ns]':
                resumo_tag[col] = resumo_tag[col].dt.strftime('%d/%m/%Y').fillna("-")
        st.dataframe(resumo_tag[colunas_reais], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado de complicação (TAG) encontrado na nuvem.")
