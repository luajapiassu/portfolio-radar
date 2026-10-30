# Portfolio Radar

Radar de notícias financeiras para uma carteira de ações, com Processamento de Linguagem Natural.

## Problema

Um analista de uma gestora de investimentos precisa acompanhar, todos os dias, as notícias sobre as empresas em que investe, espalhadas por vários sites de jornais. Ler tudo manualmente é lento. O Portfolio Radar coleta manchetes desses sites (via RSS e busca do Google News), classifica cada uma como **boa, ruim ou neutra para o investidor da empresa citada**, extrai as entidades mencionadas e permite consultar os resultados por um chatbot.

Extensão opcional: incluir os fatos relevantes publicados na CVM.

## Componentes

| Componente | O que faz no projeto | Aula de referência |
|---|---|---|
| Pré-processamento | Limpeza das manchetes e remoção de notícias duplicadas | Semanas 2–4 |
| Análise de sentimentos | Boa / ruim / neutra para o investidor | Semanas 8 e 12 |
| NER | Empresas, tickers, pessoas, locais, valores, percentuais e períodos (spaCy + `EntityRuler` + regras) | Semana 9 |
| Rede neural | Classificadores BiLSTM e GRU (Keras), comparados a TF-IDF + Regressão Logística | Semanas 4, 6 e 10 |
| Transformer | BERT em português pré-treinado, comparado ao LSTM | Semana 11 |
| Chatbot | Perguntas em linguagem natural respondidas só com os dados processados | Semana 13 |

## Estrutura

```
portfolio-radar/
├── data/            # Dados de exemplo e instruções para obtê-los
├── notebooks/       # Experimentos: sentimentos, NER, rede neural, Transformer
├── src/             # Código reaproveitado pelos notebooks e pela aplicação (NER, pré-processamento)
├── Entregas/        # Uma subpasta por data de entrega (DD-MM-AAAA): proposta, relatório, resultados
└── requirements.txt
```

## Como executar

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (no Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
python -m spacy download pt_core_news_sm
python -m spacy download pt_core_news_lg
```

Os notebooks rodam localmente (VS Code ou Jupyter), a partir da pasta `notebooks/`. Não precisam de GPU. Testado com Python 3.11.

| Notebook | O que faz | Gera |
|---|---|---|
| `01_coleta_rss.ipynb` | Coleta manchetes via RSS e Google News e filtra as que citam empresas da carteira (`data/carteira.csv`) | `data/raw/manchetes.csv`, `data/raw/manchetes_filtradas.csv` |
| `02_prerrotulo_finbert.ipynb` | Sorteia 500 manchetes (25 por empresa) para rotulagem | `data/raw/rotulagem.csv`, `data/raw/amostra_rotulagem.csv` |
| `03_sentimentos_finbert.ipynb` | **Entrega de 22/10.** Classifica as manchetes revisadas com o FinBERT-PT-BR, mede precisão, revocação e F1 por classe e registra os erros | `Entregas/27-10-2026/resultado_sentimentos.csv` |
| `04_ner.ipynb` | **Entrega de 29/10.** Compara spaCy puro (`sm` e `lg`) com spaCy + `EntityRuler` + regras e avalia o F1 por entidade em 60 manchetes anotadas (`data/ner_ouro.csv`) | `Entregas/30-10-2026/resultado_ner.csv`, `metricas_ner.csv` |
| `05_rede_neural.ipynb` | **Entrega de 29/10.** Treina TF-IDF + Regressão Logística, BiLSTM e GRU em bases públicas rotuladas e compara com o FinBERT nas 200 manchetes revisadas | `Entregas/30-10-2026/resultado_rede_neural.csv`, `metricas_sentimento.csv` |

Entre o 02 e o 03 há uma etapa manual: as 500 manchetes receberam rótulo sugerido por IA generativa (Claude), e 200 delas (cerca de 10 por empresa) formam a `data/teste_revisao.csv`, que revisamos seguindo o guia em `Entregas/27-10-2026/guia_rotulagem.md`. O notebook 03 só depende dessa planilha, então roda direto a partir do repositório. O 04 também roda direto. O 05 baixa as bases públicas de treino do Hugging Face na primeira execução (~30 MB).

## Cronograma

| Data | Entrega | Onde está |
|---|---|---|
| 22/10/2026 | Proposta + experimento de sentimentos | `Entregas/27-10-2026/`, notebook 03 |
| 29/10/2026 | Experimentos de NER e rede neural | `Entregas/30-10-2026/`, notebooks 04 e 05 |
| 09/11/2026 | Experimento com Transformer + protótipo, relatório e código | |
| 16/11/2026 | Apresentação | |

## Integrantes

- Luã Japiassu Macedo Maia
- Beatriz Babinski

## Ética e dados

Usamos apenas dados públicos. A carteira é fictícia ou baseada em índice público; nenhuma posição real ou dado interno de gestora é utilizado. O sistema não é recomendação de investimento.

## Uso de IA generativa

Conforme a política da disciplina, o uso de ferramentas de IA (Claude) no código e na escrita será documentado no relatório.
