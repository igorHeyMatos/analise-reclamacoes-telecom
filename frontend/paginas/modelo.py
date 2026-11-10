import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

import api

CLASSIFICADORES = {"Árvore de Decisão": "arvore", "Regressão Logística": "logistica"}
NOMES = {valor: nome for nome, valor in CLASSIFICADORES.items()}


def mostrar_treino():
    col_config, col_resultado = st.columns([2, 3])

    with col_config:
        st.subheader("Treinar")
        nome = st.selectbox("Classificador", list(CLASSIFICADORES))
        if nome == "Árvore de Decisão":
            parametro = st.slider("Profundidade máxima da árvore", 1, 20, 5,
                                  help="Pouca profundidade simplifica demais; muita profundidade decora o treino.")
        else:
            parametro = st.select_slider("Regularização (C)", [0.01, 0.1, 1.0, 10.0, 100.0], value=1.0,
                                         help="C menor deixa o modelo mais simples.")
        teste = st.slider("Parte da base separada para teste (%)", 10, 40, 20, step=5)

        if st.button("Treinar com a base atual", type="primary"):
            with st.spinner("Treinando e prevendo as reclamações em aberto..."):
                codigo, resposta = api.treinar(CLASSIFICADORES[nome], parametro, teste / 100)
            if codigo != 200:
                st.error(resposta["erro"])
            else:
                st.session_state["treino"] = resposta

    with col_resultado:
        st.subheader("Resultado do treino")
        treino = st.session_state.get("treino")
        if treino is None:
            st.info("Nenhum treino nesta sessão.")
            return

        st.caption(f"{NOMES[treino['classificador']]} treinado com {treino['base']}: "
                   f"{treino['linhas_treino']} linhas de treino e {treino['linhas_teste']} de teste.")
        m1, m2 = st.columns(2)
        m1.metric("Acurácia equilibrada (teste)", f"{treino['equilibrada_teste']:.1%}",
                  f"{treino['equilibrada_teste'] - treino['equilibrada_baseline']:+.1%} sobre o baseline",
                  help="Média do acerto nas resolvidas e nas não resolvidas.")
        m2.metric("Baseline", f"{treino['equilibrada_baseline']:.1%}",
                  help="Um modelo que sempre responde 'Resolvida'. Acerta todas as resolvidas e nenhuma não resolvida.")
        m3, m4 = st.columns(2)
        m3.metric("Acerto nas resolvidas", f"{treino['acerto_resolvidas']:.0%}")
        m4.metric("Acerto nas não resolvidas", f"{treino['acerto_nao_resolvidas']:.0%}")

        if treino["equilibrada_treino"] - treino["equilibrada_teste"] > 0.1:
            st.warning(f"Overfitting: {treino['equilibrada_treino']:.0%} no treino e "
                       f"{treino['equilibrada_teste']:.0%} no teste. Diminua a profundidade.")
        elif treino["equilibrada_teste"] <= treino["equilibrada_baseline"]:
            st.warning("O modelo não supera o baseline com essa configuração.")
        else:
            st.success("O modelo supera o baseline sem decorar o treino.")

        classes = ["Resolvida", "Não Resolvida"]
        fig, ax = plt.subplots(figsize=(4.5, 3))
        sns.heatmap(treino["matriz"], annot=True, fmt="d", cmap="Blues", cbar=False,
                    xticklabels=classes, yticklabels=classes, ax=ax)
        ax.set_xlabel("Previsto")
        ax.set_ylabel("Real")
        ax.set_title("Matriz de confusão (teste)")
        st.pyplot(fig)


def mostrar_historico():
    st.subheader("Histórico de treinos")
    historico = api.historico()
    if not historico:
        st.caption("Nenhum treino feito ainda.")
        return historico

    tabela = pd.DataFrame(historico)
    tabela["classificador"] = tabela["classificador"].map(NOMES)
    tabela = tabela[["base", "classificador", "parametro", "equilibrada_teste",
                     "acerto_resolvidas", "acerto_nao_resolvidas"]]
    tabela.columns = ["Base", "Classificador", "Parâmetro", "Acurácia equilibrada",
                      "Acerto resolvidas", "Acerto não resolvidas"]
    st.dataframe(tabela.style.format("{:.1%}", subset=["Acurácia equilibrada", "Acerto resolvidas",
                                                        "Acerto não resolvidas"]),
                 hide_index=True, width="stretch")
    return historico


status_resumo, resumo = api.resumo()
if status_resumo != 200:
    st.info("Envie uma base no passo 1 para treinar o modelo.")
else:
    st.title("Modelo")
    st.caption("Escolha o classificador e treine. Quando enviar uma base nova no passo 1, treine de novo: isso é o retreino. "
               "As previsões ficam na tela 4.")
    mostrar_treino()
    mostrar_historico()
