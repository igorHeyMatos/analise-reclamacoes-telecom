"""Funções que o front-end usa para conversar com o back-end (Flask)."""
import requests
import streamlit as st

URL_BACKEND = "http://localhost:5000"


def chamar(metodo, rota, **kwargs):
    """Faz o pedido ao back-end. Se ele estiver desligado, avisa e para a página."""
    try:
        resposta = requests.request(metodo, URL_BACKEND + rota, timeout=300, **kwargs)
    except requests.ConnectionError:
        st.error("O back-end está desligado. Inicie com: python backend/app.py")
        st.stop()
    return resposta.status_code, resposta.json()


def status():
    return chamar("GET", "/status")[1]


def enviar_base(nome, conteudo):
    return chamar("POST", "/dados", files={"arquivo": (nome, conteudo)})


def resumo():
    return chamar("GET", "/dados/resumo")


def treinar(classificador, parametro, tamanho_teste):
    return chamar("POST", "/modelo/treinar", json={
        "classificador": classificador, "parametro": parametro, "tamanho_teste": tamanho_teste})


def historico():
    return chamar("GET", "/modelo/historico")[1]


def prever(reclamacao):
    return chamar("POST", "/modelo/prever", json=reclamacao)
