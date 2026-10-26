# Dados

Dados brutos não são versionados (`data/raw/` está no `.gitignore`).

| Fonte | Conteúdo | Uso / licença |
|---|---|---|
| Feeds RSS de sites de notícias (ex.: InfoMoney, Money Times, Exame, g1 Economia) | Manchete, link, data e fonte de notícias sobre as empresas da carteira | Guardamos só os metadados públicos do RSS, nunca o texto completo. Termos de uso de cada site a documentar |
| CVM — Portal de Dados Abertos (IPE) | Fatos relevantes das companhias abertas | Extensão opcional. Dados públicos |

**Rótulo de sentimento:** boa / ruim / neutra **para o investidor da empresa citada**.
Exemplo: "Petrobras reajusta preço da gasolina" é ruim para o consumidor, mas boa para o acionista.

**Carteira:** fictícia ou baseada em índice público. Nenhum dado interno ou posição real de gestora é usado.

`treino.csv` e `teste.csv` são gerados pelo notebook 03. O treino junta o dataset público `lucas-leme/Sentiments-FinBERT-PT-BR` (rotulado por humanos) e as nossas manchetes rotuladas pelo FinBERT-PT-BR. O teste tem 200 manchetes com rótulo sugerido por IA generativa e revisado por nós. Todos os modelos do projeto são avaliados no mesmo `teste.csv`.

`carteira.csv` lista as 20 empresas (maiores da B3 por valor de mercado, sem a Itaúsa por duplicar o Itaú). A coluna `apelidos` traz as formas de citar cada empresa, separadas por `|`. A coluna `apelidos_ambiguos` repete os apelidos que também são palavras comuns ou outras entidades (ex.: "Vale", "Vivo", "Localiza"); no filtro eles exigem a grafia exata e a manchete vai para revisão manual.
