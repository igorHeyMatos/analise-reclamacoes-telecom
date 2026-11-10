"""Leitura, limpeza e resumo da base de reclamações do consumidor.gov.br (pandas)."""
import io

import pandas as pd

COLUNAS_OBRIGATORIAS = [
    "Região", "UF", "Sexo", "Faixa Etária", "Nome Fantasia", "Segmento de Mercado",
    "Problema", "Como Comprou Contratou", "Procurou Empresa", "Avaliação Reclamação",
]

# Colunas que o modelo usa para prever e a coluna que ele aprende a prever
COLUNAS_MODELO = ["Região", "UF", "Sexo", "Faixa Etária", "Nome Fantasia", "Problema",
                  "Como Comprou Contratou", "Procurou Empresa"]
ALVO = "Avaliação Reclamação"

# Latitude e longitude das capitais, usadas para posicionar cada estado no mapa
CAPITAIS = {
    "AC": (-9.97, -67.81), "AL": (-9.67, -35.74), "AP": (0.03, -51.07), "AM": (-3.12, -60.02),
    "BA": (-12.97, -38.50), "CE": (-3.73, -38.53), "DF": (-15.79, -47.88), "ES": (-20.32, -40.34),
    "GO": (-16.69, -49.26), "MA": (-2.53, -44.30), "MT": (-15.60, -56.10), "MS": (-20.47, -54.62),
    "MG": (-19.92, -43.94), "PA": (-1.46, -48.49), "PB": (-7.12, -34.86), "PR": (-25.43, -49.27),
    "PE": (-8.05, -34.88), "PI": (-5.09, -42.80), "RJ": (-22.91, -43.17), "RN": (-5.79, -35.21),
    "RS": (-30.03, -51.23), "RO": (-8.76, -63.90), "RR": (2.82, -60.67), "SC": (-27.59, -48.55),
    "SP": (-23.55, -46.63), "SE": (-10.91, -37.07), "TO": (-10.18, -48.33),
}


def ler_arquivo(conteudo, nome_arquivo):
    """Transforma o arquivo enviado (.csv, .json ou .xml) em um DataFrame."""
    extensao = nome_arquivo.lower().rsplit(".", 1)[-1]

    if extensao == "csv":
        # Os arquivos mais novos estão em UTF-8 e os antigos em Latin-1
        try:
            return pd.read_csv(io.BytesIO(conteudo), sep=";", encoding="utf-8-sig", low_memory=False)
        except UnicodeDecodeError:
            return pd.read_csv(io.BytesIO(conteudo), sep=";", encoding="latin-1", low_memory=False)
    if extensao == "json":
        return pd.read_json(io.BytesIO(conteudo))
    if extensao == "xml":
        # No XML o nome da coluna não pode ter espaço: "Nome_Fantasia" volta a ser "Nome Fantasia"
        df = pd.read_xml(io.BytesIO(conteudo), parser="etree")
        return df.rename(columns=lambda coluna: coluna.replace("_", " "))

    raise ValueError("Formato não aceito. Envie um arquivo .csv, .json ou .xml.")


def colunas_faltando(df):
    return [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in df.columns]


def limpar(df):
    """Filtra e limpa a base. Devolve a base limpa e quantas linhas sobraram em cada etapa."""
    etapas = [("Arquivo lido", len(df))]

    df = df[df["Segmento de Mercado"].str.contains("Telecomunica", na=False)]
    etapas.append(("Só operadoras de telecom", len(df)))

    df = df[df[ALVO].isin(["Resolvida", "Não Resolvida"])]
    etapas.append(("Só reclamações avaliadas", len(df)))

    df = df.dropna(subset=COLUNAS_MODELO).drop_duplicates()
    etapas.append(("Sem linhas vazias ou duplicadas", len(df)))

    return df[COLUNAS_MODELO + [ALVO]].reset_index(drop=True), etapas


def separar_pendentes(df):
    """Reclamações de telecom que o consumidor ainda não avaliou: são elas que o modelo vai prever."""
    df = df[df["Segmento de Mercado"].str.contains("Telecomunica", na=False)]
    df = df[df[ALVO] == "Não Avaliada"]
    return df.dropna(subset=COLUNAS_MODELO)[COLUNAS_MODELO].reset_index(drop=True)


def eh_cancelamento(problema):
    return "cancel" in problema.lower()


def resumir(df):
    """Calcula os números que o front-end usa nos gráficos."""
    total = len(df)
    resolvida = df[ALVO] == "Resolvida"
    cancelamento = df["Problema"].apply(eh_cancelamento)

    problemas = df["Problema"].value_counts().head(8)
    operadoras = df["Nome Fantasia"].value_counts().head(7)
    # Porcentagem de reclamações resolvidas de cada operadora (só as 7 mais reclamadas)
    resolucao = (df[df["Nome Fantasia"].isin(operadoras.index)]
                 .groupby("Nome Fantasia")[ALVO]
                 .apply(lambda avaliacoes: (avaliacoes == "Resolvida").mean())
                 .sort_values(ascending=False))
    estados = df["UF"].value_counts()
    faixas = df["Faixa Etária"].value_counts().sort_index()

    return {
        "total": total,
        "resolvidas": round(resolvida.mean(), 4),
        "cancelamento": int(cancelamento.sum()),
        "problemas": [{"nome": nome, "quantidade": int(qtd), "cancelamento": eh_cancelamento(nome)}
                      for nome, qtd in problemas.items()],
        "operadoras": {nome: int(qtd) for nome, qtd in operadoras.items()},
        "resolucao": {nome: round(taxa, 4) for nome, taxa in resolucao.items()},
        "estados": [{"UF": uf, "quantidade": int(qtd), "lat": CAPITAIS[uf][0], "lon": CAPITAIS[uf][1]}
                    for uf, qtd in estados.items() if uf in CAPITAIS],
        "faixas": {nome: int(qtd) for nome, qtd in faixas.items()},
        # Valores possíveis de cada coluna, usados no formulário de previsão
        "opcoes": {coluna: sorted(df[coluna].unique().tolist()) for coluna in COLUNAS_MODELO},
    }
