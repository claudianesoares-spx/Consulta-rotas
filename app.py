import streamlit as st
import pandas as pd

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="SPX | Consulta de Rotas",
    page_icon="🚚",
    layout="centered"
)

# ---------------- ESTILO / IDENTIDADE SPX ----------------
st.markdown("""
<style>
/* Fundo geral */
.main {
    background-color: #f7f8fa;
}

/* Títulos */
h1, h2, h3 {
    color: #0f172a;
    font-weight: 700;
}

/* Campo de texto */
input {
    border-radius: 10px !important;
    border: 1px solid #e5e7eb !important;
}

/* Alerts */
.stAlert-success {
    background-color: #e7f6ec;
    border-left: 6px solid #16a34a;
}

.stAlert-warning {
    background-color: #fff7ed;
    border-left: 6px solid #f97316;
}

.stAlert-info {
    background-color: #eff6ff;
    border-left: 6px solid #2563eb;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
}

section[data-testid="stSidebar"] * {
    color: white;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR / ADMIN ----------------
with st.sidebar:
    st.markdown("### 🔐 Área Administrativa")
    senha = st.text_input("Senha admin", type="password")

    if senha == "LPA2026":
        st.success("Acesso liberado")
    elif senha:
        st.error("Senha incorreta")

# ---------------- TÍTULO ----------------
st.markdown("# 🚚 SPX | Consulta de Rotas")
st.markdown("Consulta disponível **somente após a alocação das rotas**.")

# ---------------- LINK DA PLANILHA ----------------
URL = "https://docs.google.com/spreadsheets/d/1x4P8sHQ8cdn7tJCDRjPP8qm4aFIKJ1tx/export?format=xlsx"

# ---------------- CARREGAMENTO DA BASE ----------------
@st.cache_data
def carregar_base():
    df = pd.read_excel(
        URL,
        sheet_name="CONSULTA ROTAS",
        dtype=str
    )

    # Limpa nomes das colunas
    df.columns = df.columns.str.strip()

    # Garante colunas como texto
    for col in ["Placa", "Nome", "Bairro", "Rota", "Cidade"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str)

    return df

try:
    df = carregar_base()
except Exception as e:
    st.error(f"Erro ao carregar a base: {e}")
    st.stop()

# ---------------- CONFERÊNCIA DAS COLUNAS ----------------
colunas_necessarias = ["Placa", "Nome", "Bairro", "Rota", "Cidade"]

for col in colunas_necessarias:
    if col not in df.columns:
        st.error(f"Coluna obrigatória não encontrada: {col}")
        st.stop()

# ---------------- CAMPO DE BUSCA ----------------
nome_busca = st.text_input(
    "Digite o nome completo ou parcial do motorista:",
    placeholder="Ex: Adriana Cardoso"
)

# ---------------- RESULTADO ----------------
if nome_busca:
    resultado = (
        df[df["Nome"].str.contains(nome_busca, case=False, na=False)]
        .reset_index(drop=True)  # REMOVE O ÍNDICE (ex: 120)
    )

    if resultado.empty:
        st.warning("❌ Nenhuma rota encontrada para este nome.")
    else:
        st.success(f"{len(resultado)} rota(s) encontrada(s):")

        st.dataframe(
            resultado[["Placa", "Nome", "Bairro", "Rota", "Cidade"]],
            use_container_width=True
        )
else:
    st.info("Digite um nome para consultar a rota.")
