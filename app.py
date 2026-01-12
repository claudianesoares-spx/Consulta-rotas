import streamlit as st
import pandas as pd

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Consulta de Rotas",
    page_icon="🚚",
    layout="wide"
)

st.title("🔍 Consulta de Rotas")
st.write("Digite seu ID de motorista para consultar suas rotas")

# =========================
# CARREGAMENTO DA PLANILHA
# =========================
@st.cache_data
def carregar_dados():
    url = "COLE_AQUI_O_LINK_CSV_DA_PLANILHA"
    df = pd.read_csv(url)

    # Garantir que ID seja string
    df["ID"] = df["ID"].astype(str).str.strip()

    return df

df = carregar_dados()

# =========================
# INPUT DO MOTORISTA
# =========================
id_motorista = st.text_input("Digite seu ID de motorista")

# =========================
# CONSULTA DE ROTAS DO DRIVER
# =========================
if id_motorista:
    resultado = df[df["ID"] == id_motorista.strip()]

    if resultado.empty:
        st.info("ℹ️ Nenhuma rota atribuída ao seu ID.")
    else:
        st.subheader("🚚 Suas rotas")
        for _, row in resultado.iterrows():
            st.markdown(f"""
            <div style="border:1px solid #ddd;padding:15px;border-radius:10px;margin-bottom:10px;">
                <h4>🚚 Rota: {row['Rota']}</h4>
                <p>👤 <strong>Motorista:</strong> {row['Nome']}</p>
                <p>🚗 <strong>Placa:</strong> {row['Placa']}</p>
                <p>🏙️ <strong>Cidade:</strong> {row['Cidade']}</p>
                <p>📍 <strong>Bairro:</strong> {row['Bairro']}</p>
            </div>
            """, unsafe_allow_html=True)

# =========================
# ROTAS DISPONÍVEIS
# =========================
st.markdown("---")
st.subheader("📦 Rotas disponíveis")

rotas_disponiveis = df[
    df["ID"].isna()
    | (df["ID"] == "")
    | (df["ID"].str.lower() == "nan")
    | (df["ID"] == "-")
]

if rotas_disponiveis.empty:
    st.warning("🚫 No momento não há rotas disponíveis.")
else:
    for _, row in rotas_disponiveis.iterrows():
        st.markdown(f"""
        <div style="border:1px dashed #ccc;padding:15px;border-radius:10px;margin-bottom:10px;">
            <p>🏙️ <strong>Cidade:</strong> {row['Cidade']}</p>
            <p>📍 <strong>Bairro:</strong> {row['Bairro']}</p>
        </div>
        """, unsafe_allow_html=True)
