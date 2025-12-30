import streamlit as st
import pandas as pd
import unicodedata
import re
from datetime import datetime

# ---------------- CONFIGURAÇÃO DA PÁGINA ----------------
st.set_page_config(
    page_title="SPX | Consulta de Rotas",
    layout="centered"
)

# ---------------- FUNÇÕES ----------------
def normalizar_texto(texto):
    if not isinstance(texto, str):
        return ""
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return re.sub(r"\s+", " ", texto)

# ---------------- CARREGAR PLANILHA ----------------
@st.cache_data(ttl=300)
def carregar_planilha():
    try:
        url = "https://docs.google.com/spreadsheets/d/1x4P8sHQ8cdn7tJCDRjPP8qm4aFIKJ1tx/export?format=xlsx"

        # aba principal (consulta)
        df_rotas = pd.read_excel(url, sheet_name=0)

        # aba controle (segunda aba)
        df_controle = pd.read_excel(url, sheet_name=1, header=None)

        status_site = str(df_controle.iloc[0, 0]).strip().upper()

        df_rotas.columns = df_rotas.columns.str.strip().str.lower()

        if "nome" not in df_rotas.columns:
            st.error("❌ A coluna 'nome' não foi encontrada.")
            st.stop()

        df_rotas["nome_normalizado"] = df_rotas["nome"].apply(normalizar_texto)

        return df_rotas, status_site

    except Exception as e:
        st.error(f"❌ Erro ao carregar a planilha: {e}")
        st.stop()

# ---------------- EXECUÇÃO ----------------
df, status_site = carregar_planilha()

# ---------------- TRAVA GLOBAL ----------------
st.title("SPX | Consulta de Rotas")

if status_site != "LIBERADO":
    st.warning("🔒 Consulta temporariamente indisponível. Aguarde a liberação da operação.")
    st.stop()

# ---------------- CABEÇALHO ----------------
st.caption(f"📅 Base atualizada em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ---------------- BUSCA ----------------
st.markdown("### 🔎 Buscar rota")
nome_input = st.text_input("Digite o nome completo do motorista")

if nome_input:
    nome_busca = normalizar_texto(nome_input)

    resultado = df[df["nome_normalizado"].str.contains(nome_busca, na=False)]

    if not resultado.empty:
        qtd = len(resultado)

        if qtd > 1:
            st.success(f"✅ Você tem **{qtd} rotas** hoje")
        else:
            st.success("✅ Você tem **1 rota** hoje")

        colunas_exibir = [c for c in ["rota", "bairro"] if c in resultado.columns]

        st.dataframe(
            resultado[colunas_exibir].reset_index(drop=True),
            use_container_width=True
        )
    else:
        st.warning("⚠️ Nenhuma rota encontrada para esse nome")
