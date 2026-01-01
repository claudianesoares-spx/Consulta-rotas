import streamlit as st

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="SPX | Consulta de Rotas",
    page_icon="🚚",
    layout="centered"
)

# ---------------- SENHA PADRÃO ----------------
SENHA_ADMIN = "LPA2026"

# ---------------- ESTADO DO SITE ----------------
if "status_site" not in st.session_state:
    st.session_state.status_site = "FECHADO"

# ---------------- CABEÇALHO ----------------
st.title("🚚 SPX | Consulta de Rotas")
st.markdown("Consulta disponível **somente após a alocação das rotas**.")

st.divider()

# ---------------- ÁREA ADMIN (SIMPLES) ----------------
st.markdown("### 🔒 Área Administrativa")

senha = st.text_input("Senha administrativa", type="password")

if senha == SENHA_ADMIN:
    st.success("Acesso administrativo liberado")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔓 ABRIR CONSULTA"):
            st.session_state.status_site = "ABERTO"
            st.success("Consulta ABERTA")

    with col2:
        if st.button("🔒 FECHAR CONSULTA"):
            st.session_state.status_site = "FECHADO"
            st.warning("Consulta FECHADA")

elif senha:
    st.error("Senha incorreta")

st.divider()

# ---------------- STATUS ATUAL ----------------
st.markdown(f"### 📌 Status atual: **{st.session_state.status_site}**")

# ---------------- BLOQUEIO DA CONSULTA ----------------
if st.session_state.status_site == "FECHADO":
    st.warning("🚫 Consulta indisponível no momento.")
    st.stop()

# ---------------- CONSULTA (MANTIDA SIMPLES) ----------------
st.markdown("### 🔍 Consulta")

nome = st.text_input("Digite o nome do motorista")

if nome:
    st.info("⚠️ Base de dados ainda não conectada.")
