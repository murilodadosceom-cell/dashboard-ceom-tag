import streamlit as st

st.set_page_config(
    page_title="CEOM - Super Dashboard",
    page_icon="🏥",
    layout="wide"
)

# -----------------------------
# AUTENTICAÇÃO GLOBAL
# -----------------------------
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.title("🔒 Acesso Restrito - CEOM")
    st.markdown("Por favor, faça login para acessar o sistema unificado da clínica.")
    
    with st.form("login_form"):
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        submit_button = st.form_submit_button("Entrar")
        
        if submit_button:
            if usuario == "admin" and senha == "admin":
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    
    st.stop()

# -----------------------------
# HOME / NAVEGAÇÃO
# -----------------------------
st.title("🏥 CEOM - Sistema Unificado de Dashboards")
st.markdown("Bem-vindo ao sistema integrado. Utilize o menu lateral esquerdo para navegar entre os módulos.")

st.info("👈 Selecione um dos dashboards no menu lateral.")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Visão Geral Clínica")
    st.write("Análise demográfica completa dos pacientes da clínica (Idade, Gênero, Município).")

with col2:
    st.markdown("### 👁️ Controle TAG")
    st.write("Dashboard estratégico focado no acompanhamento de injeções, custos e prontuário digital.")

with col3:
    st.markdown("### 🏥 Reguladora Ocular")
    st.write("Painel no padrão SESAB para controle de autorizações, sessões e histórico cirúrgico.")

st.markdown("---")
st.markdown("🚀 *Dados sincronizados diretamente da nuvem em tempo real.*")

if st.button("Sair do Sistema 👋"):
    st.session_state.logado = False
    st.rerun()
