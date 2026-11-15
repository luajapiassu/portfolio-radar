"""Classificador de sentimento do Portfolio Radar: boa / neutra / ruim para o acionista da empresa citada.

O modelo padrão é o FinBERT-PT-BR sem ajuste (notebook 03). Para usar outro modelo do Hugging Face, ou uma pasta
com um modelo ajustado (`save_pretrained`), defina a variável de ambiente RADAR_MODELO antes de abrir o app:

    RADAR_MODELO=../modelos/bertimbau-ajustado streamlit run app.py
"""
import os

from transformers import pipeline

MODELO_PADRAO = "lucas-leme/FinBERT-PT-BR"

# Nomes de classe que aparecem nos modelos usados no projeto -> rótulos do projeto
MAPA = {
    "positive": "boa", "positivo": "boa", "boa": "boa",
    "neutral": "neutra", "neutro": "neutra", "neutra": "neutra",
    "negative": "ruim", "negativo": "ruim", "ruim": "ruim",
}


def carrega_classificador(modelo=None):
    modelo = modelo or os.environ.get("RADAR_MODELO", MODELO_PADRAO)
    clf = pipeline("text-classification", model=modelo, top_k=None)
    rotulos = {MAPA.get(str(n).lower()) for n in clf.model.config.id2label.values()}
    if rotulos != {"boa", "neutra", "ruim"}:
        raise ValueError(f"{modelo}: classes {clf.model.config.id2label} não correspondem a boa/neutra/ruim")
    return clf


def classifica(clf, manchete):
    """Devolve (rótulo, confiança, {rótulo: probabilidade}) para uma manchete."""
    saida = clf(manchete, truncation=True)
    saida = saida[0] if saida and isinstance(saida[0], list) else saida
    brutas = {MAPA[s["label"].lower()]: s["score"] for s in saida}
    total = sum(brutas.values())  # o FinBERT-PT-BR usa sigmoide; normaliza para somar 1
    probs = {r: p / total for r, p in brutas.items()}
    rotulo = max(probs, key=probs.get)
    return rotulo, probs[rotulo], probs
