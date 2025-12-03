# api2/02_build_faiss_index.py

import json
import numpy as np
import faiss
import os

BASE_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "data", "products_with_vectors.json")
INDEX_FILE = os.path.join(BASE_DIR, "data", "global_index.faiss")
CATALOG_FILE = os.path.join(BASE_DIR, "data", "catalog.json")

print(f"📂 Chargement des produits + vecteurs depuis {INPUT_FILE}...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

vectors = np.array([p["vector"] for p in products], dtype="float32")
d = vectors.shape[1]

print(f"🧠 Dimension des embeddings : {d}")
print(f"🧩 Nombre de produits      : {len(products)}")

index = faiss.IndexFlatIP(d)  # inner product = cos-sim car vecteurs normalisés
index.add(vectors)

print(f"💾 Sauvegarde de l'index FAISS dans {INDEX_FILE}...")
faiss.write_index(index, INDEX_FILE)

print(f"💾 Sauvegarde du catalogue dans {CATALOG_FILE}...")
with open(CATALOG_FILE, "w", encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print("✅ Index FAISS + catalog construits.")
