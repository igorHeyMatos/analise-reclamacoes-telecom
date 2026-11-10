"""Treino, avaliação e previsão com scikit-learn."""
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from dados import ALVO, COLUNAS_MODELO

CLASSES = ["Resolvida", "Não Resolvida"]
ROTULOS = {"Nome Fantasia": "Operadora", "Faixa Etária": "Faixa etária", "Como Comprou Contratou": "Como contratou",
           "Procurou Empresa": "Procurou a empresa"}


def criar_classificador(tipo, parametro):
    # class_weight="balanced": cerca de 70% das reclamações são "Resolvida". Sem esse peso o modelo
    # aprende a responder sempre "Resolvida" e nunca acerta uma "Não Resolvida"
    if tipo == "arvore":
        return DecisionTreeClassifier(max_depth=int(parametro), class_weight="balanced", random_state=42)
    if tipo == "logistica":
        return LogisticRegression(C=float(parametro), class_weight="balanced", max_iter=1000)
    raise ValueError("Classificador inválido. Use 'arvore' ou 'logistica'.")


def treinar(df, tipo, parametro, tamanho_teste):
    """Treina o classificador com a base atual e devolve o modelo e as métricas."""
    # As colunas de texto viram colunas de 0 e 1, porque o modelo só entende números
    X = pd.get_dummies(df[COLUNAS_MODELO])
    y = df[ALVO]

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=tamanho_teste, random_state=42, stratify=y)

    classificador = criar_classificador(tipo, parametro)
    classificador.fit(X_treino, y_treino)

    # Baseline: um "modelo" que sempre responde a classe mais comum
    baseline = DummyClassifier(strategy="most_frequent").fit(X_treino, y_treino)

    previsto_teste = classificador.predict(X_teste)
    # Acurácia equilibrada: média do acerto em cada classe. O baseline sempre fica em 50%
    acerto_por_classe = recall_score(y_teste, previsto_teste, labels=CLASSES, average=None)
    metricas = {
        "equilibrada_teste": round(balanced_accuracy_score(y_teste, previsto_teste), 4),
        "equilibrada_treino": round(balanced_accuracy_score(y_treino, classificador.predict(X_treino)), 4),
        "equilibrada_baseline": round(balanced_accuracy_score(y_teste, baseline.predict(X_teste)), 4),
        "acuracia_teste": round(accuracy_score(y_teste, previsto_teste), 4),
        "acerto_resolvidas": round(acerto_por_classe[0], 4),
        "acerto_nao_resolvidas": round(acerto_por_classe[1], 4),
        "matriz": confusion_matrix(y_teste, previsto_teste, labels=CLASSES).tolist(),
        "linhas_treino": len(X_treino),
        "linhas_teste": len(X_teste),
    }
    # As colunas são guardadas para montar a previsão no mesmo formato do treino
    return {"classificador": classificador, "colunas": X.columns}, metricas


def prever(modelo, reclamacao):
    """Recebe os dados de uma reclamação (dicionário) e devolve a chance de ser resolvida."""
    linha = pd.get_dummies(pd.DataFrame([reclamacao])[COLUNAS_MODELO])
    linha = linha.reindex(columns=modelo["colunas"], fill_value=0)

    classificador = modelo["classificador"]
    indice_resolvida = list(classificador.classes_).index("Resolvida")
    chance = classificador.predict_proba(linha)[0][indice_resolvida]
    return {"chance_resolvida": round(float(chance), 4),
            "previsao": "Resolvida" if chance >= 0.5 else "Não Resolvida"}


def prever_lote(modelo, df):
    """Prevê várias reclamações de uma vez (uma por linha do DataFrame)."""
    X = pd.get_dummies(df[COLUNAS_MODELO]).reindex(columns=modelo["colunas"], fill_value=0)
    classificador = modelo["classificador"]
    indice_resolvida = list(classificador.classes_).index("Resolvida")

    resultado = df[COLUNAS_MODELO].copy()
    resultado["chance_resolvida"] = classificador.predict_proba(X)[:, indice_resolvida].round(4)
    resultado["previsao"] = ["Resolvida" if c >= 0.5 else "Não Resolvida" for c in resultado["chance_resolvida"]]
    return resultado


def explicar(previsoes, minimo=20):
    """Chance média prevista para cada característica (ex.: Problema = juros).

    Mostra o que leva o modelo a prever chances altas ou baixas. Características com
    menos de `minimo` reclamações ficam de fora, porque a média seria pouco confiável.
    """
    partes = []
    for coluna in COLUNAS_MODELO:
        grupo = previsoes.groupby(coluna)["chance_resolvida"].agg(["mean", "count"]).reset_index()
        grupo.columns = ["valor", "chance_media", "quantidade"]
        grupo["caracteristica"] = ROTULOS.get(coluna, coluna) + ": " + grupo["valor"].astype(str)
        grupo["coluna"] = coluna
        partes.append(grupo)
    tabela = pd.concat(partes)
    return tabela[tabela["quantidade"] >= minimo].round({"chance_media": 4}).reset_index(drop=True)


def principal_motivo(previsoes, caracteristicas):
    """Para cada reclamação, a característica que mais puxou a chance para o lado da previsão."""
    # Tabela com a chance média de cada característica da reclamação (uma coluna por campo)
    medias = pd.DataFrame(index=previsoes.index)
    for coluna in COLUNAS_MODELO:
        da_coluna = caracteristicas[caracteristicas["coluna"] == coluna].set_index("valor")["chance_media"]
        medias[coluna] = previsoes[coluna].map(da_coluna)
    medias = medias.fillna(previsoes["chance_resolvida"].mean())  # sem média confiável: valor neutro

    # Em risco: a característica com menor chance média. Resolvida: a com maior
    escolhida = medias.idxmin(axis=1).where(previsoes["previsao"] == "Não Resolvida", medias.idxmax(axis=1))
    return [ROTULOS.get(coluna, coluna) + ": " + str(previsoes.at[i, coluna]) for i, coluna in escolhida.items()]


def cenarios(modelo, base, problema, uf, procurou):
    """Prevê a mesma situação para cada operadora, para comparar o resultado entre elas."""
    do_estado = base[base["UF"] == uf]
    referencia = do_estado if len(do_estado) else base
    # As demais colunas recebem o valor mais comum no estado (ex.: a faixa etária mais frequente)
    tipico = {coluna: referencia[coluna].mode()[0] for coluna in COLUNAS_MODELO}
    operadoras = base["Nome Fantasia"].value_counts().head(8).index

    linhas = [{**tipico, "UF": uf, "Problema": problema, "Procurou Empresa": procurou, "Nome Fantasia": operadora}
              for operadora in operadoras]
    resultado = prever_lote(modelo, pd.DataFrame(linhas))
    return resultado[["Nome Fantasia", "chance_resolvida"]].sort_values("chance_resolvida", ascending=False)
