"""Treina e salva o classificador de sentimento da aplicação: embeddings multilíngues congelados + Regressão Logística.

É o mesmo modelo "embeddings_lr" do notebook 06 (mesmas bases pt + en, mesma separação com semente 42, mesmo
codificador e mesma Regressão Logística), que teve o maior F1 macro médio no teste (0,657). O notebook não exportava
os modelos; este script refaz o treino em CPU (sem GPU) e salva só a Regressão Logística, que é pequena.

Na raiz do repositório:
    python src/treina_modelo_app.py

Gera `modelos/embeddings_lr.joblib` e `modelos/previsoes_teste.csv` e confere o F1 macro nas 200 manchetes de teste.
"""
import sys
import time
import urllib.request
from pathlib import Path

import joblib
import pandas as pd
import torch
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))
from preprocessamento import limpa  # noqa: E402

CODIFICADOR = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
ROTULOS = ["boa", "neutra", "ruim"]
INDICE = {r: i for i, r in enumerate(ROTULOS)}
SEMENTE_DADOS = 42
RAW = RAIZ / "data" / "raw"
SAIDA = RAIZ / "modelos" / "embeddings_lr.joblib"
HF = "https://huggingface.co/datasets"


def le(caminho_hf, nome):
    arq = RAW / nome
    if not arq.exists():
        print(f"Baixando {caminho_hf}")
        urllib.request.urlretrieve(f"{HF}/{caminho_hf}", arq)
    if nome.endswith(".parquet"):
        return pd.read_parquet(arq)
    if nome.endswith(".jsonl"):
        return pd.read_json(arq, lines=True)
    return pd.read_csv(arq)


def base(textos, rotulos, nome, idioma):
    return pd.DataFrame({"texto": list(textos), "rotulo": list(rotulos), "base": nome, "idioma": idioma})


def bases_de_treino(teste):
    """As cinco bases públicas do notebook 06, sem as manchetes de teste."""
    lucas = le("lucas-leme/Sentiments-FinBERT-PT-BR/resolve/main/sentiments.csv", "finbert_ptbr_sentiments.csv")
    lucas = lucas[lucas["sentiment"].isin(["Positivo", "Neutro", "Negativo"])]
    pt_humano = base(lucas["text"], lucas["sentiment"].map({"Positivo": "boa", "Neutro": "neutra", "Negativo": "ruim"}),
                     "FinBERT-PT-BR (humano)", "pt")
    heitor = le("heitorrosa/financial-sentiment-pt/resolve/main/final.jsonl", "financial_sentiment_pt.jsonl")
    heitor = heitor[heitor["quality"] >= 0.6]
    pt_traduzido = base(heitor["translated"],
                        heitor["sentiment"].map({"positive": "boa", "neutral": "neutra", "negative": "ruim"}),
                        "financial-sentiment-pt (traduzido)", "pt")
    en = {"positive": "boa", "neutral": "neutra", "negative": "ruim"}
    sentfin = pd.concat([le(f"tasksource/sentfin/resolve/main/data/{s}-00000-of-00001.parquet", f"sentfin_{s}.parquet")
                         for s in ["train", "validation", "test"]])
    consistentes = sentfin.groupby("sentence1")["labels"].agg(lambda s: s.iloc[0] if s.nunique() == 1 else None).dropna()
    en_sentfin = base(consistentes.index, consistentes.map(en), "SEntFiN", "en")
    twitter = pd.concat([le(f"zeroshot/twitter-financial-news-sentiment/resolve/main/sent_{s}.csv", f"twitter_fin_{s}.csv")
                         for s in ["train", "valid"]])
    twitter["text"] = twitter["text"].str.replace(r"https?://\S+", "", regex=True).str.strip()
    en_twitter = base(twitter["text"], twitter["label"].map({0: "ruim", 1: "boa", 2: "neutra"}),
                      "Twitter Financial News", "en")
    fpb_arqs = {"train": "train-00000-of-00001-ab9a3b4799b09589", "valid": "valid-00000-of-00001-303e4ba2afe838d4",
                "test": "test-00000-of-00001-8bd1e21c671fb670"}
    fpb = pd.concat([le(f"ChanceFocus/en-fpb/resolve/main/data/{a}.parquet", f"fpb_{s}.parquet")
                     for s, a in fpb_arqs.items()])
    en_fpb = base(fpb["text"], fpb["answer"].map(en), "Financial PhraseBank", "en")

    todas = pd.concat([pt_humano, pt_traduzido, en_sentfin, en_twitter, en_fpb], ignore_index=True).dropna()
    todas["texto"] = todas["texto"].astype(str).str.strip()
    todas["limpo"] = todas["texto"].apply(limpa)
    todas = todas[todas["limpo"].str.len() > 0].drop_duplicates("texto")
    return todas[~todas["limpo"].isin(set(teste["manchete"].apply(limpa)))].reset_index(drop=True)


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    teste = pd.read_csv(RAIZ / "data" / "teste_revisao.csv")
    teste = teste[teste["rotulo"].isin(ROTULOS)].reset_index(drop=True)
    todas = bases_de_treino(teste)
    treino, valid = train_test_split(todas, test_size=0.1, stratify=todas["rotulo"], random_state=SEMENTE_DADOS)
    print(f"treino: {len(treino)} · validação: {len(valid)} · teste: {len(teste)}")

    dispositivo = "mps" if torch.backends.mps.is_available() else "cpu"
    codificador = SentenceTransformer(CODIFICADOR, device=dispositivo)
    inicio = time.time()
    E_tr, E_va, E_te = (codificador.encode(list(t), batch_size=64, show_progress_bar=True, normalize_embeddings=True)
                        for t in (treino["texto"], valid["texto"], teste["manchete"]))
    print(f"codificação: {(time.time() - inicio) / 60:.1f} min em {dispositivo}")

    lr = LogisticRegression(max_iter=3000, class_weight="balanced", C=1.0, random_state=42)
    lr.fit(E_tr, treino["rotulo"].map(INDICE))
    f1_valid = f1_score(valid["rotulo"].map(INDICE), lr.predict(E_va), average="macro")
    previsto = lr.predict(E_te)
    f1_teste = f1_score(teste["rotulo"].map(INDICE), previsto, average="macro")
    print(f"F1 macro validação: {f1_valid:.3f} · teste: {f1_teste:.3f} (notebook 06: 0,701 e 0,657)")
    print(classification_report(teste["rotulo"].map(INDICE), previsto, target_names=ROTULOS, digits=3))

    SAIDA.parent.mkdir(exist_ok=True)
    joblib.dump({"codificador": CODIFICADOR, "rotulos": ROTULOS, "lr": lr,
                 "f1_teste": round(f1_teste, 3), "f1_validacao": round(f1_valid, 3)}, SAIDA)
    print(f"Salvo em {SAIDA.relative_to(RAIZ)}")
    # Previsões no teste, para a aba "Radar da carteira" do app
    teste["previsto"] = [ROTULOS[i] for i in previsto]
    teste["pontuacao"] = lr.predict_proba(E_te).max(axis=1).round(3)
    teste[["id", "previsto", "pontuacao"]].to_csv(SAIDA.parent / "previsoes_teste.csv", index=False)


if __name__ == "__main__":
    main()
