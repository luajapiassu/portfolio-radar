"""Portfolio Radar: cole o link (ou a manchete) de uma notícia e veja o sentimento para o acionista e as entidades citadas.

Para rodar, na raiz do repositório:
    streamlit run src/app.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st
from spacy import displacy

from ner import INSTITUICOES, carrega_nlp, entidades, normaliza
from sentimento import carrega_classificador, classifica
from titulo import manchete_do_link

RAIZ = Path(__file__).resolve().parent.parent
CARTEIRA = RAIZ / "data" / "carteira.csv"

CORES = {"ORG": "#7aecec", "TICKER": "#bfeeb7", "PESSOA": "#aa9cfc", "LOCAL": "#ff9561",
         "VALOR": "#e4e7d2", "PERCENTUAL": "#ffeb80", "PERIODO": "#c887fb"}
ICONE = {"boa": "🟢", "neutra": "⚪", "ruim": "🔴"}
# Vêm de regras com forma fixa (R$ ..., 2T26, PETR4): não dependem do modelo estatístico
POR_REGRA = {"TICKER", "VALOR", "PERCENTUAL", "PERIODO"}
EXEMPLOS = [
    "Itaú (ITUB4) lucra R$ 12,4 bilhões no 2T26, acima das expectativas",
    "Lucro da Ambev (ABEV3) supera expectativa no 2T26, mas ação chega a cair 3%",
    "O efeito colateral do fim da escala 6x1 para Rede D'Or, Hapvida e Fleury",
    "Axia, ex-Eletrobras, inicia sucessão do CEO Ivan Monteiro",
]


@st.cache_resource(show_spinner="Carregando o NER...")
def nlp():
    return carrega_nlp(CARTEIRA)


@st.cache_resource(show_spinner="Carregando o modelo de sentimento...")
def classificador():
    return carrega_classificador()


@st.cache_data
def nomes_carteira():
    return pd.read_csv(CARTEIRA).set_index("ticker")["empresa"].to_dict()


def verificada(e):
    """Entidade confiável: ligada à carteira, encontrada por regra ou na lista de instituições do mercado."""
    return bool(e["ticker"]) or e["rotulo"] in POR_REGRA or e["texto"] in INSTITUICOES


st.set_page_config(page_title="Portfolio Radar", layout="centered")
st.title("Portfolio Radar")
st.caption("Cole o link de uma notícia financeira, ou a própria manchete, para ver se ela tende a ser **boa, neutra "
           "ou ruim para o acionista** da empresa citada e quais entidades aparecem nela.")

with st.form("entrada"):
    link = st.text_input("Link da notícia", placeholder="https://www.infomoney.com.br/...")
    manchete = st.text_area("…ou cole a manchete", height=80, help="Se você preencher os dois, vale a manchete.")
    exemplo = st.selectbox("…ou escolha um exemplo", [""] + EXEMPLOS)
    enviar = st.form_submit_button("Analisar", type="primary")

if not enviar:
    st.stop()

texto = manchete.strip() or exemplo
if not texto and link.strip():
    try:
        with st.spinner("Lendo o título da notícia..."):
            texto = manchete_do_link(link)
    except ValueError as erro:
        st.error(str(erro))
        st.stop()
if not texto:
    st.warning("Informe um link, uma manchete ou escolha um exemplo.")
    st.stop()

rotulo, confianca, probs = classifica(classificador(), texto)
ents = entidades(nlp(), texto)
nomes = nomes_carteira()
empresas = sorted({e["ticker"] for e in ents if e["ticker"]})

st.subheader(texto.replace("$", "\\$"))  # sem isso, "R$ ... R$" vira fórmula matemática

col1, col2 = st.columns(2)
col1.metric("Para o acionista", f"{ICONE[rotulo]} {rotulo}")
col1.caption(f"confiança de {confianca:.0%}")
col2.metric("Empresas da carteira", len(empresas))
col2.caption(", ".join(f"{nomes.get(t, t)} ({t})" for t in empresas) or "nenhuma")
for r in ["boa", "neutra", "ruim"]:
    st.progress(probs[r], text=f"{r}: {probs[r]:.0%}")

st.markdown("#### Entidades")
if ents:
    doc = {"text": normaliza(texto), "ents": [{"start": e["inicio"], "end": e["fim"], "label": e["rotulo"]} for e in ents]}
    st.markdown(displacy.render(doc, style="ent", manual=True, options={"colors": CORES}), unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([{
        "trecho": e["texto"],
        "tipo": e["rotulo"],
        "verificada": "sim" if verificada(e) else "não verificada",
        "empresa da carteira": f"{nomes.get(e['ticker'], '')} ({e['ticker']})" if e["ticker"] else "",
    } for e in ents]), hide_index=True, use_container_width=True)
    st.caption("**Não verificada:** pessoa, local ou organização encontrada só pelo modelo estatístico do spaCy, "
               "sem ligação com a carteira nem com a lista de instituições do mercado. Pode ser erro.")
else:
    st.info("Nenhuma entidade encontrada.")

st.divider()
st.caption(f"Sentimento: `{classificador().model.name_or_path}` · NER: spaCy `pt_core_news_lg` + regras da carteira "
           "(`src/ner.py`). Projeto acadêmico de PLN (Ibmec); não é recomendação de investimento.")
