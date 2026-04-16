"""
backend/knowledge_base/ingest.py — Ingest documents into ChromaDB.
ASCII-only version for Windows compatibility.
"""
import os
import sys
import shutil
import argparse
from pathlib import Path
from dotenv import load_dotenv

# --- Path Setup ---
SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path: sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(PROJECT_DIR / ".env")

CHROMA_PATH = os.getenv("CHROMA_PATH", str(SCRIPT_DIR / "chroma_db"))
COLLECTION_NAME = "hackbot_kb"

def embed_batch(texts: list[str]) -> list[list[float]]:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vecs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return [v.tolist() for v in vecs]

def main():
    parser = argparse.ArgumentParser(description="Ingest documents")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()

    print("=" * 55)
    print("  [INFO] HackBot Knowledge Base Ingestion")
    print("=" * 55)

    if args.reset and Path(CHROMA_PATH).exists():
        print(f"[!] Resetting ChromaDB at: {CHROMA_PATH}")
        shutil.rmtree(CHROMA_PATH)

    import chromadb
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    print("[INFO] No external documents to ingest. Check builtin_data.py")
    
    # Try to load builtin
    try:
        from builtin_data import BUILTIN_DOCUMENTS
        if BUILTIN_DOCUMENTS:
            texts = [d["content"] for d in BUILTIN_DOCUMENTS]
            ids = [f"builtin_{i}" for i in range(len(texts))]
            embeddings = embed_batch(texts)
            collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=[{"source": d["title"], "category": d.get("category", "builtin")}] * len(texts),
                ids=ids
            )
            print(f"[OK] Ingested {len(texts)} builtin entries.")
    except Exception as e:
        print(f"[ERROR] Builtin ingest failed: {e}")

    print("-" * 55)
    print("  [OK] Ingestion complete.")
    print("=" * 55)

if __name__ == "__main__":
    main()
