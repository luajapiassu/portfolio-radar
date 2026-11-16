"""Classificadores de sentimento do Portfolio Radar: boa / neutra / ruim para o acionista da empresa citada.

Dois modelos, com a mesma interface (`classifica(clf, manchete)`):

- "embeddings_lr" (padrão do app): embeddings multilíngues congelados + Regressão Logística, o maior F1 macro médio
  no teste (0,657, notebook 06). Precisa de `modelos/embeddings_lr.joblib`, gerado por `src/treina_modelo_app.py`.
- "finbert": FinBERT-PT-BR sem ajuste, a linha de base (F1 0,553, notebook 03). Também aceita outro modelo do
  Hugging Face ou uma pasta com `save_pretrained`, pela variável de ambiente RADAR_MODELO.
"""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ_EMBEDDINGS_LR = RAIZ / "modelos" / "embeddings_lr.joblib"
MODELO_FINBERT = "lucas-leme/FinBERT-PT-BR"

# Nomes de classe que aparecem nos modelos usados no projeto -> rótulos do projeto
MAPA = {
    "positive": "boa", "positivo": "boa", "boa": "boa",
    "neutral": "neutra", "neutro": "neutra", "neutra": "neutra",
    "negative": "ruim", "negativo": "ruim", "ruim": "ruim",
}


class EmbeddingsLR:
    """Codificador de frases congelado + Regressão Logística treinada nas bases públicas (notebook 06)."""

    def __init__(self, arquivo=ARQ_EMBEDDINGS_LR):
        import joblib
        from sentence_transformers import SentenceTransformer

        salvo = joblib.load(arquivo)
        self.lr, self.rotulos = salvo["lr"], salvo["rotulos"]
        self.codificador = SentenceTransformer(salvo["codificador"], device="cpu")
        self.nome = "Embeddings multilíngues + Regressão Logística"
        self.detalhe = f"`{salvo['codificador'].split('/')[-1]}` congelado · F1 macro no teste {salvo['f1_teste']:.3f}"

    def probabilidades(self, manchete):
        e = self.codificador.encode([manchete], normalize_embeddings=True)
        return dict(zip(self.rotulos, self.lr.predict_proba(e)[0].tolist()))


class FinBERT:
    """Pipeline do Hugging Face. O FinBERT-PT-BR usa sigmoide; as pontuações são reescaladas para somar 1."""

    def __init__(self, modelo=MODELO_FINBERT):
        from transformers import pipeline

        self.clf = pipeline("text-classification", model=modelo, top_k=None)
        rotulos = {MAPA.get(str(n).lower()) for n in self.clf.model.config.id2label.values()}
        if rotulos != {"boa", "neutra", "ruim"}:
            raise ValueError(f"{modelo}: classes {self.clf.model.config.id2label} não correspondem a boa/neutra/ruim")
        self.nome = "FinBERT-PT-BR sem ajuste (linha de base)" if modelo == MODELO_FINBERT else modelo
        self.detalhe = f"`{modelo}` · F1 macro no teste 0.553" if modelo == MODELO_FINBERT else f"`{modelo}`"

    def probabilidades(self, manchete):
        saida = self.clf(manchete, truncation=True)
        saida = saida[0] if saida and isinstance(saida[0], list) else saida
        brutas = {MAPA[s["label"].lower()]: s["score"] for s in saida}
        total = sum(brutas.values())
        return {r: p / total for r, p in brutas.items()}


def carrega_classificador(modelo=None):
    """`modelo`: "embeddings_lr", "finbert", nome no Hugging Face ou pasta. Sem nada, usa RADAR_MODELO ou o melhor."""
    modelo = modelo or os.environ.get("RADAR_MODELO") or ("embeddings_lr" if ARQ_EMBEDDINGS_LR.exists() else "finbert")
    if modelo == "embeddings_lr":
        return EmbeddingsLR()
    return FinBERT(MODELO_FINBERT if modelo == "finbert" else modelo)


def classifica(clf, manchete):
    """Devolve (rótulo, pontuação, {rótulo: pontuação}) para uma manchete."""
    probs = clf.probabilidades(manchete)
    rotulo = max(probs, key=probs.get)
    return rotulo, probs[rotulo], probs
