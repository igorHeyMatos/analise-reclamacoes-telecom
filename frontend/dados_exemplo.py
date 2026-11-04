"""Dados fictícios usados no protótipo do front-end.

As colunas e categorias imitam a base real de reclamações do consumidor.gov.br,
mas os valores são sorteados. Na versão final, estes dados virão do back-end.
"""
import numpy as np
import pandas as pd

# UF: (região, latitude da capital, longitude da capital, peso no sorteio)
ESTADOS = {
    "AC": ("N", -9.97, -67.81, 0.4),   "AL": ("NE", -9.67, -35.74, 1.6),
    "AP": ("N", 0.03, -51.07, 0.4),    "AM": ("N", -3.12, -60.02, 2.0),
    "BA": ("NE", -12.97, -38.50, 7.0), "CE": ("NE", -3.73, -38.53, 4.5),
    "DF": ("CO", -15.79, -47.88, 1.5), "ES": ("SE", -20.32, -40.34, 2.0),
    "GO": ("CO", -16.69, -49.26, 3.5), "MA": ("NE", -2.53, -44.30, 3.0),
    "MT": ("CO", -15.60, -56.10, 1.8), "MS": ("CO", -20.47, -54.62, 1.4),
    "MG": ("SE", -19.92, -43.94, 10.0), "PA": ("N", -1.46, -48.49, 4.0),
    "PB": ("NE", -7.12, -34.86, 2.0),  "PR": ("S", -25.43, -49.27, 6.0),
    "PE": ("NE", -8.05, -34.88, 4.5),  "PI": ("NE", -5.09, -42.80, 1.6),
    "RJ": ("SE", -22.91, -43.17, 9.0), "RN": ("NE", -5.79, -35.21, 1.7),
    "RS": ("S", -30.03, -51.23, 6.0),  "RO": ("N", -8.76, -63.90, 0.9),
    "RR": ("N", 2.82, -60.67, 0.3),    "SC": ("S", -27.59, -48.55, 4.0),
    "SP": ("SE", -23.55, -46.63, 22.0), "SE": ("NE", -10.91, -37.07, 1.1),
    "TO": ("N", -10.18, -48.33, 0.8),
}

OPERADORAS = ["Vivo - Telefônica", "Tim", "Claro Celular", "Claro Residencial",
              "NIO", "SKY", "Oi Fixo"]
PESOS_OPERADORAS = [0.36, 0.20, 0.17, 0.14, 0.05, 0.04, 0.04]

PROBLEMAS = [
    "Cobrança indevida / abusiva para alterar ou cancelar o contrato",
    "Cobrança por serviço/produto não contratado / não reconhecido / não solicitado",
    "Oferta não cumprida / serviço não fornecido/ venda enganosa / publicidade enganosa",
    "Cobrança após cancelamento do serviço",
    "Negativação indevida (SPC, Serasa, SCPC etc)",
    "SAC - Dificuldade para cancelar o serviço",
    "Funcionamento inadequado do serviço (má qualidade do sinal, instabilidade, queda)",
    "SAC - Demanda não resolvida / não respondida / respondida após o prazo",
]
PESOS_PROBLEMAS = [0.22, 0.19, 0.14, 0.13, 0.11, 0.08, 0.07, 0.06]

# Problemas ligados a cancelamento, destacados nos gráficos
PROBLEMAS_CANCELAMENTO = [p for p in PROBLEMAS if "cancel" in p.lower()]

FAIXAS_ETARIAS = ["até 20 anos", "entre 21 a 30 anos", "entre 31 a 40 anos",
                  "entre 41 a 50 anos", "entre 51 a 60 anos", "entre 61 a 70 anos",
                  "mais de 70 anos"]
PESOS_FAIXAS = [0.02, 0.22, 0.35, 0.24, 0.10, 0.05, 0.02]

FORMAS_CONTRATACAO = ["Internet", "Telefone", "Não comprei / contratei",
                      "Loja física", "Domicílio"]
PESOS_CONTRATACAO = [0.39, 0.27, 0.20, 0.12, 0.02]


def gerar_dados_exemplo(quantidade=1000):
    """Sorteia reclamações fictícias com as mesmas colunas da base real."""
    np.random.seed(42)  # mesma semente: os dados saem iguais a cada execução

    siglas = list(ESTADOS.keys())
    pesos_uf = np.array([ESTADOS[uf][3] for uf in siglas])
    ufs = np.random.choice(siglas, size=quantidade, p=pesos_uf / pesos_uf.sum())

    return pd.DataFrame({
        "Região": [ESTADOS[uf][0] for uf in ufs],
        "UF": ufs,
        "Sexo": np.random.choice(["M", "F"], size=quantidade, p=[0.57, 0.43]),
        "Faixa Etária": np.random.choice(FAIXAS_ETARIAS, size=quantidade, p=PESOS_FAIXAS),
        "Nome Fantasia": np.random.choice(OPERADORAS, size=quantidade, p=PESOS_OPERADORAS),
        "Problema": np.random.choice(PROBLEMAS, size=quantidade, p=PESOS_PROBLEMAS),
        "Como Comprou Contratou": np.random.choice(FORMAS_CONTRATACAO, size=quantidade,
                                                   p=PESOS_CONTRATACAO),
        "Procurou Empresa": np.random.choice(["S", "N"], size=quantidade, p=[0.85, 0.15]),
        "Avaliação Reclamação": np.random.choice(["Resolvida", "Não Resolvida"],
                                                 size=quantidade, p=[0.71, 0.29]),
    })


def reclamacoes_por_estado(df):
    """Conta as reclamações de cada UF e junta a coordenada da capital (para o mapa)."""
    contagem = df["UF"].value_counts().reset_index()
    contagem.columns = ["UF", "Reclamações"]
    contagem["lat"] = contagem["UF"].map(lambda uf: ESTADOS[uf][1])
    contagem["lon"] = contagem["UF"].map(lambda uf: ESTADOS[uf][2])
    return contagem
