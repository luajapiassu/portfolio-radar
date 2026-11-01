# Entrega de 09/11 — Experimento com Transformer (em andamento)

| Etapa | Situação | Onde está |
|---|---|---|
| 5 · Transformers e modelos pré-treinados | **Feito** | `notebooks/06_treino_estendido.ipynb`, resultados em `treino_estendido/completo/` |
| 6 · Protótipo (chatbot) | A fazer | — |
| Relatório técnico | A fazer | — |

## Experimento com Transformers (notebook 06)

Treinamos 8 modelos, cada um com 5 sementes quando o resultado depende da semente, e comparamos com o FinBERT-PT-BR sem treino nas mesmas 200 manchetes revisadas do notebook 03. Usamos as bases em português do notebook 05 e mais três bases em inglês rotuladas por humanos: SEntFiN, Twitter Financial News e Financial PhraseBank.

| modelo | F1 macro (média de 5 sementes) | P(melhor que FinBERT) |
|---|---|---|
| Embeddings multilíngues + Regressão Logística | 0,657 | 99,4% |
| XLM-R treinado só em inglês | 0,648 | 99,8% |
| BERTimbau (fine-tuning) | 0,647 | 99,6% |
| FinBERT-PT-BR (fine-tuning) | 0,641 | 98,9% |
| XLM-R (português + inglês) | 0,639 | 100% |
| FinBERT-PT-BR sem treino (notebook 03) | 0,553 | — |
| GRU | 0,479 | 8% |
| BiLSTM | 0,474 | 7% |

- **Transformers com fine-tuning ganham ~0,10 de F1 macro** sobre o FinBERT sem treino. A vantagem é consistente no *bootstrap* pareado, mas os Transformers empatam entre si.
- **A conclusão da entrega de 29/10 se mantém:** com 5 sementes, BiLSTM e GRU ficam em ~0,47, dentro da faixa do notebook 05, e não superam o FinBERT.
- **Transferência entre línguas:** o XLM-R treinado sem nenhum texto em português empata com o BERTimbau treinado em português.
- **Erro que continua:** nenhum modelo reconhece JCP e dividendos como notícia boa, porque as bases de treino rotulam essas notícias quase sempre como neutras. O próximo passo é incluir no treino manchetes rotuladas no nosso critério.

Arquivos em `treino_estendido/completo/`:

- `consistencia.csv`: média, desvio, mínimo e máximo do F1 de cada modelo nas 5 sementes;
- `comparacao_bootstrap.csv`: F1 do voto das sementes, intervalo de confiança de 95% e P(melhor que FinBERT);
- `rodadas.csv` e `rodadas/`: o resultado de cada treino, com as previsões;
- `previsoes_melhor_modelo.csv`: previsões do melhor modelo e do FinBERT, manchete a manchete.

Treino completo: cerca de 3h35 numa RTX 3060. Instruções de execução no início do notebook.
