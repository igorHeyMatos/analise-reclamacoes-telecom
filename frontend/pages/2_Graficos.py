import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from dados_exemplo import PROBLEMAS_CANCELAMENTO, gerar_dados_exemplo, reclamacoes_por_estado

st.set_page_config(page_title="Gráficos", page_icon="📊", layout="wide")
st.title("📊 Gráficos")
st.caption("Protótipo com dados fictícios.")

sns.set_theme(style="whitegrid")
df = gerar_dados_exemplo()

aba_problemas, aba_operadoras, aba_perfil, aba_mapa = st.tabs(
    ["Problemas", "Operadoras", "Perfil do consumidor", "Mapa"]
)

with aba_problemas:
    st.subheader("Problemas mais reclamados")
    contagem = df["Problema"].value_counts()
    # Problemas de cancelamento em vermelho, os demais em azul
    cores = ["#dc2626" if p in PROBLEMAS_CANCELAMENTO else "#2563eb" for p in contagem.index]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.barh(contagem.index, contagem.values, color=cores)
    ax.invert_yaxis()  # o maior fica em cima
    ax.set_xlabel("Reclamações")
    st.pyplot(fig)
    st.caption("Em vermelho: problemas ligados a cancelamento.")

with aba_operadoras:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Reclamações por operadora")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.countplot(data=df, y="Nome Fantasia", order=df["Nome Fantasia"].value_counts().index, ax=ax)
        ax.set_xlabel("Reclamações")
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        st.subheader("Resolvidas x não resolvidas")
        avaliacao = df["Avaliação Reclamação"].value_counts()
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.pie(avaliacao.values, labels=avaliacao.index, autopct="%1.1f%%",
               colors=["#16a34a", "#dc2626"])
        st.pyplot(fig)

with aba_perfil:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Reclamações por faixa etária")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.countplot(data=df, y="Faixa Etária", color="#2563eb", ax=ax)
        ax.set_xlabel("Reclamações")
        ax.set_ylabel("")
        st.pyplot(fig)

    with col2:
        st.subheader("Resolução por forma de contratação")
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.countplot(data=df, y="Como Comprou Contratou", hue="Avaliação Reclamação",
                      palette={"Resolvida": "#16a34a", "Não Resolvida": "#dc2626"}, ax=ax)
        ax.set_xlabel("Reclamações")
        ax.set_ylabel("")
        st.pyplot(fig)

with aba_mapa:
    st.subheader("Reclamações por estado")
    por_estado = reclamacoes_por_estado(df)
    # Raio do círculo em metros: um mínimo de 30 km mais um valor proporcional às reclamações
    por_estado["tamanho"] = 30000 + por_estado["Reclamações"] * 1200

    col1, col2 = st.columns([3, 1])
    col1.map(por_estado, latitude="lat", longitude="lon", size="tamanho", color="#2563eb88")
    col2.dataframe(por_estado[["UF", "Reclamações"]], hide_index=True)
