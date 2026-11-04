import streamlit as st

from dados_exemplo import gerar_dados_exemplo

st.set_page_config(page_title="Dados", page_icon="📂", layout="wide")
st.title("📂 Dados")

arquivo = st.file_uploader("Envie a base de reclamações", type=["csv", "json", "xml"])

if arquivo is not None:
    st.success(f"Arquivo recebido: **{arquivo.name}** ({arquivo.size / 1_000_000:.1f} MB)")
    st.info("No protótipo o arquivo ainda não é processado. Abaixo, dados de exemplo.")

df = gerar_dados_exemplo()

# Cartões com os números principais da base
total = len(df)
resolvidas = (df["Avaliação Reclamação"] == "Resolvida").sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Reclamações", f"{total:,}".replace(",", "."))
col2.metric("Operadoras", df["Nome Fantasia"].nunique())
col3.metric("Estados", df["UF"].nunique())
col4.metric("Resolvidas", f"{resolvidas / total:.0%}")

st.subheader("Prévia da base")
st.dataframe(df.head(20), width="stretch")

st.subheader("Tratamento aplicado aos dados")
st.markdown(
    """
- Mantém apenas as reclamações contra **operadoras de telecom**.
- Remove as reclamações **não avaliadas** pelo consumidor.
- Remove linhas **duplicadas** e trata **valores vazios**.
- Descarta colunas que entregam a resposta (**Nota do Consumidor** e **Situação**).
"""
)
