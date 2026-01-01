import streamlit as st

# ---------------- CONFIGURAÇÃO ----------------
st.set_page_config(
    page_title="SPX | Consulta de Rotas",
    page_icon="🚚",
    layout="centered"
)

# ---------------- SENHAS FIXAS ----------------
SENHA_MASTER = "MASTER2026"
SENHA_OPERACIONAL = "OPER2026"

# ---------------- ESTADO ----------------
if "logado" not in st.session_state:
    st.session_state.logado = False

if "perfil" not in st.session_state:
    st.session_state.perfil = None

if "status" not in st.session_state:
    st.session_state.status = "FECHADO"

# ---------------- LOGIN ----------------
st.title("🚚 SPX | Consulta de Rotas")

if not st.session_state.logado:
    senha = st.text_input("Digite sua senha", type="password")

    if st.button("Entrar"):
        if senha == SENHA_MASTER:
            st.session_state.logado = True
            st.session_state.perfil = "MASTER"
            st.rerun()

        elif senha == SENHA_OPERACIONAL:
            st.session_state.logado = True
            st.session_state.perfil = "OPERACIONAL"
            st.rerun()

        else:
            st.error("❌ Senha incorreta")

    st.stop()

# ---------------- ÁREA LOGADA ----------------
st.success(f"Acesso autorizado ({st.session_state.perfil})")

st.divider()
st.subheader("⚙️ Área Administrativa")

st.info(f"Status atual: **{st.session_state.status}**")

col1, col2 = st.columns(2)

with col1:
    if st.button("🟢 ABRIR"):
        st.session_state.status = "ABERTO"
        st.success("Consulta ABERTA")

with col2:
    if st.button("🔴 FECHAR"):
        st.session_state.status = "FECHADO"
        st.warning("Consulta FECHADA")

# ---------------- CONSULTA ----------------
st.divider()
st.subheader("📄 Consulta")

if st.session_state.status == "FECHADO":
    st.error("🚫 Consulta fechada no momento.")
else:
    st.success("✅ Consulta aberta.")
    st.write("Aqui entra a lógica da consulta de rotas.")

# ---------------- LOGOUT ----------------
if st.button("Sair"):
    st.session_state.clear()
    st.rerun()
