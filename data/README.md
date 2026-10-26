# Dados

Dados brutos não são versionados (`data/raw/` está no `.gitignore`).

| Fonte | Conteúdo | Uso / licença |
|---|---|---|
| Feeds RSS de sites de notícias (ex.: InfoMoney, Money Times, Exame, g1 Economia) | Manchete, link, data e fonte de notícias sobre as empresas da carteira | Guardamos só os metadados públicos do RSS, nunca o texto completo. Termos de uso de cada site a documentar |
| CVM — Portal de Dados Abertos (IPE) | Fatos relevantes das companhias abertas | Extensão opcional. Dados públicos |

**Rótulo de sentimento:** boa / ruim / neutra **para o investidor da empresa citada**.
Exemplo: "Petrobras reajusta preço da gasolina" é ruim para o consumidor, mas boa para o acionista.

**Carteira:** fictícia ou baseada em índice público. Nenhum dado interno ou posição real de gestora é usado.

`carteira.csv` lista as 20 empresas (maiores da B3 por valor de mercado, sem a Itaúsa por duplicar o Itaú). A coluna `apelidos` traz as formas de citar cada empresa, separadas por `|`. A coluna `apelidos_ambiguos` repete os apelidos que também são palavras comuns ou outras entidades (ex.: "Vale", "Vivo", "Localiza"); no filtro eles exigem a grafia exata e a manchete vai para revisão manual.
