"""Lê a manchete de uma notícia a partir do link: só o título da página, nunca o texto da matéria."""
import html
import re
from html.parser import HTMLParser
from urllib.parse import urlparse

import requests

USER_AGENT = "Mozilla/5.0 (portfolio-radar; projeto academico)"
# Ordem de preferência: o título "editorial" das redes sociais costuma vir sem o nome do site
METAS = ["og:title", "twitter:title"]


class _Titulos(HTMLParser):
    def __init__(self):
        super().__init__()
        self.metas, self.titulo, self._no_title, self._achou = {}, "", False, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            chave = a.get("property") or a.get("name")
            if chave in METAS and a.get("content"):
                self.metas.setdefault(chave, a["content"])
        self._no_title = tag == "title" and not self._achou

    def handle_endtag(self, tag):
        if tag == "title" and self._no_title:
            self._no_title, self._achou = False, True  # só o primeiro <title>: o da página

    def handle_data(self, data):
        if self._no_title:
            self.titulo += data


def tira_nome_do_site(titulo):
    """'Petrobras lucra R$ 30 bi | InfoMoney' -> 'Petrobras lucra R$ 30 bi'. Só corta se o pedaço final for curto."""
    for sep in (" | ", " - ", " – ", " — "):
        if sep in titulo:
            inicio, fim = titulo.rsplit(sep, 1)
            if len(fim.split()) <= 4 and len(inicio.split()) >= 3:
                return inicio.strip()
    return titulo.strip()


def manchete_do_link(url, timeout=10):
    """Baixa a página e devolve a manchete. Levanta ValueError com uma mensagem para o usuário se não conseguir."""
    partes = urlparse(url.strip())
    if partes.scheme not in {"http", "https"} or not partes.netloc:
        raise ValueError("O link precisa começar com http:// ou https://.")
    if partes.netloc.endswith("news.google.com"):
        raise ValueError("Links do Google News abrem a notícia por JavaScript. Abra a notícia e copie o link do site, "
                         "ou cole a manchete no campo abaixo.")
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Não consegui abrir o link ({e.__class__.__name__}). Cole a manchete no campo abaixo.")
    if resp.encoding is None or resp.encoding.lower() == "iso-8859-1":  # padrão do requests sem charset: acentos quebram
        resp.encoding = resp.apparent_encoding
    p = _Titulos()
    p.feed(resp.text[:500_000])  # o título fica no começo da página
    bruto = next((p.metas[m] for m in METAS if m in p.metas), p.titulo)
    titulo = re.sub(r"\s+", " ", html.unescape(bruto)).strip()
    if not titulo:
        raise ValueError("A página não tem título. Cole a manchete no campo abaixo.")
    return tira_nome_do_site(titulo)


if __name__ == "__main__":
    assert tira_nome_do_site("Petrobras lucra R$ 30 bi no trimestre | InfoMoney") == "Petrobras lucra R$ 30 bi no trimestre"
    assert tira_nome_do_site("Vale - Notícias") == "Vale - Notícias"  # começo curto demais: não corta
    assert tira_nome_do_site("Itaú (ITUB4) sobe 3% - Money Times") == "Itaú (ITUB4) sobe 3%"
    print("ok")
