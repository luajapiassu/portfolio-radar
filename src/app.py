"""Portfolio Radar: cole o link (ou a manchete) de uma notícia e veja o sentimento para o acionista e as entidades citadas.

Três abas:
- Analisar manchete: sentimento (modelo escolhido × linha de base) e entidades de uma notícia;
- Por que estes modelos: os resultados dos experimentos que justificam as escolhas;
- Radar da carteira: as 200 manchetes de teste processadas, por empresa, com os erros à vista.

Para rodar, na raiz do repositório:
    streamlit run src/app.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st
from spacy import displacy

from ner import INSTITUICOES, carrega_nlp, entidades, normaliza
from sentimento import ARQ_EMBEDDINGS_LR, carrega_classificador, classifica
from titulo import manchete_do_link

RAIZ = Path(__file__).resolve().parent.parent
CARTEIRA = RAIZ / "data" / "carteira.csv"
ENTREGAS = RAIZ / "Entregas"
FIGURAS = ENTREGAS / "16-11-2026" / "figuras"
TREINO = ENTREGAS / "09-11-2026" / "treino_estendido" / "completo"

CORES = {"ORG": "#7aecec", "TICKER": "#bfeeb7", "PESSOA": "#aa9cfc", "LOCAL": "#ff9561",
         "VALOR": "#e4e7d2", "PERCENTUAL": "#ffeb80", "PERIODO": "#c887fb"}
ICONE = {"boa": "🟢", "neutra": "⚪", "ruim": "🔴"}
# Vêm de regras com forma fixa (R$ ..., 2T26, PETR4): não dependem do modelo estatístico
POR_REGRA = {"TICKER", "VALOR", "PERCENTUAL", "PERIODO"}
# Manchetes do teste (rótulo revisado entre parênteses) em que o modelo do app acerta e a linha de base erra,
# um erro que os dois cometem (proventos) e casos que exercitam o NER
EXEMPLOS = [
    "Sem espaço para otimismo? CFO do Santander (SANB11) faz alerta sobre rentabilidade e provisões",  # ruim
    "PRIO (PRIO3) registra vitória em blocos Magnetita e Hematita da ANP",  # boa
    "Itaú Unibanco (ITUB4) emite R$ 5 bi em letras financeiras",  # neutra
    "Equatorial atribui à gestão municipal responsabilidade pela rede do Terminal da Cohab",  # neutra
    "Santander Brasil (SANB11) aprova JCP de R$ 0,40 por unit",  # boa: os dois erram (proventos)
    "Lucro da Ambev (ABEV3) supera expectativa no 2T26, mas ação chega a cair 3%",
    "O efeito colateral do fim da escala 6x1 para Rede D'Or, Hapvida e Fleury",
    "Axia, ex-Eletrobras, inicia sucessão do CEO Ivan Monteiro",
]


@st.cache_resource(show_spinner="Carregando o NER...")
def nlp():
    return carrega_nlp(CARTEIRA)


@st.cache_resource(show_spinner="Carregando o modelo de sentimento...")
def classificador(modelo=None):
    return carrega_classificador(modelo)


@st.cache_data
def nomes_carteira():
    return pd.read_csv(CARTEIRA).set_index("ticker")["empresa"].to_dict()


def verificada(e):
    """Entidade confiável: ligada à carteira, encontrada por regra ou na lista de instituições do mercado."""
    return bool(e["ticker"]) or e["rotulo"] in POR_REGRA or e["texto"] in INSTITUICOES


def barras(probs):
    for r in ["boa", "neutra", "ruim"]:
        st.progress(probs[r], text=f"{r}: {probs[r]:.0%}")


st.set_page_config(page_title="Portfolio Radar", layout="wide")
st.title("Portfolio Radar")
st.caption("Triagem de notícias financeiras para uma carteira de ações: a manchete é **boa, neutra ou ruim para o "
           "acionista** da empresa citada, e quais entidades aparecem nela. Projeto acadêmico de PLN (Ibmec), "
           "não é recomendação de investimento.")

aba_analise, aba_modelos, aba_radar = st.tabs(["Analisar manchete", "Por que estes modelos", "Radar da carteira"])

# --------------------------------------------------------------------------------------------- Analisar manchete
with aba_analise:
    with st.form("entrada"):
        link = st.text_input("Link da notícia", placeholder="https://www.infomoney.com.br/...")
        manchete = st.text_area("…ou cole a manchete", height=80, help="Se você preencher os dois, vale a manchete.")
        exemplo = st.selectbox("…ou escolha um exemplo", [""] + EXEMPLOS)
        comparar = st.toggle("Comparar com a linha de base (FinBERT-PT-BR sem ajuste)", value=True)
        enviar = st.form_submit_button("Analisar", type="primary")

    texto = ""
    if enviar:
        texto = manchete.strip() or exemplo
        if not texto and link.strip():
            try:
                with st.spinner("Lendo o título da notícia..."):
                    texto = manchete_do_link(link)
            except ValueError as erro:
                st.error(str(erro))
        if not texto and not link.strip():
            st.warning("Informe um link, uma manchete ou escolha um exemplo.")

    if texto:
        clf = classificador()
        rotulo, pontuacao, probs = classifica(clf, texto)
        ents = entidades(nlp(), texto)
        nomes = nomes_carteira()
        empresas = sorted({e["ticker"] for e in ents if e["ticker"]})

        st.subheader(texto.replace("$", "\\$"))  # sem isso, "R$ ... R$" vira fórmula matemática
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Para o acionista", f"{ICONE[rotulo]} {rotulo}")
            st.caption(f"**{clf.nome}** · {clf.detalhe}")
            barras(probs)
        if comparar:
            base = classificador("finbert")
            rotulo_b, _, probs_b = classifica(base, texto)
            with col2:
                st.metric("Linha de base", f"{ICONE[rotulo_b]} {rotulo_b}",
                          delta="concorda" if rotulo_b == rotulo else "discorda", delta_color="off")
                st.caption(f"**{base.nome}** · {base.detalhe}")
                barras(probs_b)
        with col3:
            st.metric("Empresas da carteira", len(empresas))
            st.caption(", ".join(f"{nomes.get(t, t)} ({t})" for t in empresas) or "nenhuma")
        st.caption("As barras são a pontuação de cada classe, não uma probabilidade calibrada: servem para comparar "
                   "as classes de uma mesma manchete.")

        st.markdown("#### Entidades")
        if ents:
            doc = {"text": normaliza(texto),
                   "ents": [{"start": e["inicio"], "end": e["fim"], "label": e["rotulo"]} for e in ents]}
            st.markdown(displacy.render(doc, style="ent", manual=True, options={"colors": CORES}),
                        unsafe_allow_html=True)
            st.dataframe(pd.DataFrame([{
                "trecho": e["texto"],
                "tipo": e["rotulo"],
                "origem": "regra / carteira" if verificada(e) else "só modelo estatístico (não verificada)",
                "empresa da carteira": f"{nomes.get(e['ticker'], '')} ({e['ticker']})" if e["ticker"] else "",
            } for e in ents]), hide_index=True, use_container_width=True)
            st.caption("**Não verificada:** pessoa, local ou organização encontrada só pelo spaCy, sem ligação com a "
                       "carteira nem com a lista de instituições do mercado. Pode ser erro.")
        else:
            st.info("Nenhuma entidade encontrada.")

# ------------------------------------------------------------------------------------------ Por que estes modelos
with aba_modelos:
    st.markdown("### Sentimento: nove classificadores nas mesmas 200 manchetes")
    st.markdown(
        "Teste: 200 manchetes da carteira (76 boas, 96 neutras, 28 ruins), rotuladas no critério do acionista e "
        "nunca usadas no treino. Métrica principal: **F1 macro**, que dá o mesmo peso às três classes e não deixa a "
        "classe neutra, a maior, esconder os erros nas outras.")
    c1, c2 = st.columns([3, 2])
    if (FIGURAS / "f1_sentimento.png").exists():
        c1.image(str(FIGURAS / "f1_sentimento.png"), use_container_width=True)
    with c2:
        st.markdown(
            "**Três patamares, e cada um explica uma escolha:**\n"
            "1. **Treinados do zero** (TF-IDF, BiLSTM, GRU): ~0,48. Aprendem o vocabulário só com o treino, quase "
            "todo traduzido do inglês; 12% das palavras do teste nunca foram vistas.\n"
            "2. **FinBERT-PT-BR sem ajuste**: 0,553. Conhece o vocabulário financeiro, mas mede o *tom*, não o "
            "impacto para o acionista.\n"
            "3. **Transformer pré-treinado + nossas bases**: 0,64 a 0,66. O pré-treino resolve o vocabulário e o "
            "ajuste ensina a tarefa.\n\n"
            "**Entre os cinco do topo não há vencedor estatístico:** as diferenças (0,01 a 0,02) são menores que a "
            "variação entre sementes. O app usa **Embeddings multilíngues + Regressão Logística** porque empata com "
            "os fine-tunings, treina só a Regressão Logística (2,5 min contra 4 a 14 min por rodada de fine-tuning "
            "na GPU), é determinístico e dá para treinar e rodar sem GPU.\n\n"
            "A cópia usada aqui foi retreinada num Mac (`src/treina_modelo_app.py`): mesma validação (0,701) e "
            "F1 de 0,652 no teste. Só 5 das 200 manchetes mudam, todas com pontuação abaixo de 0,49, por "
            "diferenças numéricas entre a GPU da NVIDIA e a do Mac.")

    cons = pd.read_csv(TREINO / "consistencia.csv")
    boot = pd.read_csv(TREINO / "comparacao_bootstrap.csv").rename(columns={"modelo": "nome"})
    tabela = cons.merge(boot, on="nome", how="left")
    tabela = pd.DataFrame({
        "modelo": tabela["nome"],
        "rodadas": tabela["rodadas"],
        "F1 macro (média)": tabela["f1_teste_media"],
        "± desvio": tabela["f1_teste_desvio"],
        "IC 95%": tabela.apply(lambda r: f"{r['IC 95% inferior']:.2f} a {r['IC 95% superior']:.2f}", axis=1),
        "F1 boa": tabela["f1_boa"], "F1 neutra": tabela["f1_neutra"], "F1 ruim": tabela["f1_ruim"],
        "P(> FinBERT)": tabela["P(melhor que FinBERT)"] * 100,
        "treino por rodada (min)": (tabela["minutos"] / tabela["rodadas"]).round(1),
    })
    st.dataframe(tabela, hide_index=True, use_container_width=True, column_config={
        "P(> FinBERT)": st.column_config.NumberColumn(format="%.1f%%"),
    })
    st.caption("Rodadas: 5 sementes nos modelos que dependem da inicialização; TF-IDF e embeddings congelados são "
               "determinísticos e rodam uma vez. IC 95% e P(> FinBERT) vêm de um bootstrap pareado (2.000 sorteios) "
               "sobre o voto das sementes. Tempo de treino de uma rodada numa RTX 3060 (notebook 06).")
    if (FIGURAS / "f1_por_classe.png").exists():
        st.image(str(FIGURAS / "f1_por_classe.png"), caption="F1 por classe: o maior ganho dos Transformers está "
                 "na classe ruim; a classe boa continua a mais difícil (proventos).", use_container_width=True)

    st.markdown("### NER: cada camada corrige um tipo de erro")
    c1, c2 = st.columns([3, 2])
    if (FIGURAS / "f1_ner.png").exists():
        c1.image(str(FIGURAS / "f1_ner.png"), use_container_width=True)
    ner = pd.read_csv(ENTREGAS / "30-10-2026" / "metricas_ner.csv").rename(columns={"Unnamed: 0": "reconhecedor"})
    final = ner[ner["reconhecedor"].str.startswith("D")].copy()
    final["no gabarito"] = final["TP"] + final["FN"]
    with c2:
        st.markdown(
            "60 manchetes anotadas, 205 entidades. spaCy `lg` puro: **0,37**. + `EntityRuler` da carteira e regras "
            "de forma fixa (ticker, R$, %, 2T26): **0,86**. + contexto do mercado (\"Nome (TICKER)\" é empresa, "
            "siglas, cargos, enumerações): **0,96**.")
        st.dataframe(final[["rotulo", "no gabarito", "precisão", "revocação", "F1"]], hide_index=True,
                     use_container_width=True)
        st.warning("**Leia com cuidado:** PESSOA (8) e LOCAL (9) têm pouco suporte, então um único acerto ou erro "
                   "muda o F1 em 0,05 a 0,10. E as regras de contexto foram criadas olhando os erros nesta mesma "
                   "amostra, então o 0,96 é otimista; o 0,86 da camada C é a estimativa mais conservadora.")

# ------------------------------------------------------------------------------------------- Radar da carteira
with aba_radar:
    st.markdown("As 200 manchetes de teste passadas pelo pipeline inteiro: sentimento do modelo do app, linha de "
                "base, entidades e o rótulo revisado por nós. É o que o analista veria no radar, com os erros à vista.")
    arq_prev = ARQ_EMBEDDINGS_LR.parent / "previsoes_teste.csv"
    radar = pd.read_csv(TREINO / "previsoes_melhor_modelo.csv")[["id", "empresa", "manchete", "rotulo", "finbert"]]
    radar = radar.merge(pd.read_csv(ENTREGAS / "30-10-2026" / "resultado_ner.csv")[["id", "entidades"]],
                        on="id", how="left")
    if arq_prev.exists():
        radar = radar.merge(pd.read_csv(arq_prev), on="id", how="left")
    else:
        st.info("Rode `python src/treina_modelo_app.py` para incluir as previsões do modelo do app.")
        radar["previsto"], radar["pontuacao"] = radar["finbert"], None
    nomes = nomes_carteira()

    f1, f2, f3 = st.columns([2, 2, 1])
    empresa = f1.selectbox("Empresa", ["todas"] + sorted(radar["empresa"].unique()),
                           format_func=lambda t: t if t == "todas" else f"{nomes.get(t, t)} ({t})")
    classes = f2.multiselect("Sentimento previsto", ["boa", "neutra", "ruim"], default=["boa", "neutra", "ruim"])
    so_erros = f3.toggle("Só erros do modelo")
    filtro = radar if empresa == "todas" else radar[radar["empresa"] == empresa]

    acerto = (filtro["previsto"] == filtro["rotulo"]).mean()
    acerto_b = (filtro["finbert"] == filtro["rotulo"]).mean()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Manchetes", len(filtro))
    m2.metric("Ruins segundo o modelo", int((filtro["previsto"] == "ruim").sum()))
    m3.metric("Acerto do modelo do app", f"{acerto:.0%}")
    m4.metric("Acerto da linha de base", f"{acerto_b:.0%}", delta=f"{(acerto_b - acerto) * 100:+.1f} p.p.".replace(".", ",", 1).replace(",p", ".p"),
              delta_color="normal")

    if empresa == "todas":
        contagem = pd.crosstab(radar["empresa"].map(lambda t: f"{nomes.get(t, t)}"), radar["previsto"])
        st.bar_chart(contagem.reindex(columns=["boa", "neutra", "ruim"], fill_value=0),
                     color=["#2e9e5b", "#b0b0b0", "#d64545"], horizontal=True, height=520)

    vista = filtro[filtro["previsto"].isin(classes)]
    if so_erros:
        vista = vista[vista["previsto"] != vista["rotulo"]]
    st.dataframe(vista.assign(
        modelo=vista["previsto"].map(lambda r: f"{ICONE[r]} {r}"),
        revisado=vista["rotulo"].map(lambda r: f"{ICONE[r]} {r}"),
        linha_de_base=vista["finbert"].map(lambda r: f"{ICONE[r]} {r}"),
    )[["empresa", "manchete", "modelo", "revisado", "linha_de_base", "entidades"]],
        hide_index=True, use_container_width=True, height=420,
        column_config={"manchete": st.column_config.TextColumn(width="large"),
                       "linha_de_base": "linha de base (FinBERT)"})
    st.caption("Erro que se repete: manchetes de JCP e dividendos, boas para o acionista, saem como neutras, porque "
               "as bases públicas de treino rotulam proventos quase sempre como neutros.")
