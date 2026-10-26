# Guia de rotulagem

**Pergunta central:** esta manchete tende a ser boa, ruim ou neutra **para quem tem ações da empresa citada**?

O que vale é o impacto provável para o acionista, não o tom da frase nem o efeito para o consumidor.
Exemplo: "Petrobras reajusta preço da gasolina" é ruim para o consumidor, mas **boa** para o acionista.

## Rótulos

| rótulo | quando usar | exemplos |
|---|---|---|
| `boa` | a notícia tende a valorizar a ação ou aumentar o retorno ao acionista | lucro acima do esperado ou em alta; dividendos/JCP; ação sobe; recomendação de compra ou preço-alvo elevado; novos contratos e encomendas; aquisição estratégica; OPA com prêmio; fim de disputa judicial a favor |
| `ruim` | a notícia tende a desvalorizar a ação ou trazer custo/risco | lucro abaixo do esperado ou em queda; ação cai; recomendação de venda ou corte de preço-alvo; multas e condenações; risco político ou regulatório; falhas operacionais; produção em queda |
| `neutra` | sem efeito claro para o acionista | ações institucionais e culturais; prêmios e rankings; vagas de emprego; páginas de cotação; mudança de participação de fundos (BlackRock, Orbis…); reorganização societária; emissão de dívida de rotina; lançamento de produto sem números; perguntas do tipo "comprar ou vender?" |
| `descartar` | a manchete não é sobre a empresa ou não serve | homônimos (Suzano cidade ou time de vôlei, "Vale" de lugar ou "vale a pena", B3 como local onde se negocia milho, índice ou dólar, Margem Equatorial); empresa citada só como fonte de dados ou de análise; manchete em outra língua |

## Casos difíceis

- **Notícia mista** (ex.: "lucro sobe, mas ação cai"): use o que pesa mais para o acionista, em geral a reação do mercado, e explique em `observacao`.
- **Multas e condenações pequenas**: contam como `ruim` pela direção da notícia, mesmo que o valor seja pequeno para o tamanho da empresa. O modelo só vê a manchete, então não tem como avaliar a proporção.
- **Sinais de trading** ("Swing Trade Compra…", "Day trade: compre X e venda Y"): compra = `boa`, venda = `ruim` para a empresa daquele lado da operação.
- **Notícia sobre outra empresa** em que a nossa aparece de passagem (ex.: cliente usando aviões da Embraer): `neutra`.
- **Manchete só com o nome da empresa**, sem conteúdo: `neutra`.

Na dúvida, escreva o motivo em `observacao` para discutirmos.
