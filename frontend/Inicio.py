import streamlit as st

st.set_page_config(page_title="Reclamações Telecom", page_icon="📞", layout="wide")

st.title("📞 Análise de Reclamações contra Operadoras de Telecom")
st.write(
    "Aplicação para analisar as reclamações registradas no **consumidor.gov.br** "
    "contra operadoras de telefonia, internet e TV por assinatura, e prever se uma "
    "reclamação será resolvida."
)

st.warning("Protótipo: as telas usam **dados fictícios** para mostrar como o sistema vai funcionar.")

st.subheader("Como usar")
st.markdown(
    """
1. **Dados**: envie a base de reclamações (.csv, .json ou .xml) e veja um resumo.
2. **Gráficos**: veja os principais problemas, as operadoras e o mapa por estado.
3. **Modelo**: escolha o classificador, ajuste os parâmetros e treine.
4. **Predição**: informe os dados de uma reclamação e veja a previsão.
"""
)

st.caption("Fonte dos dados: consumidor.gov.br (Secretaria Nacional do Consumidor)")
