# api2/search_engine.py

import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")

INDEX_FILE = os.path.join(DATA_DIR, "global_index.faiss")
CATALOG_FILE = os.path.join(DATA_DIR, "catalog.json")

TEXT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CROSS_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

print("📦 Chargement du modèle bi-encodeur...")
text_model = SentenceTransformer(TEXT_MODEL)

print("📦 Chargement du cross-encodeur...")
cross_model = CrossEncoder(CROSS_MODEL)

print("📂 Chargement de l'index FAISS...")
index = faiss.read_index(INDEX_FILE)


print("📂 Chargement du catalogue produits...")
with open(CATALOG_FILE, "r", encoding="utf-8") as f:
    catalog = json.load(f)


def encode_query(query: str) -> np.ndarray:
    q = text_model.encode(query, normalize_embeddings=True)
    return q.astype("float32").reshape(1, -1)


def filter_by_type_for_query(query, products):
    q = query.lower()

    # Cas "pc portable"
    if "pc portable" in q or "ordinateur portable" in q or "laptop" in q:
        allowed = {"laptop"}
        typed = [p for p in products if p.get("product_type") in allowed]

        # si on a trouvé au moins 1 laptop, on ne garde que ça
        if typed:
            return typed

        # sinon, on ne filtre pas → on renvoie quand même les produits initiaux
        return products

    # Cas "chargeur"
    if "chargeur" in q or "adaptateur" in q:
        allowed = {"charger"}
        typed = [p for p in products if p.get("product_type") in allowed]

        if typed:
            return typed

        return products

    # Sinon, pas de filtre
    return products



def adaptive_filter_by_vector(query_vec, products, min_sim=0.40, min_keep=20):
    q = query_vec.reshape(-1).astype("float32")
    filtered = []

    for p in products:
        v = np.array(p["vector"], dtype="float32")
        sim = float(np.dot(q, v))  # cos-sim

        if sim >= min_sim:
            filtered.append((p, sim))

    if len(filtered) < min_keep:
        return products[:min_keep]

    filtered.sort(key=lambda x: x[1], reverse=True)
    return [p for p, _ in filtered]


def lexical_score(query, product):
    q_words = query.lower().split()
    title = (product.get("title") or "").lower()

    score = 0.0
    if all(w in title for w in q_words):
        score += 1.0
    if query.lower() in title:
        score += 0.5
    return score


def category_boost(query, product):
    cat = (product.get("category_norm") or product.get("category") or "").lower()
    q = query.lower()
    boost = 0.0

    if "pc portable" in q or "ordinateur portable" in q or "laptop" in q:
        if "pc portable" in cat or "laptop" in cat:
            boost += 0.8
        if "accessoire" in cat or "chargeur" in cat or "sacoche" in cat:
            boost -= 0.5

    return boost


def combined_score(query, product, ce_score):
    lex = lexical_score(query, product)
    cat_b = category_boost(query, product)
    return 0.6 * ce_score + 0.3 * lex + 0.1 * cat_b


def search(query: str,
           k: int = 20,
           faiss_k: int = 200,
           max_crossencoder: int = 40):
    # 1) FAISS
    qv = encode_query(query)
    scores, idxs = index.search(qv, faiss_k)
    candidates = [catalog[i] for i in idxs[0]]

    # 2) filtre métier par type
    candidates = filter_by_type_for_query(query, candidates)

    # 3) filtre adaptatif vecteur
    filtered = adaptive_filter_by_vector(qv, candidates, min_sim=0.40, min_keep=min(20, len(candidates)))

    # 4) rerank cross-encoder sur un sous-ensemble
    top_for_ce = filtered[:max_crossencoder]

    pairs = [
        (query, f"{p['title']} | {p.get('brand','')} | {p.get('category_norm', p.get('category',''))}")
        for p in top_for_ce
    ]

    ce_scores = cross_model.predict(pairs)

    results = []
    for p, ce_s in zip(top_for_ce, ce_scores):
        score = combined_score(query, p, ce_s)
        results.append((p, score))

    ranked = sorted(results, key=lambda x: x[1], reverse=True)
    return ranked[:k]
