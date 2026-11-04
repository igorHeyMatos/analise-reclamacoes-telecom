import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

import api

AZUL, CINZA, LARANJA = "#0b6e8f", "#9fb4c3", "#c2410c"
sns.set_theme(style="whitegrid")


def grafico_barras(nomes, valores, cores, formato="{:,.0f}"):
    """Barras horizontais com o valor escrito ao lado de cada barra."""
    rotulos = [textwrap.shorten(nome, 48, placeholder="...") for nome in nomes]
    fig, ax = plt.subplots(figsize=(7, 0.45 * len(nomes) + 0.6))
    barras = ax.barh(rotulos, valores, color=cores)
    ax.bar_label(barras, labels=[formato.format(v).replace(",", ".") for v in valores], padding=3, fontsize=9)
    ax.invert_yaxis()  # o maior fica em cima
    ax.set_xlim(0, max(valores) * 1.15)
    ax.set_xticks([])
    ax.grid(False)
    sns.despine(left=True, bottom=True)
    return fig


def mostrar_analise(resumo):
    total = resumo["total"]
    operadoras = pd.Series(resumo["operadoras"])
    resolucao = pd.Series(resumo["resolucao"])

    st.title("Análise das reclamações")
    st.caption(f"{total:,} reclamações contra operadoras de telecom avaliadas pelo consumidor.".replace(",", "."))

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Reclamações analisadas", f"{total:,}".replace(",", "."))
    k2.metric("Foram resolvidas", f"{resumo['resolvidas']:.0%}")
    k3.metric("Ligadas a cancelamento", f"{resumo['cancelamento'] / total:.0%}")
    k4.metric("Operadora mais reclamada", operadoras.index[0], f"{operadoras.iloc[0] / total:.0%} do total", delta_color="off")

    st.header("Motivos das reclamações", divider="gray")
    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Quais problemas geram mais reclamações?")
        problemas = resumo["problemas"]
        st.caption("Em laranja, os problemas ligados a cancelamento.")
        st.pyplot(grafico_barras([p["nome"] for p in problemas], [p["quantidade"] for p in problemas],
                                 [LARANJA if p["cancelamento"] else CINZA for p in problemas]))
    with col2:
        st.subheader("Quanto o cancelamento pesa no total?")
        cancelamento = resumo["cancelamento"]
        st.caption(f"{cancelamento:,} de {total:,} reclamações citam cancelamento.".replace(",", "."))
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.pie([cancelamento, total - cancelamento], labels=["Cancelamento", "Demais motivos"],
               colors=[LARANJA, CINZA], autopct="%1.0f%%", startangle=90, wedgeprops={"width": 0.45})
        st.pyplot(fig)

    st.header("Operadoras", divider="gray")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Quais operadoras recebem mais reclamações?")
        st.caption(f"{operadoras.index[0]} concentra {operadoras.iloc[0] / total:.0%} das reclamações.")
        st.pyplot(grafico_barras(operadoras.index, operadoras.values,
                                 [AZUL] + [CINZA] * (len(operadoras) - 1)))
    with col2:
        st.subheader("Qual operadora resolve mais as reclamações?")
        st.caption(f"{resolucao.index[0]} resolve {resolucao.iloc[0]:.0%}; {resolucao.index[-1]} resolve {resolucao.iloc[-1]:.0%}.")
        st.pyplot(grafico_barras(resolucao.index, resolucao.values,
                                 [AZUL] + [CINZA] * (len(resolucao) - 1), formato="{:.0%}"))

    st.header("Onde e quem reclama", divider="gray")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Em quais estados há mais reclamações?")
        estados = pd.DataFrame(resumo["estados"])
        st.caption(f"{estados.iloc[0]['UF']} lidera com {estados.iloc[0]['quantidade']:,} reclamações. "
                   "O tamanho do círculo mostra a quantidade.".replace(",", "."))
        # Raio do círculo em metros: um mínimo de 30 km mais um valor proporcional às reclamações
        estados["raio"] = 30000 + estados["quantidade"] / estados["quantidade"].max() * 250000
        st.map(estados, latitude="lat", longitude="lon", size="raio", color="#0b6e8f99")
    with col2:
        st.subheader("Qual faixa etária mais reclama?")
        faixas = pd.Series(resumo["faixas"])
        st.caption(f"A faixa de {faixas.idxmax()} faz {faixas.max() / total:.0%} das reclamações.")
        st.pyplot(grafico_barras(faixas.index, faixas.values,
                                 [AZUL if v == faixas.max() else CINZA for v in faixas.values]))


status, resumo = api.resumo()
if status == 200:
    mostrar_analise(resumo)
else:
    st.info("Envie uma base no passo 1 para ver a análise.")
