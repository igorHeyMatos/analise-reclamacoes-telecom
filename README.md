# Análise de Reclamações contra Operadoras de Telecom

Aplicação web em Python que analisa as reclamações registradas no
[consumidor.gov.br](https://www.consumidor.gov.br/pages/dadosabertos/externo/) contra operadoras
de telefonia, internet e TV por assinatura, com foco nos motivos de cancelamento, e prevê se uma
reclamação será resolvida.

## Como funciona

| Passo | Tela | O que acontece |
|---|---|---|
| 1 | Dados | Envio da base (.csv, .json ou .xml). O back-end confere as colunas, filtra as operadoras de telecom e limpa os dados |
| 2 | Análise | Gráficos dos problemas mais reclamados, operadoras, estados (mapa) e faixa etária |
| 3 | Modelo e previsão | Escolha do classificador (Árvore de Decisão ou Regressão Logística), ajuste do parâmetro, treino, histórico e previsão |

**Retreino:** ao enviar a base de um novo mês no passo 1, ela substitui a anterior. Basta treinar de novo no passo 3; cada treino fica registrado no histórico.

## Tecnologias

| Biblioteca | Uso |
|---|---|
| Flask | Back-end (rotas que recebem os pedidos do front-end) |
| Streamlit | Front-end (telas) |
| pandas | Leitura, limpeza e resumo dos dados |
| matplotlib e seaborn | Gráficos |
| scikit-learn | Treino, avaliação e previsão |

## Estrutura

```
backend/
  app.py        rotas do Flask
  dados.py      leitura, limpeza e resumo da base (pandas)
  modelo.py     treino, avaliação e previsão (scikit-learn)
frontend/
  app.py        menu com os 3 passos
  api.py        funções que chamam o back-end
  paginas/      dados.py, analise.py, modelo.py
dados/exemplo/  amostra da base oficial para testes
```

## Rotas do back-end

| Método | Rota | Função |
|---|---|---|
| GET | `/status` | Base atual e base usada no último treino |
| POST | `/dados` | Recebe o arquivo, valida e limpa a base |
| GET | `/dados/resumo` | Números usados nos gráficos |
| POST | `/modelo/treinar` | Treina (ou retreina) o classificador |
| GET | `/modelo/historico` | Lista os treinos feitos |
| POST | `/modelo/prever` | Prevê se uma reclamação será resolvida |

## Como executar

Criar e ativar o ambiente virtual (Windows):

```bash
python -m venv .venv
.venv\Scripts\activate
```

Instalar as dependências:

```bash
pip install -r requirements.txt
```

Em um terminal, iniciar o back-end (porta 5000):

```bash
python backend/app.py
```

Em outro terminal, iniciar o front-end (abre em `http://localhost:8501`):

```bash
streamlit run frontend/app.py
```

## Dados

As bases mensais ficam em consumidor.gov.br, Dados Abertos, nas linhas "Dados - Mês/Ano"
(arquivos `finalizadas_AAAA-MM`). A pasta `dados/exemplo` tem uma amostra de 7.500 linhas da base
de setembro de 2026, usada no botão "Usar a base de exemplo".

## Equipe

| Integrante | Responsabilidade |
|---|---|
| Igor | Dados e análise: `backend/dados.py`, `frontend/paginas/dados.py`, `frontend/paginas/analise.py` |
| Rafael | Modelo e previsão: `backend/modelo.py`, `frontend/paginas/modelo.py` |
