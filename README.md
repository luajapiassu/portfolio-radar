# Portfolio Radar

Radar de notícias financeiras para uma carteira de ações, com Processamento de Linguagem Natural.

## Problema

Um analista de uma gestora de investimentos precisa acompanhar, todos os dias, as notícias sobre as empresas em que investe, espalhadas por vários sites de jornais. Ler tudo manualmente é lento. O Portfolio Radar coleta manchetes desses sites (via RSS), classifica cada uma como **boa, ruim ou neutra para o investidor da empresa citada**, extrai as entidades mencionadas e permite consultar os resultados por um chatbot.

Extensão opcional: incluir os fatos relevantes publicados na CVM.

## Componentes

| Componente | O que faz no projeto | Aula de referência |
|---|---|---|
| Pré-processamento | Limpeza das manchetes e remoção de notícias duplicadas | Semanas 2–4 |
| Análise de sentimentos | Boa / ruim / neutra para o investidor | Semanas 8 e 12 |
| NER | Empresas, tickers, pessoas, valores e datas (spaCy + `EntityRuler`) | Semana 8 |
| Rede neural | Classificador LSTM/GRU (Keras) como baseline | Semana 10 |
| Transformer | BERT em português pré-treinado, comparado ao LSTM | Semana 11 |
| Chatbot | Perguntas em linguagem natural respondidas só com os dados processados | Semana 13 |

## Estrutura

```
portfolio-radar/
├── data/            # Dados de exemplo e instruções para obtê-los
├── notebooks/       # Experimentos: sentimentos, NER, rede neural, Transformer
├── src/             # Código da aplicação integrada
├── Entregas/        # Uma subpasta por data de entrega (proposta, relatório, resultados)
└── requirements.txt
```

## Como executar

```bash
pip install -r requirements.txt
python -m spacy download pt_core_news_sm
```

Os notebooks também rodam no Google Colab.

## Cronograma

| Data | Entrega |
|---|---|
| 22/10/2026 | Proposta + experimento de sentimentos |
| 29/10/2026 | Experimentos de NER e rede neural |
| 09/11/2026 | Experimento com Transformer + protótipo, relatório e código |
| 16/11/2026 | Apresentação |

## Integrantes

- Luã Japiassu Macedo Maia
- Beatriz Babinski

## Ética e dados

Usamos apenas dados públicos. A carteira é fictícia ou baseada em índice público; nenhuma posição real ou dado interno de gestora é utilizado. O sistema não é recomendação de investimento.

## Uso de IA generativa

Conforme a política da disciplina, o uso de ferramentas de IA (Claude) no código e na escrita será documentado no relatório.
