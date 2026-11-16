# Portfolio Radar

Radar de notícias financeiras para uma carteira de ações, com Processamento de Linguagem Natural.

## Problema

Um analista de uma gestora de investimentos precisa acompanhar, todos os dias, as notícias sobre as empresas em que investe, espalhadas por vários sites de jornais. Ler tudo manualmente é lento. O Portfolio Radar coleta manchetes desses sites (via RSS e busca do Google News), classifica cada uma como **boa, ruim ou neutra para o investidor da empresa citada**, extrai as entidades mencionadas e mostra o resultado numa aplicação web: o analista cola o link (ou a manchete) de uma notícia e vê o sentimento e as entidades.

Extensão opcional: incluir os fatos relevantes publicados na CVM.

## Componentes

| Componente | O que faz no projeto | Aula de referência |
|---|---|---|
| Pré-processamento | Limpeza das manchetes e remoção de notícias duplicadas | Semanas 2–4 |
| Análise de sentimentos | Boa / ruim / neutra para o investidor | Semanas 8 e 12 |
| NER | Empresas, tickers, pessoas, locais, valores, percentuais e períodos (spaCy + `EntityRuler` + regras) | Semana 9 |
| Rede neural | Classificadores BiLSTM e GRU (Keras), comparados a TF-IDF + Regressão Logística | Semanas 4, 6 e 10 |
| Transformer | BERT em português pré-treinado, comparado ao LSTM | Semana 11 |
| Aplicação web | Interface em Streamlit: analisa o link ou a manchete (sentimento e entidades), compara com a linha de base, mostra os resultados que justificam os modelos e o radar das manchetes por empresa | Semana 13 |

## Estrutura

```
portfolio-radar/
├── data/            # Dados de exemplo e instruções para obtê-los
├── notebooks/       # Experimentos: sentimentos, NER, rede neural, Transformer
├── src/             # Aplicação web (app.py), treino do modelo do app e código reaproveitado pelos notebooks
├── modelos/         # Classificador do app (gerado por src/treina_modelo_app.py) e suas previsões no teste
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
| `06_treino_estendido.ipynb` | **Entrega de 09/11.** Treina 8 modelos com 5 sementes (TF-IDF, BiLSTM, GRU, embeddings multilíngues, fine-tuning de BERTimbau, FinBERT-PT-BR e XLM-R) em bases em português e inglês e compara com o FinBERT com *bootstrap*. Cria o ambiente na primeira célula; precisa de GPU (~3h30 numa RTX 3060) | `Entregas/09-11-2026/treino_estendido/completo/` |

### Aplicação web

Na raiz do repositório, com o ambiente ativado, treine uma vez o classificador do app (cerca de 15 minutos em CPU; baixa as bases públicas, ~40 MB, e o codificador de frases, ~1 GB):

```bash
python src/treina_modelo_app.py
```

O script refaz o modelo "Embeddings multilíngues + Regressão Logística" do notebook 06, o de maior F1 macro médio no teste (0,657), confere o F1 nas 200 manchetes e salva `modelos/embeddings_lr.joblib` e `modelos/previsoes_teste.csv`. Depois:

```bash
streamlit run src/app.py
```

O navegador abre em http://localhost:8501. A aplicação tem três abas:

- **Analisar manchete:** cole o link de uma notícia (InfoMoney, Money Times, Exame…) ou a própria manchete. O app lê **só o título** da página, nunca o texto da matéria (links do Google News não funcionam, porque abrem a notícia por JavaScript: cole a manchete); classifica a manchete como boa, neutra ou ruim para o acionista com o modelo escolhido e, lado a lado, com a linha de base (FinBERT-PT-BR sem ajuste); e destaca as entidades (`src/ner.py`), liga as empresas da carteira ao ticker e marca como **não verificadas** as entidades que só o modelo estatístico encontrou.
- **Por que estes modelos:** os resultados dos notebooks 03 a 06 que justificam as escolhas (F1 macro dos nove classificadores, intervalos de confiança, F1 por classe e o NER por camada, com o suporte de cada tipo de entidade).
- **Radar da carteira:** as 200 manchetes de teste passadas pelo pipeline inteiro, filtráveis por empresa e por sentimento, com o rótulo revisado ao lado para mostrar onde o modelo erra.

A primeira análise demora alguns segundos, enquanto os modelos carregam. Roda em CPU (testado num MacBook M1 com 8 GB). Sem `modelos/embeddings_lr.joblib`, o app usa o FinBERT-PT-BR. Para usar outro modelo, como um BERTimbau ajustado salvo com `save_pretrained`, defina a variável `RADAR_MODELO` com o nome no Hugging Face ou a pasta do modelo antes de abrir o app.

Entre o 02 e o 03 há uma etapa manual: as 500 manchetes receberam rótulo sugerido por IA generativa (Claude), e 200 delas (cerca de 10 por empresa) formam a `data/teste_revisao.csv`, que revisamos seguindo o guia em `Entregas/27-10-2026/guia_rotulagem.md`. O notebook 03 só depende dessa planilha, então roda direto a partir do repositório. O 04 também roda direto. O 05 baixa as bases públicas de treino do Hugging Face na primeira execução (~30 MB).

## Cronograma

| Data | Entrega | Onde está |
|---|---|---|
| 22/10/2026 | Proposta + experimento de sentimentos | `Entregas/27-10-2026/`, notebook 03 |
| 29/10/2026 | Experimentos de NER e rede neural | `Entregas/30-10-2026/`, notebooks 04 e 05 |
| 09/11/2026 | Experimento com Transformer + protótipo, relatório e código | `Entregas/09-11-2026/`, notebook 06, aplicação em `src/app.py` |
| 16/11/2026 | Relatório técnico e apresentação | `Entregas/16-11-2026/` (`relatorio_tecnico.pdf` e `.docx`) |

## Integrantes

- Luã Japiassu Macedo Maia
- Beatriz Babinski

## Ética e dados

Usamos apenas dados públicos. A carteira é fictícia ou baseada em índice público; nenhuma posição real ou dado interno de gestora é utilizado. O sistema não é recomendação de investimento.

## Uso de IA generativa

Conforme a política da disciplina, o uso de ferramentas de IA (Claude) no código e na escrita será documentado no relatório.
