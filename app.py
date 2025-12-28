
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =========================
# Configuração da página
# =========================
st.set_page_config(
    page_title="Consulta de Rotas",
    layout="centered"
)

st.title("📦 Consulta de Rotas")
st.markdown("Consulta operacional de rotas — base atualizada diariamente.")

# =========================
# Carregar planilha
# =========================
ARQUIVO = "rotas.xlsx"

if not os.path.exists(ARQUIVO):
    st.error("❌ Planilha 'rotas.xlsx' não encontrada na pasta do sistema.")
    st.stop()

df = pd.read_excel(ARQUIVO)

# Padronizar colunas (evita erro humano)
df.columns = df.columns.str.strip().str.lower()

# Mostrar data da última atualização
data_modificacao = os.path.getmtime(ARQUIVO)
data_formatada = datetime.fromtimestamp(data_modificacao).strftime("%d/%m/%Y %H:%M")
st.caption(f"📅 Base atualizada em: {data_formatada}")

# =========================
# Validação mínima
# =========================
colunas_necessarias = {"nome", "placa", "id", "rota", "bairro"}
if not colunas_necessarias.issubset(df.columns):
    st.error("❌ A planilha não está no padrão correto de colunas.")
    st.stop()

# =========================
# Consulta
# =========================
st.divider()
st.subheader("🔎 Buscar rota")

nome = st.text_input("Nome do motorista")

if nome:
    resultado = df[df["nome"].str.lower() == nome.lower()]

    if not resultado.empty:
        st.success("✅ Rota encontrada")
        st.write(f"🚚 **Rota:** {resultado.iloc[0]['rota']}")
        st.write(f"📍 **Bairro:** {resultado.iloc[0]['bairro']}")
    else:
        st.error("❌ Motorista não encontrado. Verifique o nome informado.")
