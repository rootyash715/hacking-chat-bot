"""
backend/rag_pipeline.py — Simplified Vector Store & Retriever.
Minimalist implementation for HackBot AI.
"""
import os
import chromadb
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
BACKEND_DIR = Path(__file__).resolve().parent
CHROMA_PATH = os.getenv("CHROMA_PATH", str(BACKEND_DIR / "knowledge_base" / "chroma_db"))
COLLECTION_NAME = "hackbot_kb"

# --- Embeddings (Local) ---
_model_cache = None

def _get_embed_model():
    global _model_cache
    if _model_cache is None:
        from sentence_transformers import SentenceTransformer
        _model_cache = SentenceTransformer("all-MiniLM-L6-v2")
    return _model_cache

def _embed(text: str) -> list[float]:
    model = _get_embed_model()
    vec = model.encode([text], show_progress_bar=False, convert_to_numpy=True)
    return vec[0].tolist()

# --- Retriever Class ---
class ChromaRetriever:
    def __init__(self, collection):
        self._collection = collection

    def invoke(self, query: str):
        from langchain_core.documents import Document
        embedding = _embed(query)
        try:
            results = self._collection.query(
                query_embeddings=[embedding],
                n_results=5,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            print(f"[WARN] Chroma query failed: {e}")
            return []

        docs = []
        for text, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            similarity = 1.0 - (dist / 2.0)
            if similarity >= 0.35: # Threshold
                docs.append(Document(page_content=text, metadata=meta or {}))
        return docs

# --- Load Function ---
def load_retriever() -> Optional[ChromaRetriever]:
    Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        count = collection.count()
        print(f"[INFO] Vector store ready: {count} chunks loaded.")
        return ChromaRetriever(collection)
    except Exception as e:
        print(f"[ERROR] Vector store init failed: {e}")
        return None

# --- Ingestion helper ---
def add_document_to_store(content: bytes, filename: str, title: str, category: str, retriever: Optional[ChromaRetriever]) -> int:
    if not retriever: return 0
    text = content.decode("utf-8", errors="ignore")
    
    # Simple chunking
    chunk_size, overlap = 512, 64
    chunks = [text[i : i + chunk_size].strip() for i in range(0, len(text), chunk_size - overlap)]
    chunks = [c for c in chunks if len(c) > 50]
    
    if not chunks: return 0
    
    existing = retriever._collection.count()
    embeddings = _get_embed_model().encode(chunks, show_progress_bar=False, convert_to_numpy=True)
    
    retriever._collection.add(
        documents=chunks,
        embeddings=[e.tolist() for e in embeddings],
        metadatas=[{"source": title, "category": category, "filename": filename}] * len(chunks),
        ids=[f"chunk_{existing + i}" for i in range(len(chunks))]
    )
    return len(chunks)
