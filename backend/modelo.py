"""Treino, avaliação e previsão com scikit-learn."""
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, recall_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

from dados import ALVO, COLUNAS_MODELO

CLASSES = ["Resolvida", "Não Resolvida"]


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
