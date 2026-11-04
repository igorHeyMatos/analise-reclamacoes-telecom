# Análise de Reclamações contra Operadoras de Telecom

Aplicação web em Python para analisar as reclamações registradas no
[consumidor.gov.br](https://www.consumidor.gov.br/pages/dadosabertos/externo/)
contra operadoras de telefonia, internet e TV por assinatura, e prever se uma
reclamação será resolvida.

> **Status:** protótipo do front-end. As telas usam dados fictícios para mostrar
> como o sistema vai funcionar depois que a base real for tratada.

## Funcionalidades

| Tela | O que faz |
|---|---|
| **Início** | Apresenta o sistema e explica como usar |
| **Dados** | Upload da base (.csv, .json ou .xml), resumo e prévia dos dados |
| **Gráficos** | Problemas mais reclamados (com destaque para cancelamento), operadoras, perfil do consumidor e mapa por estado |

## Tecnologias

| Biblioteca | Uso |
|---|---|
| Streamlit | Interface web (front-end) |
| pandas | Manipulação e limpeza dos dados |
| NumPy | Geração dos dados de exemplo |
| Matplotlib e Seaborn | Gráficos |

## Como executar

**1. Criar e ativar o ambiente virtual**

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux ou Mac:

```bash
source .venv/bin/activate
```

**2. Instalar as dependências**

```bash
pip install -r requirements.txt
```

**3. Iniciar a aplicação**

```bash
streamlit run frontend/Inicio.py
```

A aplicação abre no navegador em `http://localhost:8501`.

## Estrutura do projeto

```
├── frontend/
│   ├── Inicio.py           tela inicial
│   ├── dados_exemplo.py    dados fictícios usados no protótipo
│   └── pages/
│       ├── 1_Dados.py      upload e resumo da base
│       ├── 2_Graficos.py   gráficos e mapa
├── requirements.txt
└── README.md
```

## Fonte dos dados

Dados abertos do **consumidor.gov.br** (Secretaria Nacional do Consumidor), arquivos
mensais `finalizadas_AAAA-MM`, com uma linha por reclamação.

## Equipe

| Integrante | Responsabilidade |
|---|---|
| Igor | Estrutura do projeto, telas de Dados e Gráficos |
| Rafael | Telas de Modelo e Predição |
