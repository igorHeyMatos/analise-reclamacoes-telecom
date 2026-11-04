from pathlib import Path

import pandas as pd
import streamlit as st

import api

BASE_EXEMPLO = Path(__file__).resolve().parents[2] / "dados" / "exemplo" / "reclamacoes_exemplo_2026-09.csv"


def enviar(nome, conteudo):
    with st.spinner("Lendo e tratando a base..."):
        status, resposta = api.enviar_base(nome, conteudo)
    if status != 201:
        st.error(resposta["erro"])
        return
    st.session_state["envio"] = resposta


st.title("Enviar a base de reclamações")
st.caption("Arquivo mensal do consumidor.gov.br em .csv, .json ou .xml. Uma base nova substitui a anterior.")

arquivo = st.file_uploader("Arquivo da base", type=["csv", "json", "xml"])
col1, col2 = st.columns([1, 4])
if col1.button("Enviar e tratar", type="primary", disabled=arquivo is None):
    enviar(arquivo.name, arquivo.getvalue())
if col2.button("Usar a base de exemplo"):
    enviar(BASE_EXEMPLO.name, BASE_EXEMPLO.read_bytes())

envio = st.session_state.get("envio")
if envio is None:
    st.info("Nenhuma base enviada nesta sessão.")
else:
    st.success(f"Base **{envio['arquivo']}** recebida e tratada.")
    col_etapas, col_previa = st.columns([1, 2])
    with col_etapas:
        st.subheader("Tratamento dos dados")
        st.dataframe(pd.DataFrame(envio["etapas"]).rename(columns={"etapa": "Etapa", "linhas": "Linhas"}),
                     hide_index=True, width="stretch")
    with col_previa:
        st.subheader("Prévia dos dados tratados")
        st.dataframe(pd.DataFrame(envio["previa"]), hide_index=True, width="stretch")
