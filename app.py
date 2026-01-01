import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="SPX | Consulta de Rotas",
    page_icon="🚚",
    layout="centered"
)

# ---------------- ARQUIVOS ----------------
CONFIG_FILE = "config.json"

# ---------------- CONFIG INICIAL ----------------
def carregar_config():
    if not os.path.exists(CONFIG_FILE):
        config = {
            "senha_master": "MASTER2026",
            "senha_operacional": "LPA2026",
            "status_site": "ABERTO"
        }
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
    else:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    return config

def salvar_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

config = carregar_config()

# ---------------- URL PLANILHA ----------------
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=xlsx"

# ---------------- CARREGA PLANILHA DE ROTAS ----------------
@st.cache_data(ttl=300)
def carregar_base():
    df = pd.read_excel(URL_PLANILHA)
    df.columns = df.columns.str.strip()
    df = df.fillna("")
    return df

df = carregar_base()

# ---------------- AUTENTICAÇÃO GOOGLE SHEETS ----------------
# Substitua 'service_account.json' pelo seu arquivo JSON da conta de serviço
scope = ["https://spreadsheets.google.com/feeds", 
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)
sheet_logs = client.open_by_url(URL_PLANILHA).worksheet("Logs")

# ---------------- FUNÇÃO DE LOG ONLINE ----------------
def registrar_log(acao, nivel):
    sheet_logs.append_row([
        datetime.now().strftime("%d/%m/%Y"),
        datetime.now().strftime("%H:%M:%S"),
        acao,
        nivel
    ])

# ---------------- LIMPEZA AUTOMÁTICA DE LOGS (3 DIAS) ----------------
def limpar_logs_3_dias():
    all_logs = sheet_logs.get_all_records()
    if not all_logs:
        return
    df_logs = pd.DataFrame(all_logs)
    df_logs['Data'] = pd.to_datetime(df_logs['Data'], format="%d/%m/%Y")
    limite = datetime.now() - timedelta(days=3)
    df_limpo = df_logs[df_logs['Data'] >= limite]
    # Limpa aba e rescreve apenas logs recentes
    sheet_logs.clear()
    sheet_logs.append_row(["Data", "Hora", "Ação", "Acesso"])  # cabeçalho
    for _, row in df_limpo.iterrows():
        sheet_logs.append_row([row['Data'].strftime("%d/%m/%Y"), row['Hora'], row['Ação'], row['Acesso']])

limpar_logs_3_dias()

# ---------------- ESTILO ----------------
st.markdown("""
<style>
.stApp { background-color: #f6f7f9; }
.header-card {
    background: white;
    padding: 24px 28px;
    border-radius: 16px;
    border-left: 6px solid #ff7a00;
    box-shadow: 0 6px 18px rgba(0,0,0,0.05);
    margin-bottom: 30px;
}
.header-title { font-size: 32px; font-weight: 700; color: #1f2937; }
.header-sub { font-size: 14px; color: #6b7280; margin-top: 4px; }
.header-info { margin-top: 14px; font-size: 15px; color: #374151; }
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
    <div class="header-title">🚚 SPX | Consulta de Rotas</div>
    <div class="header-sub">Shopee Express • Operação Logística</div>
    <div class="header-info">
        Consulta disponível <strong>somente após a alocação das rotas</strong>.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- LOGIN E SENHAS TEMPORÁRIAS ----------------
temporary_passwords = {}  # {senha_temp: expira_timestamp}

with st.sidebar:
    st.markdown("## 🔒 Área Administrativa")
    senha = st.text_input("Senha", type="password")

    nivel = None
    current_time = time.time()

    # Remove temporárias expiradas
    expired = [k for k, v in temporary_passwords.items() if v < current_time]
    for k in expired:
        del temporary_passwords[k]

    # Verifica senha
    if senha == config["senha_master"]:
        nivel = "MASTER"
    elif senha == config["senha_operacional"]:
        nivel = "OPERACIONAL"
    elif senha in temporary_passwords:
        nivel = "TEMP"

    if nivel:
        st.success(f"Acesso {nivel}")
        st.markdown(f"**🚦 Status:** `{config['status_site']}`")

        col1, col2 = st.columns(2)
        if col1.button("🟢 Abrir"):
            config["status_site"] = "ABERTO"
            salvar_config(config)
            registrar_log("Consulta ABERTA", nivel)
            st.rerun()
        if col2.button("🔴 Fechar"):
            config["status_site"] = "FECHADO"
            salvar_config(config)
            registrar_log("Consulta FECHADA", nivel)
            st.rerun()

        # ---------------- MASTER ONLY ----------------
        if nivel == "MASTER":
            st.markdown("---")
            st.markdown("### 🔑 Gerenciar Senhas")
            nova_op = st.text_input("Nova senha operacional")
            if st.button("Salvar senha operacional") and nova_op:
                config["senha_operacional"] = nova_op
                salvar_config(config)
                registrar_log("Senha operacional alterada", nivel)
                st.success("Senha operacional atualizada")
            nova_master = st.text_input("Nova senha master")
            if st.button("Salvar senha master") and nova_master:
                config["senha_master"] = nova_master
                salvar_config(config)
                registrar_log("Senha master alterada", nivel)
                st.success("Senha master atualizada")

            st.markdown("---")
            st.markdown("### 🔑 Criar senha temporária")
            temp_senha = st.text_input("Senha temporária")
            temp_dur = st.number_input("Duração (minutos)", min_value=1, max_value=1440, value=30)
            if st.button("Gerar senha temporária") and temp_senha:
                temporary_passwords[temp_senha] = time.time() + temp_dur * 60
                registrar_log(f"Senha temporária '{temp_senha}' criada por {temp_dur} min", nivel)
                st.success(f"Senha temporária '{temp_senha}' criada por {temp_dur} min.")

            st.markdown("---")
            st.markdown("### 📜 Histórico")
            st.dataframe(pd.DataFrame(sheet_logs.get_all_records()), use_container_width=True)

    elif senha:
        st.error("Senha incorreta")

# ---------------- BLOQUEIO USUÁRIO COMUM ----------------
if config["status_site"] == "FECHADO":
    st.warning("🚫 Consulta temporariamente indisponível.")
    st.stop()

# ---------------- BUSCA ----------------
nome_busca = st.text_input("Digite o **nome completo ou parcial** do motorista:")

if nome_busca:
    resultado = df[df["Nome"].str.contains(nome_busca, case=False, na=False)]
    if resultado.empty:
        st.warning("❌ Nenhuma rota atribuída.")
    else:
        for _, row in resultado.iterrows():
            st.markdown(f"""
            <div class="result-card">
                <div class="result-title">🚚 Rota {row['Rota']}</div>
                <strong>👤 Motorista:</strong> {row['Nome']}<br>
                <strong>🚗 Placa:</strong> {row['Placa']}<br>
                <strong>🏙️ Cidade:</strong> {row['Cidade']}<br>
                <strong>📍 Bairro:</strong> {row['Bairro']}
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Digite um nome para consultar a rota.")
