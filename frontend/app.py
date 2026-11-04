"""Ponto de entrada do front-end: menu com os 3 passos e o status na barra lateral."""
import streamlit as st

import api

st.set_page_config(page_title="Reclamações Telecom", page_icon="📞", layout="wide")

paginas = st.navigation([
    st.Page("paginas/dados.py", title="1. Dados", default=True),
    st.Page("paginas/analise.py", title="2. Análise"),
    st.Page("paginas/modelo.py", title="3. Modelo e previsão"),
])


def mostrar_status():
    situacao = api.status()
    with st.sidebar:
        st.caption("Base atual")
        st.write(f"**{situacao['base'] or 'nenhuma'}**")
        st.caption("Modelo")
        if situacao["base_do_modelo"] is None:
            st.warning("Não treinado")
        elif situacao["base_do_modelo"] != situacao["base"]:
            st.warning("Treinado com outra base: retreine")
        else:
            st.success("Treinado com a base atual")


# O status é desenhado depois da página, para já mostrar a base e o modelo que ela acabou de mudar
paginas.run()
mostrar_status()
