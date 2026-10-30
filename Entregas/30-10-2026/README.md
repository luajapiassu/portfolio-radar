# Entrega de 29/10 — Experimentos de NER e rede neural

| Etapa | Notebook | Resultados |
|---|---|---|
| 3 · NER | `notebooks/04_ner.ipynb` | `resultado_ner.csv` (entidades das 200 manchetes), `metricas_ner.csv` (precisão, revocação e F1 por entidade) |
| 4 · Rede neural | `notebooks/05_rede_neural.ipynb` | `resultado_rede_neural.csv` (previsões de cada modelo), `metricas_sentimento.csv` (comparação com o FinBERT) |

Guia de anotação das entidades: `guia_ner.md`. Base anotada: `data/ner_ouro.csv`.

## Resumo

**NER.** Comparamos quatro reconhecedores, cada um somando uma camada ao anterior, em 60 manchetes anotadas (205 entidades):

| reconhecedor | F1 por entidade |
|---|---|
| spaCy `pt_core_news_sm` puro (aula 9) | 0,24 |
| spaCy `pt_core_news_lg` puro | 0,37 |
| + `EntityRuler` com a carteira e os tickers + regras para valores, percentuais e períodos | 0,86 |
| + instituições do mercado e correções pelo contexto ("Nome (TICKER)" é empresa) | **0,95** |

O NER liga cada nome ao ticker da carteira ("Axia Energia", "ex-Eletrobras" e "ELET6" viram ELET3). O código fica em `src/ner.py`, para ser usado pelo chatbot.

**Rede neural.** Treinamos TF-IDF + Regressão Logística, BiLSTM e GRU em duas bases públicas: 503 notícias brasileiras rotuladas por humanos e ~46 mil frases financeiras traduzidas. Avaliamos nas mesmas 200 manchetes do notebook 03:

| modelo | F1 macro |
|---|---|
| TF-IDF + LR | 0,49 |
| BiLSTM | 0,49 |
| GRU | 0,46 |
| FinBERT-PT-BR (notebook 03) | **0,55** |

A rede treinada do zero não superou o FinBERT. Ela sobreajusta já na segunda época e sofre com a mudança de domínio (texto traduzido × manchetes brasileiras). Nenhum modelo reconhece JCP e dividendos como notícia boa. A conclusão é que faltam dados rotulados no nosso critério, e não uma arquitetura melhor, o que orienta o fine-tuning do BERTimbau na próxima etapa.

## Melhorias no que já existia

- `notebooks/03_sentimentos_finbert.ipynb`: acrescentamos precisão, revocação, F1 por classe, F1 macro e matriz de confusão, e preenchemos a análise com os resultados.
- `src/preprocessamento.py`: limpeza de manchetes compartilhada pelos classificadores.
- READMEs atualizados com as bases de treino, as licenças e as instruções de execução.

## Uso de IA generativa

Usamos o Claude (Anthropic) para sugerir as anotações de entidades, que revisamos seguindo `guia_ner.md`, e como apoio na escrita do código e das análises. Rodamos e conferimos todos os resultados.
