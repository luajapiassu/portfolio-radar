"""NER do Portfolio Radar: spaCy + EntityRuler (carteira e tickers) + regras para valores, percentuais e períodos.

Uso:
    from ner import carrega_nlp, entidades
    nlp = carrega_nlp("../data/carteira.csv")
    entidades(nlp, "Itaú (ITUB4) lucra R$ 12,4 bilhões no 2T26")
"""
import re

import pandas as pd
import spacy
from spacy.language import Language
from spacy.tokens import Span
from spacy.util import compile_prefix_regex, filter_spans

# Rótulos do spaCy em português -> rótulos do projeto. MISC fica de fora:
# no corpus WikiNER ele mistura eventos, obras e nacionalidades, que não usamos.
MAPA_SPACY = {"ORG": "ORG", "PER": "PESSOA", "LOC": "LOCAL"}
ROTULOS_REGRAS = {"TICKER", "VALOR", "PERCENTUAL", "PERIODO"}

# Código de negociação da B3: 4 letras + 3/4/5/6 (ações), 11 (units) ou 34 (BDRs). B3SA3 é a exceção com dígito.
TICKER = r"(?:[A-Z]{4}(?:3|4|5|6|11|34)|B3SA3)"

MESES = "janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro"

# Ordem importa: o primeiro padrão que casar num trecho fica com ele.
REGRAS = [
    ("VALOR", r"(?:R\$|US\$)\s?\d+(?:[.,]\d+)*(?:\s?(?i:mil|mi|milhão|milhões|bi|bilhão|bilhões|tri|trilhão|trilhões)\b)?"),
    ("PERCENTUAL", r"\d+(?:,\d+)?\s?%"),
    ("PERIODO", r"\b[1-4]T(?:\d{2})?\b"                       # 2T26, 3T
                rf"|\b[1-4][ºª°]\s?(?i:tri(?:mestre)?|semestre)\b"  # 2º trimestre, 2º tri
                rf"|\b(?i:{MESES})(?:\s+de\s+20\d{{2}})?\b"    # setembro, setembro de 2026
                r"|\b\d{1,2}/\d{1,2}/20\d{2}\b"                # 28/7/2026
                r"|\b20\d{2}\b"),                              # 2026
]


# Instituições que aparecem o tempo todo no noticiário de mercado: bancos e casas de análise, gestoras e órgãos públicos.
INSTITUICOES = [
    "JP Morgan", "J.P. Morgan", "JPMorgan", "Goldman Sachs", "Goldman", "Morgan Stanley", "Citi", "Citigroup",
    "Bank of America", "BofA", "UBS", "UBS BB", "Safra", "XP", "XP Investimentos", "Itaú BBA", "BB Investimentos",
    "BB-BI", "Bradesco BBI", "Genial", "Ágora", "Ativa", "Empiricus", "Credit Suisse", "HSBC", "Barclays",
    "BlackRock", "Vanguard", "Orbis", "Kinea", "Verde Asset",
    "STF", "STJ", "TCU", "CVM", "Cade", "CADE", "ANP", "Aneel", "Anatel", "ANS", "Banco Central", "Receita Federal",
    "União", "Ibama", "TJRJ", "TJSP",
]
# Siglas do jargão financeiro que o modelo estatístico confunde com organizações ou pessoas
SIGLAS = {"JCP", "ROE", "ROIC", "ACT", "CEO", "CFO", "OPA", "IPO", "PIB", "BDR", "BDRs", "Ibovespa", "Selic", "IA",
          "CLT", "Ebitda", "EBITDA", "IPCA", "DY"}


def normaliza(texto):
    """Unifica apóstrofos (Rede D’Or / Rede D'Or) sem mudar o tamanho do texto."""
    return texto.replace("’", "'").replace("‘", "'")


def padroes_carteira(nlp, carteira):
    """Um padrão do EntityRuler por apelido de cada empresa da carteira, com o ticker como id.

    Apelidos ambíguos (Vale, Vivo, Localiza...) exigem a grafia exata; os outros ignoram maiúsculas.
    """
    padroes = []
    for _, emp in carteira.iterrows():
        ambiguos = set(emp["apelidos_ambiguos"].split("|")) - {""}
        for apelido in emp["apelidos"].split("|"):
            if re.fullmatch(TICKER, apelido):
                continue  # códigos entram pelo padrão genérico de TICKER
            attr = "TEXT" if apelido in ambiguos else "LOWER"
            toks = [t.text if attr == "TEXT" else t.lower_ for t in nlp.make_doc(normaliza(apelido))]
            padroes.append({"label": "ORG", "id": emp["ticker"], "pattern": [{attr: t} for t in toks]})
    padroes.append({"label": "TICKER", "pattern": [{"TEXT": {"REGEX": f"^{TICKER}$"}}]})
    return padroes


@Language.component("regras_financeiras")
def regras_financeiras(doc):
    """Acrescenta VALOR, PERCENTUAL e PERIODO por expressão regular (como no exercício de R$ da aula 9)."""
    novas = []
    for rotulo, rx in REGRAS:
        for m in re.finditer(rx, doc.text):
            span = doc.char_span(m.start(), m.end(), label=rotulo, alignment_mode="expand")
            if span is not None:
                novas.append(span)
    novas = filter_spans(novas)
    # Onde a regra e o modelo estatístico se sobrepõem, fica a regra
    antigas = [e for e in doc.ents if not any(e.start < n.end and n.start < e.end for n in novas)]
    doc.ents = sorted(antigas + novas, key=lambda s: s.start)
    return doc


@Language.component("regras_mercado")
def regras_mercado(doc):
    """Corrige o modelo estatístico com o contexto do noticiário financeiro.

    - nome próprio logo antes de "(TICKER)" é empresa: "Cemig (CMIG4)" e "Casas Bahia (BHIA3)" viram ORG,
      mesmo que o modelo tenha dito LOCAL ou não tenha visto nada;
    - siglas do jargão (JCP, ROE, CEO...) deixam de ser entidade.
    """
    ents = [e for e in doc.ents if e.text not in SIGLAS]
    for i, tok in enumerate(doc[:-1]):
        if tok.text != "(" or not re.fullmatch(TICKER, doc[i + 1].text):
            continue
        inicio = i
        while inicio > 0 and _parte_de_nome(doc, inicio - 1):
            inicio -= 1
        while inicio < i and doc[inicio].is_lower:  # não começa com "de", "do"...
            inicio += 1
        if inicio == i or any(e.ent_id_ and e.start < i and inicio < e.end for e in ents):
            continue  # nada antes, ou já é uma empresa da carteira
        ents = [e for e in ents if not (e.start < i and inicio < e.end)] + [Span(doc, inicio, i, label="ORG")]
    doc.ents = sorted(ents, key=lambda s: s.start)
    return doc


def _parte_de_nome(doc, j):
    t = doc[j]
    if t.lower_ in {"de", "do", "da", "dos", "das", "&"}:
        return j > 0 and (doc[j - 1].is_title or doc[j - 1].is_upper)
    return (t.is_title or t.is_upper) and t.pos_ in {"PROPN", "NOUN", "ADJ"}


def carrega_nlp(arq_carteira, modelo="pt_core_news_lg", com_regras=True, com_mercado=True):
    """Pipeline do spaCy.

    - `com_regras=False`: modelo puro, a linha de base;
    - `com_regras=True, com_mercado=False`: + carteira, tickers, valores, percentuais e períodos;
    - `com_mercado=True`: + lista de instituições do mercado e as correções de `regras_mercado`.
    """
    nlp = spacy.load(modelo, exclude=["lemmatizer"])
    if com_regras:
        # "ex-Eletrobras" vira "ex-" + "Eletrobras", para o nome da empresa casar com o padrão
        prefixos = list(nlp.Defaults.prefixes) + [r"(?i:ex)-(?=[A-ZÀ-Ú])"]
        nlp.tokenizer.prefix_search = compile_prefix_regex(prefixos).search
        carteira = pd.read_csv(arq_carteira).fillna("")
        ruler = nlp.add_pipe("entity_ruler", before="ner", config={"overwrite_ents": True})
        ruler.add_patterns(padroes_carteira(nlp, carteira))
        if com_mercado:
            ruler.add_patterns([{"label": "ORG", "pattern": [{"TEXT": t.text} for t in nlp.make_doc(nome)]}
                                for nome in INSTITUICOES])
            nlp.add_pipe("regras_mercado", after="ner")
        nlp.add_pipe("regras_financeiras", after="ner")
        # Códigos alternativos (PETR3, EMBJ3, ELET6...) apontam para o ticker da carteira
        nlp.meta["codigo_para_ticker"] = {
            a: emp["ticker"] for _, emp in carteira.iterrows()
            for a in emp["apelidos"].split("|") if re.fullmatch(TICKER, a)
        }
    return nlp


def entidades(nlp, texto):
    """Entidades com os rótulos do projeto: lista de dicts (texto, rotulo, inicio, fim, ticker)."""
    codigos = nlp.meta.get("codigo_para_ticker", {})
    saida = []
    for e in nlp(normaliza(texto)).ents:
        rotulo = e.label_ if e.label_ in ROTULOS_REGRAS else MAPA_SPACY.get(e.label_)
        if rotulo is None:
            continue
        ticker = e.ent_id_ or (codigos.get(e.text, "") if rotulo == "TICKER" else "")
        saida.append({"texto": e.text, "rotulo": rotulo, "inicio": e.start_char, "fim": e.end_char, "ticker": ticker})
    return saida


def empresas_citadas(ents):
    """Tickers da carteira citados na manchete, pelo nome ou pelo código."""
    return sorted({e["ticker"] for e in ents if e["ticker"]})
