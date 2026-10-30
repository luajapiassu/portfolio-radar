# Dados

Dados brutos não são versionados (`data/raw/` está no `.gitignore`). Ficam versionados só a carteira, a planilha de teste revisada (`teste_revisao.csv`, 200 manchetes) e as entidades anotadas (`ner_ouro.csv`, 60 dessas manchetes).

| Fonte | Conteúdo | Uso / licença |
|---|---|---|
| Feeds RSS de sites de notícias (ex.: InfoMoney, Money Times, Exame, g1 Economia) | Manchete, link, data e fonte de notícias sobre as empresas da carteira | Guardamos só os metadados públicos do RSS, nunca o texto completo. Termos de uso de cada site a documentar |
| Google News (RSS de busca, uma consulta por empresa) | Manchete, link, data e veículo de notícias sobre cada empresa da carteira | Fonte da maior parte das manchetes. Guardamos só os metadados, nunca o texto. Termos de uso a documentar |
| CVM — Portal de Dados Abertos (IPE) | Fatos relevantes das companhias abertas | Extensão opcional. Dados públicos |
| [`lucas-leme/Sentiments-FinBERT-PT-BR`](https://huggingface.co/datasets/lucas-leme/Sentiments-FinBERT-PT-BR) (Hugging Face) | 503 notícias financeiras brasileiras rotuladas por 3 anotadores (positivo / negativo / neutro para o retorno) | Treino do notebook 05. Apache 2.0. Baixado em `data/raw/` na primeira execução |
| [`heitorrosa/financial-sentiment-pt`](https://huggingface.co/datasets/heitorrosa/financial-sentiment-pt) (Hugging Face) | ~63 mil frases e manchetes financeiras traduzidas do inglês (Financial PhraseBank e outras), com nota de qualidade da tradução | Treino do notebook 05, só traduções com nota ≥ 0,6. GPL-3.0. Baixado em `data/raw/` na primeira execução |

**Rótulo de sentimento:** boa / ruim / neutra **para o investidor da empresa citada**.
Exemplo: "Petrobras reajusta preço da gasolina" é ruim para o consumidor, mas boa para o acionista.

**Carteira:** fictícia ou baseada em índice público. Nenhum dado interno ou posição real de gestora é usado.

`carteira.csv` lista as 20 empresas (maiores da B3 por valor de mercado, sem a Itaúsa por duplicar o Itaú). A coluna `apelidos` traz as formas de citar cada empresa, separadas por `|`. A coluna `apelidos_ambiguos` repete os apelidos que também são palavras comuns ou outras entidades (ex.: "Vale", "Vivo", "Localiza"); no filtro eles exigem a grafia exata e a manchete vai para revisão manual.

`ner_ouro.csv` tem as entidades de 60 manchetes do teste, no formato `texto|ROTULO;texto|ROTULO` (rótulos ORG, TICKER, PESSOA, LOCAL, VALOR, PERCENTUAL e PERIODO). As regras de anotação estão em `Entregas/30-10-2026/guia_ner.md`. As anotações foram sugeridas por IA generativa (Claude) e revisadas por nós.
