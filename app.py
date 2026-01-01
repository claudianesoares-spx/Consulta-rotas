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

# ---------------- SECRETS ----------------
segredos = {
    "senha_master": "MASTER2026",
    "senha_operacional": "LPA2026",
    "status_site": "ABERTO",
    "GCP_SERVICE_ACCOUNT": st.secrets.get("GCP_SERVICE_ACCOUNT")
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

    # Google Sheets
    try:
        planilha = conectar_sheets()
        if planilha:
            try:
                aba = planilha.worksheet(ABA_LOGS)
            except gspread.WorksheetNotFound:
                aba = planilha.add_worksheet(title=ABA_LOGS, rows=1000, cols=10)

            df_logs = get_as_dataframe(aba).fillna("")
            df_logs = pd.concat([df_logs, pd.DataFrame([linha])], ignore_index=True)
            set_with_dataframe(aba, df_logs)
    except Exception as e:
        st.warning(f"Erro ao registrar log na planilha: {e}")

# ---------------- LIMPEZA DE LOGS (3 DIAS) ----------------
def limpar_logs():
    planilha = conectar_sheets()
    if planilha:
        try:
            aba = planilha.worksheet(ABA_LOGS)
            df = get_as_dataframe(aba)
            df["Data"] = pd.to_datetime(df["Data"], format="%d/%m/%Y", errors="coerce")
            limite = datetime.now() - timedelta(days=3)
            df = df[df["Data"] >= limite]
            set_with_dataframe(aba, df)
        except:
            pass

limpar_logs()

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
.result-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    margin-bottom: 16px;
}
.result-title {
    font-size: 20px;
    font-weight: 700;
    color: #ff7a00;
    margin-bottom: 12px;
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
def carre
