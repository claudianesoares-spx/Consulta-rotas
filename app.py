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

# ---------------- SEGREDOS (STREAMLIT CLOUD) ----------------
def carregar_segredos():
    if "senha_master" not in st.secrets:
        st.error("Senha master não configurada nos Secrets.")
        st.stop()
    return {
        "senha_master": st.secrets["senha_master"],
        "senha_operacional": st.secrets.get("senha_operacional", ""),
        "status_site": st.secrets.get("status_site", "ABERTO")
    }

segredos = carregar_segredos()

# ---------------- GOOGLE SHEETS ----------------
def conectar_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["GCP_SERVICE_ACCOUNT"],
        scope
    )
    client = gspread.authorize(creds)
    return client.open_by_url(URL_PLANILHA)

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
        try:
            aba = planilha.worksheet(ABA_LOGS)
        except gspread.WorksheetNotFound:
            aba = planilha.add_worksheet(title=ABA_LOGS, rows=1000, cols=10)

        df = get_as_dataframe(aba).fillna("")
        df = pd.concat([df, pd.DataFrame([linha])], ignore_index=True)
        set_with_dataframe(aba, df)
    except Exception as e:
        st.warning(f"Erro ao registrar log na planilha: {e}")

# ---------------- LIMPEZA DE LOGS (3 DIAS) ----------------
def limpar_logs():
    try:
        planilha = conectar_sheets()
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
    df = pd.read_excel(f"{URL_PLANILHA}/export?format=xlsx")
    df.columns = df.columns.str.strip()
    return df.fillna("")

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
            try:
                planilha = conectar_sheets()
                aba = planilha.worksheet(ABA_LOGS)
                st.dataframe(get_as_dataframe(aba), use_container_width=True)
            except:
                st.info("Nenhum log disponível")
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

