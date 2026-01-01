import streamlit as st
import pandas as pd

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="SPX | Consulta de Rotas",
    page_icon="🚚",
    layout="centered"
)

# ---------------- CONFIGURAÇÕES ----------------
SENHA_ADMIN = "LPA2026"
PLANILHA_URL = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=xlsx"

# ---------------- ESTADO DO SITE ----------------
if "status_site" not in st.session_state:
    st.session_state.status_site = "ABERTO"

# ---------------- CARREGAR BASE ----------------
@st.cache_data(ttl=300)
def carregar_base():
    df = pd.read_excel(PLANILHA_URL)

    # normaliza colunas (NUNCA MAIS QUEBRA)
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
    )

    return df.fillna("")

df = carregar_base()

# ---------------- CABEÇALHO ----------------
st.title("🚚 SPX | Consulta de Rotas")
st.markdown("Consulta disponível **somente após a alocação das rotas**.")
st.divider()

# ---------------- ÁREA ADMIN (SIDEBAR) ----------------
with st.sidebar:
    st.markdown("## 🔒 Área Administrativa")
    senha = st.text_input("Senha", type="password")

    if senha == SENHA_ADMIN:
        st.success("Acesso liberado")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🟢 ABRIR CONSULTA"):
                st.session_state.status_site = "ABERTO"

        with col2:
            if st.button("🔴 FECHAR CONSULTA"):
                st.session_state.status_site = "FECHADO"

    elif senha:
        st.error("Senha incorreta")

# ---------------- STATUS ----------------
st.markdown(f"### 📌 Status atual: **{st.session_state.status_site}**")

# ---------------- BLOQUEIO ----------------
if st.session_state.status_site == "FECHADO":
    st.warning("🚫 Consulta indisponível no momento.")
    st.stop()

# ---------------- CONSULTA ----------------
st.markdown("### 🔍 Consulta de Rotas")

nome = st.text_input("Digite o **nome completo ou parcial** do motorista:")

if nome:
    resultado = df[df["MOTORISTA"].str.contains(nome, case=False, na=False)]

    if resultado.empty:
        st.warning("❌ Nenhuma rota atribuída.")
    else:
        for _, row in resultado.iterrows():
            st.markdown(f"""
            <div style="
                background:white;
                padding:20px;
                border-radius:14px;
                border:1px solid #e5e7eb;
                margin-bottom:16px;
            ">
                <h4 style="color:#ff7a00;">🚚 Rota: {row['ROTA']}</h4>
                <strong>👤 Motorista:</strong> {row['MOTORISTA']}<br>
                <strong>🚗 Placa:</strong> {row['PLACA']}<br>
                <strong>🏙️ Cidade:</strong> {row['CIDADE']}<br>
                <strong>📍 Bairro:</strong> {row['BAIRRO']}
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Digite um nome para consultar a rota.")
