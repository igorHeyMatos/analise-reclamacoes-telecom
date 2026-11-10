import textwrap

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

import api

VERDE, LARANJA, CINZA = "#15803d", "#c2410c", "#9fb4c3"
NOMES = {"arvore": "Árvore de Decisão", "logistica": "Regressão Logística"}
ROTULOS = {"Nome Fantasia": "Operadora", "Faixa Etária": "Faixa etária", "Como Comprou Contratou": "Como contratou",
           "Procurou Empresa": "Procurou a empresa antes?", "UF": "Estado (UF)"}
sns.set_theme(style="whitegrid")


def numero(n):
    """Número com ponto de milhar, como em português: 16.500."""
    return f"{n:,}".replace(",", ".")


@st.cache_data(show_spinner="Carregando as previsões...")
def carregar_previsoes(treinado_em):
    """Busca as previsões no back-end. O cache só busca de novo quando há um treino novo (treinado_em muda)."""
    return api.previsoes()


def grafico_barras(nomes, valores, cores, linha_50=False):
    """Barras horizontais com a porcentagem escrita ao lado de cada barra."""
    rotulos = [textwrap.shorten(str(nome), 40, placeholder="...") for nome in nomes]
    fig, ax = plt.subplots(figsize=(6, 0.4 * len(nomes) + 0.6))
    barras = ax.barh(rotulos, valores, color=cores)
    ax.bar_label(barras, labels=[f"{v:.0%}" for v in valores], padding=3, fontsize=9)
    ax.tick_params(axis="y", labelsize=9)
    if linha_50:
        ax.axvline(0.5, color="gray", linestyle="--", linewidth=1)  # a partir de 50%: deve ser resolvida
    ax.invert_yaxis()
    ax.set_xlim(0, 1.1)
    ax.set_xticks([])
    ax.grid(False)
    sns.despine(left=True, bottom=True)
    return fig


def mostrar_confianca(treino, total):
    st.header("1. Quanto confiar nestas previsões", divider="gray")
    st.caption(f"Métricas do último treino feito na tela 3: {NOMES[treino['classificador']]} "
               f"({treino['parametro']}), treinado com {treino['base']}.")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Acurácia equilibrada", f"{treino['equilibrada_teste']:.1%}",
              f"{treino['equilibrada_teste'] - treino['equilibrada_baseline']:+.1%} sobre o baseline")
    k2.metric("Acerta as que serão resolvidas", f"{treino['acerto_resolvidas']:.0%}")
    k3.metric("Encontra as que não serão", f"{treino['acerto_nao_resolvidas']:.0%}")
    k4.metric("Reclamações previstas", numero(total), "ainda sem avaliação", delta_color="off")


def mostrar_resultado(prev, carac):
    st.header("2. O que deve acontecer com as reclamações em aberto", divider="gray")
    total = len(prev)
    resolvidas = (prev["previsao"] == "Resolvida").sum()
    em_risco = total - resolvidas
    # As 3 características com maior e com menor chance média explicam o resultado
    altas = ", ".join(carac.nlargest(3, "chance_media")["caracteristica"])
    baixas = ", ".join(carac.nsmallest(3, "chance_media")["caracteristica"])

    col_grafico, col_texto = st.columns([1, 2])
    with col_grafico:
        fig, ax = plt.subplots(figsize=(3.5, 3.5))
        ax.pie([resolvidas, em_risco], colors=[VERDE, LARANJA], startangle=90, wedgeprops={"width": 0.4})
        ax.text(0, 0, f"{resolvidas / total:.0%}", ha="center", va="center", fontsize=22, fontweight="bold")
        st.pyplot(fig)
    with col_texto:
        st.success(f"**Devem ser resolvidas: {numero(resolvidas)} ({resolvidas / total:.0%})**  \n"
                   f"O modelo dá chance alta para reclamações com: {altas}.", icon="✅")
        st.warning(f"**Em risco de não ser resolvidas: {numero(em_risco)} ({em_risco / total:.0%})**  \n"
                   f"O modelo dá chance baixa para reclamações com: {baixas}.", icon="⚠️")


def mostrar_porque(carac):
    st.header("3. Por que o modelo decide assim", divider="gray")
    st.caption("Chance média que o modelo previu para as reclamações com cada característica "
               "(só características com pelo menos 20 reclamações).")
    col_ajuda, col_atrapalha = st.columns(2)
    with col_ajuda:
        st.subheader("O que mais ajuda a resolver")
        altas = carac.nlargest(7, "chance_media")
        st.pyplot(grafico_barras(altas["caracteristica"], altas["chance_media"], VERDE))
    with col_atrapalha:
        st.subheader("O que mais atrapalha")
        baixas = carac.nsmallest(7, "chance_media")
        st.pyplot(grafico_barras(baixas["caracteristica"], baixas["chance_media"], LARANJA))


def mostrar_cenarios(prev):
    st.header("4. Comparar cenários", divider="gray")
    st.caption("Escolha uma situação e veja a previsão para as principais operadoras ao mesmo tempo.")
    c1, c2, c3 = st.columns(3)
    problema = c1.selectbox("Problema", prev["Problema"].value_counts().index, key="cenario_problema")
    uf = c2.selectbox("Estado (UF)", prev["UF"].value_counts().index, key="cenario_uf")
    procurou = c3.selectbox("Procurou a empresa antes?", ["S", "N"], key="cenario_procurou")

    codigo, resposta = api.cenarios(problema, uf, procurou)
    if codigo != 200:
        st.error(resposta["erro"])
        return
    resultado = pd.DataFrame(resposta)
    col_grafico, col_nota = st.columns([2, 1])
    with col_grafico:
        st.subheader(f"Chance de resolução em {uf}, por operadora")
        cores = [VERDE if c >= 0.5 else LARANJA for c in resultado["chance_resolvida"]]
        st.pyplot(grafico_barras(resultado["Nome Fantasia"], resultado["chance_resolvida"], cores, linha_50=True))
    with col_nota:
        st.caption("Verde: deve ser resolvida (50% ou mais). Laranja: em risco. A linha tracejada marca 50%.")
        if resultado["chance_resolvida"].nunique() == 1:
            # A árvore decide por perguntas: se nenhuma pergunta olha a operadora, todas caem na mesma folha
            st.info("Todas as operadoras receberam a mesma chance: nesta situação o modelo decide só pelo "
                    "problema, sem olhar a operadora. Isso é comum na Árvore de Decisão. Para comparar as "
                    "operadoras, treine a Regressão Logística na tela 3.")


def mostrar_lista(prev):
    st.header("5. Lista das previsões", divider="gray")
    c1, c2 = st.columns(2)
    operadora = c1.selectbox("Operadora", ["Todas"] + list(prev["Nome Fantasia"].value_counts().index))
    mostrar = c2.selectbox("Mostrar", ["Só as em risco, da menor chance para a maior", "Todas"])

    lista = prev if operadora == "Todas" else prev[prev["Nome Fantasia"] == operadora]
    if mostrar != "Todas":
        lista = lista[lista["previsao"] == "Não Resolvida"]
    lista = lista.sort_values("chance_resolvida")

    tabela = lista[["UF", "Nome Fantasia", "Problema", "chance_resolvida", "previsao", "motivo"]].rename(columns={
        "Nome Fantasia": "Operadora", "chance_resolvida": "Chance", "previsao": "Previsão", "motivo": "Principal motivo"})
    st.caption(f"{numero(len(tabela))} reclamações. A tabela mostra as 50 primeiras; o arquivo traz todas.")
    st.dataframe(tabela.head(50).style.format({"Chance": "{:.0%}"}), hide_index=True, width="stretch")
    st.download_button("Baixar a lista completa (.csv)", tabela.to_csv(index=False, sep=";").encode("utf-8-sig"),
                       file_name="previsoes_reclamacoes.csv", mime="text/csv")


def mostrar_previsao_individual(prev, carac):
    st.header("6. Prever uma reclamação", divider="gray")
    colunas_modelo = [coluna for coluna in prev.columns if coluna not in ("chance_resolvida", "previsao", "motivo")]
    with st.form("previsao"):
        campos = st.columns(2)
        reclamacao = {}
        for i, coluna in enumerate(colunas_modelo):
            # Opções da mais comum para a mais rara
            reclamacao[coluna] = campos[i % 2].selectbox(ROTULOS.get(coluna, coluna), prev[coluna].value_counts().index)
        enviado = st.form_submit_button("Prever", type="primary")

    if not enviado:
        return
    codigo, resposta = api.prever(reclamacao)
    if codigo != 200:
        st.error(resposta["erro"])
        return

    chance = resposta["chance_resolvida"]
    media_operadora = prev.loc[prev["Nome Fantasia"] == reclamacao["Nome Fantasia"], "chance_resolvida"].mean()
    col_chance, col_fatores = st.columns([1, 2])
    with col_chance:
        st.metric("Chance de ser resolvida", f"{chance:.0%}",
                  f"{chance - media_operadora:+.0%} em relação à média da operadora")
        if resposta["previsao"] == "Resolvida":
            st.success("Previsão: deve ser **resolvida**.")
        else:
            st.error("Previsão: risco de **não ser resolvida**.")
    with col_fatores:
        st.subheader("O que mais pesou nesta previsão")
        media_geral = prev["chance_resolvida"].mean()
        fatores = carac[[(c, v) in reclamacao.items() for c, v in zip(carac["coluna"], carac["valor"])]].copy()
        fatores["efeito"] = fatores["chance_media"] - media_geral
        for _, f in fatores.reindex(fatores["efeito"].abs().sort_values(ascending=False).index).head(4).iterrows():
            cor, palavra = ("green", "ajuda") if f["efeito"] >= 0 else ("orange", "atrapalha")
            st.markdown(f"{f['caracteristica']}: :{cor}[**{palavra}**] "
                        f"(chance média {f['chance_media']:.0%}, contra {media_geral:.0%} no geral)")


historico = api.historico()
if not historico:
    st.info("Treine um modelo na tela 3 para ver as previsões.")
else:
    codigo, dados = carregar_previsoes(historico[-1]["treinado_em"])
    if codigo != 200:
        st.info(dados["erro"])
    else:
        prev = pd.DataFrame(dados["previsoes"])
        carac = pd.DataFrame(dados["caracteristicas"])
        st.title("Previsões")
        st.caption("A tela 2 mostra o que já aconteceu. Aqui o modelo treinado na tela 3 prevê o que deve acontecer "
                   "com as reclamações que o consumidor ainda não avaliou, e explica por quê.")
        mostrar_confianca(historico[-1], len(prev))
        mostrar_resultado(prev, carac)
        mostrar_porque(carac)
        mostrar_cenarios(prev)
        mostrar_lista(prev)
        mostrar_previsao_individual(prev, carac)
