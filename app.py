import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="SPX | Consulta de Rotas",
    page_icon="🚚",
    layout="centered"
)

# ---------------- CONSTANTES ----------------
LOG_FILE = "logs.csv"
ABA_LOGS = "Logs"
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI"

# ---------------- TEMPORÁRIO: SENHA HARDCODED ----------------
# Apenas para desbloquear acesso; depois substitua por st.secrets
segredos = {
    "senha_master": "MASTER2026",
    "senha_operacional": "",
    "status_site": "ABERTO",
    "GCP_SERVICE_ACCOUNT": None  # Ainda precisa configurar o JSON depois
}

# ---------------- GOOGLE SHEETS ----------------
def conectar_sheets():
    if not segredos["GCP_SERVICE_ACCOUNT"]:
        st.warning("Service Account não configurado, logs na planilha não funcionarão.")
        return None
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            segredos["GCP_SERVICE_ACCOUNT"], scope
        )
        client = gspread.authorize(creds)
        return client.open_by_url(URL_PLANILHA)
    except Exception as e:
        st.warning(f"Erro ao conectar com Google Sheets: {e}")
        return None

# ---------------- LOGS ----------------
def registrar_log(acao, nivel):
    agora = datetime.now()
    linha = {
        "Data": agora.strftime("%d/%m/%Y"),
        "Hora": agora.strftime("%H:%M:%S"),
        "Ação": acao,
        "Acesso": nivel
    }

    # Backup local
    if not os.path.exists(LOG_FILE):
        pd.DataFrame([linha]).to_csv(LOG_FILE, index=False)
    else:
        pd.DataFrame([linha]).to_csv(LOG_FILE, mode="a", header=False, index=False)

# ---------------- ESTILO ----------------
st.markdown("""
<style>
.stApp { background-color: #f6f7f9; }
.header-card {
    background: white;
    padding: 24px;
    border-radius: 16px;
    border-left: 6px solid #ff7a00;
}
</style>
""", unsafe_allow_html=True)

# ---------------- CABEÇALHO ----------------
st.markdown("""
<div class="header-card">
<h2>🚚 SPX | Consulta de Rotas</h2>
<p>Consulta disponível somente após a alocação.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- BASE ----------------
@st.cache_data(ttl=300)
def carregar_base():
    try:
        df = pd.read_excel(f"{URL_PLANILHA}/export?format=xlsx")
        df.columns = df.columns.str.strip()
        return df.fillna("")
    except:
        st.warning("Não foi possível carregar a planilha, verifique a URL.")
        return pd.DataFrame()

df = carregar_base()

# ---------------- LOGIN ----------------
with st.sidebar:
    st.markdown("## 🔒 Área Administrativa")
    senha = st.text_input("Senha", type="password")

    nivel = None
    if senha == segredos["senha_master"]:
        nivel = "MASTER"
    elif senha == segredos["senha_operacional"] and segredos["senha_operacional"]:
        nivel = "OPERACIONAL"

    if nivel:
        st.success(f"Acesso {nivel}")
        registrar_log("Login realizado", nivel)

        if nivel == "MASTER":
            st.markdown("### 📜 Histórico")
            st.info("Logs na planilha não funcionam nesta versão temporária.")
    elif senha:
        st.error("Senha incorreta")

# ---------------- BLOQUEIO ----------------
if segredos["status_site"] == "FECHADO":
    st.warning("Consulta indisponível.")
    st.stop()

# ---------------- BUSCA ----------------
nome = st.text_input("Digite o nome do motorista")

if nome:
    res = df[df["Nome"].str.contains(nome, case=False, na=False)]
    if res.empty:
        st.warning("❌ Nenhuma rota atribuída.")
    else:
        for _, r in res.iterrows():
            st.success(f"🚚 Rota {r['Rota']} | {r['Nome']} | {r['Placa']}")
