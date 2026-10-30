"""Limpeza de manchetes para os classificadores (TF-IDF e redes neurais).

Segue o pipeline da aula 2, com duas decisões próprias do problema:
- números, valores, percentuais, trimestres e tickers viram marcadores (<valor>, <pct>, <trimestre>, <num>, <ticker>):
  o modelo deve aprender "lucra <valor>", não decorar "R$ 12,4 bilhões";
- não removemos stopwords nem aplicamos stemming: palavras como "não", "mas" e "após" mudam o sentido
  da manchete, e a camada de embedding aprende sozinha que "cai" e "caem" são parecidos.
"""
import re

from ner import TICKER

ESCALA = r"(?:mil|mi|milhão|milhões|bi|bilhão|bilhões|tri|trilhão|trilhões)"


def limpa(texto):
    t = str(texto).replace("’", "'").replace("‘", "'")
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(rf"\b{TICKER}\b", " <ticker> ", t)  # antes de minúsculas: o padrão exige maiúsculas
    t = t.lower()
    t = re.sub(rf"(?:r\$|us\$)\s?\d+(?:[.,]\d+)*(?:\s?{ESCALA}\b)?", " <valor> ", t)
    t = re.sub(r"\d+(?:,\d+)?\s?%", " <pct> ", t)
    t = re.sub(r"\b[1-4]t\d{2}\b|\b[1-4][ºª°]\s?tri(?:mestre)?\b", " <trimestre> ", t)
    t = re.sub(r"\d+(?:[.,]\d+)*", " <num> ", t)
    t = re.sub(r"[^\w<>\s-]", " ", t)  # pontuação vira espaço; hífen fica ("preço-alvo")
    t = re.sub(r"(?<!\w)-|-(?!\w)", " ", t)
    return re.sub(r"\s+", " ", t).strip()
