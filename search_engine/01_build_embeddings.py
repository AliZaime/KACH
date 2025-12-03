# api2/01_build_embeddings.py

import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import os

BASE_DIR = os.path.dirname(__file__)
INPUT_FILE = os.path.join(BASE_DIR, "data", "all_products_with_taxonomy.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "products_with_vectors.json")

TEXT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

print("📦 Chargement du modèle de texte...")
model = SentenceTransformer(TEXT_MODEL)  # device="cuda" si tu as un GPU

print(f"📂 Chargement des produits depuis {INPUT_FILE}...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

print(f"➡️ {len(products)} produits trouvés")


def build_product_text(p: dict) -> str:
    parts = [
        p.get("title") or "",
        p.get("brand") or "",
        p.get("category_norm") or p.get("category") or "",
        p.get("top_category") or "",
        p.get("sub_category") or "",
        p.get("sub_sub_category") or "",
    ]

    desc = p.get("description")
    if desc:
        parts.append(desc)

    ts = p.get("technical_sheet")
    if isinstance(ts, dict):
        for k, v in ts.items():
            parts.append(f"{k}: {v}")
    elif isinstance(ts, list):
        for item in ts:
            parts.append(f"{item.get('label','')}: {item.get('value','')}")

    parts = [str(x).strip() for x in parts if x]
    return " ; ".join(parts)


def infer_product_type(p):
    """OPTIONNEL mais très utile pour 'pc portable' vs accessoires."""
    title = (p.get("title") or "").lower()
    cat = (p.get("category_norm") or p.get("category") or "").lower()

    if "pc portable" in title or "laptop" in title or "ordinateur portable" in title:
        return "laptop"
    if "chargeur" in title or "adaptateur" in title:
        return "charger"
    if "sacoche" in title or "housse" in title or "bag" in title:
        return "bag"
    if "refroidisseur" in title or "cooler" in title:
        return "cooler"
    if "ram" in title or "barrette mémoire" in title:
        return "ram"
    return "other"


print("🧱 Construction des textes produits...")
texts = [build_product_text(p) for p in products]

print("🚀 Génération des embeddings (batch + normalisation)...")
embeddings = model.encode(
    texts,
    batch_size=128,
    show_progress_bar=True,
    normalize_embeddings=True  # très important
)

new_products = []
for p, vec in tqdm(list(zip(products, embeddings)), total=len(products)):
    p["vector"] = vec.tolist()
    p["product_type"] = infer_product_type(p)  # ajoute le type produit
    new_products.append(p)

print(f"\n💾 Sauvegarde dans {OUTPUT_FILE}...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(new_products, f, ensure_ascii=False, indent=2)

print("✅ Terminé : vecteurs + product_type ajoutés.")
