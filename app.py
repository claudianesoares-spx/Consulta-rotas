import streamlit as st
import pandas as pd

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="SPX | Consulta de Rotas",
    page_icon="🚚",
    layout="centered"
)

# ---------------- ESTILO (CORES / LAYOUT) ----------------
st.markdown("""
<style>
    body {
        background-color: #f7f7f7;
    }
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    .titulo {
        color: #FF6A00;
        font-weight: 700;
    }
    .sub {
        color: #555;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- TÍTULO ----------------
st.markdown("<h2 class='titulo'>🚚 SPX | Consulta de Rotas</h2>", unsafe_allow_html=True)
st.markdown("<p class='sub'>Consulta disponível somente após a alocação das rotas</p>", unsafe_allow_html=True)

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

    df.columns = df.columns.str.strip()
    df["Cidade"] = df["Cidade"].fillna("").astype(str)

    return df

try:
    df = carregar_base()
except Exception as e:
    st.error(f"Erro ao carregar a base: {e}")
    st.stop()

# ---------------- SIDEBAR ADMIN ----------------
with st.sidebar:
    st.markdown("### 🔐 Área Administrativa")
    senha = st.text_input("Senha admin", type="password")

    if senha == "LPA2026":
        st.success("Admin ativo")

        if st.button("🔄 Limpar cache"):
            st.cache_data.clear()
            st.success("Cache limpo! Atualize a página.")

        st.markdown("—")
        st.write("Colunas carregadas:")
        st.write(df.columns.tolist())

    elif senha:
        st.error("Senha incorreta")

# ---------------- CONFERÊNCIA DAS COLUNAS ----------------
colunas_necessarias = ["Placa", "Nome", "Bairro", "Rota", "Cidade"]

for col in colunas_necessarias:
    if col not in df.columns:
        st.error(f"Coluna obrigatória não encontrada: {col}")
        st.stop()

# ---------------- CONSULTA ----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)

nome_busca = st.text_input(
    "Digite o nome completo ou parcial do motorista:",
    placeholder="Ex: Adriana Cardoso"
)

if nome_busca:
    resultado = df[df["Nome"].str.contains(nome_busca, case=False, na=False)]

    if resultado.empty:
        st.warning("❌ Nenhuma rota encontrada para este nome.")
    else:
        resultado = resultado.copy()
        resultado["Cidade"] = resultado["Cidade"].replace("", "Não informado")

        st.success(f"{len(resultado)} rota(s) encontrada(s):")

        st.dataframe(
            resultado[["Placa", "Nome", "Cidade", "Bairro", "Rota"]],
            use_containe_
