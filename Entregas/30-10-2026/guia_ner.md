# Guia de anotação de entidades (NER)

Base anotada: `data/ner_ouro.csv`, com 60 manchetes de `data/teste_revisao.csv`. Escolhemos as manchetes de modo a cobrir todas as empresas e todos os tipos de entidade. As anotações foram sugeridas por IA generativa (Claude) e revisadas por nós, como os rótulos de sentimento.

Formato: `texto|ROTULO`, separados por `;`, na ordem em que aparecem. O texto é copiado exatamente da manchete. Se a mesma entidade aparece duas vezes, ela é anotada duas vezes.

## Rótulos

| rótulo | o que marcar | exemplos | não marcar |
|---|---|---|---|
| `ORG` | empresas, bancos, gestoras, corretoras, órgãos públicos e tribunais | Santander Brasil, BTG Pactual Asset, JP Morgan, STF, CVM, União, Força Aérea do Uzbequistão | índices (Ibovespa), produtos (Gripen, C-390), veículos de imprensa citados como prefixo ("JP1:") |
| `TICKER` | código de negociação da B3 | SANB11, BBAS3, MELI34, B3SA3 | — |
| `PESSOA` | pessoas, mesmo quando só o primeiro nome aparece | André Esteves, Lula, Flávio | — |
| `LOCAL` | países, estados, cidades, bairros, ativos físicos com nome de lugar | Peru, Maceió, Centro Histórico, Complexo de Thompson | — |
| `VALOR` | quantia em dinheiro, com a moeda e a escala | R$ 0,40; R$ 197 Milhões; US$34,5 bilhões; 10 milhões (quando é dinheiro, mesmo sem "R$") | quantidades físicas (191,6 mil boepd, 388 mil hectares) |
| `PERCENTUAL` | número seguido de % | 7,8%; 79% | — |
| `PERIODO` | trimestres, meses, anos e datas | 2T26; 4T25; 2º tri; 3º trimestre; setembro de 2026; 2026 | "hoje", "nesta segunda-feira" |

## Regras

- **Nome e ticker são entidades separadas:** "Banco do Brasil (BBAS3)" vira `Banco do Brasil|ORG` e `BBAS3|TICKER`.
- **Sem palavras de função:** "quase R$ 2 bilhões" é anotado como `R$ 2 bilhões`, e "a dona da Vivo" como `Vivo`.
- **Nome antigo e nome novo:** "Axia Energia, antiga Eletrobras" tem duas `ORG`. As duas apontam para o ticker ELET3.

## Avaliação

- **Exata:** a entidade prevista só conta como acerto se o texto e o rótulo forem iguais aos da anotação, ignorando maiúsculas e o tipo de apóstrofo. Também calculamos precisão, revocação e F1 por rótulo.
- **Relaxada:** conta como acerto se o rótulo é o mesmo e o trecho se sobrepõe ao anotado. Isso mostra quantos erros são só de fronteira, por exemplo `R$ 2 bilhões` × `quase R$ 2 bilhões`.
