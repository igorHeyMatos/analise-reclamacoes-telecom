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
| 3 | Modelo | Escolha do classificador (Árvore de Decisão ou Regressão Logística), ajuste do parâmetro, treino, métricas e histórico |
| 4 | Previsões | O modelo prevê de uma vez todas as reclamações ainda sem avaliação: confiança do modelo, resultado geral, o que mais pesa nas previsões, comparação de cenários entre operadoras, lista com o principal motivo (com download em .csv) e previsão individual |

**Retreino:** ao enviar a base de um novo mês no passo 1, ela substitui a anterior. Basta treinar de novo no passo 3; cada treino fica registrado no histórico e atualiza as previsões da tela 4.

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
  dados.py      leitura, limpeza, resumo e reclamações pendentes (pandas)
  modelo.py     treino, avaliação, previsão em lote e explicação (scikit-learn)
frontend/
  app.py        menu com os 4 passos
  api.py        funções que chamam o back-end
  paginas/      dados.py, analise.py, modelo.py, previsoes.py
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
| GET | `/previsoes` | Previsões de todas as reclamações sem avaliação, com o principal motivo de cada uma |
| POST | `/modelo/cenarios` | Prevê a mesma situação para cada operadora, para comparar |

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
| Igor | Dados, análise e previsões: `backend/dados.py`, `frontend/paginas/dados.py`, `frontend/paginas/analise.py`, `frontend/paginas/previsoes.py`, previsão em lote e cenários em `backend/modelo.py` |
| Rafael | Modelo: treino e avaliação em `backend/modelo.py`, `frontend/paginas/modelo.py` |
