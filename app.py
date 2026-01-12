import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="SPX | Consulta de Rotas",
    page_icon="🚚",
    layout="centered"
)

# ================= ARQUIVO DE PERSISTÊNCIA =================
CONFIG_FILE = "config.json"

# ================= CONFIG PADRÃO =================
DEFAULT_CONFIG = {
    "status_site": "FECHADO",
    "senha_master": "MASTER2026",
    "historico": []
}

# ================= LOAD / SAVE =================
def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)

config = load_config()

# ================= FUNÇÃO LOG =================
def registrar_acao(usuario, acao):
    config["historico"].append({
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "usuario": usuario,
        "acao": acao
    })
    save_config(config)

# ================= ESTILO =================
st.markdown("""
<style>
.card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    border-left: 6px solid #ff7a00;
    margin-bottom: 16px;
}
.card h4 {
    margin-bottom: 12px;
}
.card p {
    margin: 4px 0;
    font-size: 15px;
}
</style>
""", unsafe_allow_html=True)

# ================= CABEÇALHO =================
st.title("🚚 SPX | Consulta de Rotas")
st.markdown("Consulta disponível **somente após a alocação das rotas**.")
st.divider()

# ================= SIDEBAR / ADMIN =================
with st.sidebar:
    with st.expander("🔒 Área Administrativa", expanded=False):

        senha = st.text_input("Senha", type="password")
        nivel = None

        if senha == config["senha_master"]:
            nivel = "MASTER"
            st.success("Acesso MASTER liberado")

        elif senha == "LPA2026":
            nivel = "ADMIN"
            st.success("Acesso ADMIN liberado")

        elif senha:
            st.error("Senha incorreta")

        if nivel in ["ADMIN", "MASTER"]:
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔓 ABRIR"):
                    config["status_site"] = "ABERTO"
                    registrar_acao(nivel, "ABRIU CONSULTA")
                    st.success("Consulta ABERTA")

            with col2:
                if st.button("🔒 FECHAR"):
                    config["status_site"] = "FECHADO"
                    registrar_acao(nivel, "FECHOU CONSULTA")
                    st.warning("Consulta FECHADA")

        if nivel == "MASTER":
            st.markdown("---")
            nova_senha = st.text_input("Nova senha MASTER", type="password")

            if st.button("Salvar nova senha"):
                if nova_senha:
                    config["senha_master"] = nova_senha
                    registrar_acao("MASTER", "ALTEROU SENHA MASTER")
                    save_config(config)
                    st.success("Senha MASTER atualizada")

            st.markdown("---")
            st.markdown("### 📜 Histórico de ações")

            if config["historico"]:
                for h in reversed(config["historico"]):
                    st.markdown(
                        f"- {h['data']} | **{h['usuario']}** | {h['acao']}"
                    )
            else:
                st.info("Nenhuma ação registrada")

# ================= STATUS ATUAL =================
st.markdown(f"### 📌 Status atual: **{config['status_site']}**")
st.divider()

# ================= BLOQUEIO =================
if config["status_site"] == "FECHADO":
    st.warning("🚫 Consulta indisponível no momento.")
    st.stop()

# ================= CONSULTA SEGURA =================
st.markdown("### 🔍 Consulta de Rotas")

id_motorista = st.text_input("Digite seu ID de motorista")

if id_motorista:
    url = "https://docs.google.com/spreadsheets/d/1F8HC2D8UxRc5R_QBdd-zWu7y6Twqyk3r0NTPN0HCWUI/export?format=xlsx"
    df = pd.read_excel(url)

    # Garantia de comparação correta
    df["ID"] = df["ID"].astype(str)

resultado = df[df["ID"] == id_motorista.strip()]

# ================= MOTORISTA COM ROTA =================
if not resultado.empty:
    for _, row in resultado.iterrows():
        st.markdown(f"""
        <div class="card">
            <h4>🚚 Rota: {row['Rota']}</h4>
            <p>👤 <strong>Motorista:</strong> {row['Nome']}</p>
            <p>🚗 <strong>Placa:</strong> {row['Placa']}</p>
            <p>🏙️ <strong>Cidade:</strong> {row['Cidade']}</p>
            <p>📍 <strong>Bairro:</strong> {row['Bairro']}</p>
        </div>
        """, unsafe_allow_html=True)

    # 🔒 quem já tem rota NÃO vê rotas disponíveis
    st.stop()

# ================= MOTORISTA SEM ROTA =================
st.warning("Nenhuma rota atribuída para este ID.")

st.markdown("### 🚚 Rotas disponíveis no momento")

rotas_disponiveis = df[
    (df["ID"].isna()) | (df["ID"].str.strip() == "")
]

if rotas_disponiveis.empty:
    st.info("No momento não há rotas disponíveis.")
else:
    for _, row in rotas_disponiveis.iterrows():
        st.markdown(f"""
        <div class="card">
            <h4>🚚 Rota disponível: {row['Rota']}</h4>
            <p>🏙️ <strong>Cidade:</strong> {row['Cidade']}</p>
            <p>📍 <strong>Bairro:</strong> {row['Bairro']}</p>
        </div>
        """, unsafe_allow_html=True)


