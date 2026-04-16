"""
backend/rag_pipeline.py — Vector store retriever using native ChromaDB client.

Uses chromadb's Python client directly to avoid pydantic v1/v2 conflicts
introduced by LangChain's compatibility shim.
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR     = Path(__file__).resolve().parent
CHROMA_PATH     = os.getenv("CHROMA_PATH", str(BACKEND_DIR / "knowledge_base" / "chroma_db"))
EMBED_PROVIDER  = os.getenv("EMBEDDING_PROVIDER", "ollama").lower()
EMBED_MODEL     = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
COLLECTION_NAME = "hackbot_kb"
TOP_K           = 5
MIN_SCORE       = 0.30   # cosine similarity threshold (lower = more permissive)


# ── Embedding ──────────────────────────────────────────────
_embed_model_cache = None

def _get_embed_model():
    """Load local embedding model."""
    global _embed_model_cache
    if _embed_model_cache is not None:
        return _embed_model_cache

    from sentence_transformers import SentenceTransformer
    _embed_model_cache = SentenceTransformer("all-MiniLM-L6-v2")
    
    return _embed_model_cache


def _embed(text: str) -> list[float]:
    model = _get_embed_model()
    if hasattr(model, "embed_query"):
        return model.embed_query(text)
    else:
        vec = model.encode([text], show_progress_bar=False, convert_to_numpy=True)
        return vec[0].tolist()


# ── Custom Retriever ───────────────────────────────────────

class ChromaRetriever:
    """
    Thin retriever wrapping the native ChromaDB collection.
    Mimics the LangChain retriever interface so existing chatbot code works.
    """

    def __init__(self, collection):
        self._collection = collection

    def get_relevant_documents(self, query: str):
        """Return list of LangChain-style Document objects."""
        from langchain_core.documents import Document

        query_embedding = _embed(query)
        try:
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=TOP_K,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            print(f"[!] ChromaDB query failed: {e}")
            return []

        docs = []
        documents  = results.get("documents", [[]])[0]
        metadatas  = results.get("metadatas", [[]])[0]
        distances  = results.get("distances", [[]])[0]

        for text, meta, dist in zip(documents, metadatas, distances):
            # ChromaDB cosine distance: 0 = identical, 2 = opposite
            # Convert to similarity score: similarity = 1 - dist/2
            similarity = 1.0 - (dist / 2.0)
            if similarity >= MIN_SCORE:
                docs.append(Document(page_content=text, metadata=meta or {}))

        return docs

    # LangChain compatibility alias
    def invoke(self, query: str):
        return self.get_relevant_documents(query)


# ── Load Retriever ─────────────────────────────────────────

def load_retriever() -> Optional[ChromaRetriever]:
    """
    Load ChromaDB and return a retriever, or None if the store is unavailable.
    """
    import chromadb

    Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)

    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        count = collection.count()
        print(f"[✓] Vector store loaded — {count} chunks in ChromaDB")

        if count == 0:
            print("    ℹ️  Knowledge base is empty. Run: python backend/knowledge_base/ingest.py")
            _auto_ingest(collection)
            count = collection.count()
            if count == 0:
                print("    [!] RAG disabled — no data ingested")
                return None

        return ChromaRetriever(collection)

    except Exception as e:
        print(f"[!] Vector store initialization failed: {e}")
        print("    RAG will be disabled.")
        return None


def _auto_ingest(collection):
    """Auto-ingest built-in data if knowledge base is empty."""
    try:
        kb_dir = str(BACKEND_DIR / "knowledge_base")
        if kb_dir not in __import__("sys").path:
            __import__("sys").path.insert(0, kb_dir)
        try:
            from builtin_data import BUILTIN_DOCUMENTS
        except ImportError:
            from knowledge_base.builtin_data import BUILTIN_DOCUMENTS

        if not BUILTIN_DOCUMENTS:
            return

        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")

        texts = [e["content"] for e in BUILTIN_DOCUMENTS]
        metas = [{"source": e["title"], "category": e.get("category", "builtin"), "filename": "builtin"}
                 for e in BUILTIN_DOCUMENTS]
        ids   = [f"builtin_{i}" for i in range(len(BUILTIN_DOCUMENTS))]

        BATCH = 64
        for i in range(0, len(texts), BATCH):
            batch_texts = texts[i:i+BATCH]
            embeddings  = model.encode(batch_texts, show_progress_bar=False, convert_to_numpy=True)
            collection.add(
                documents=batch_texts,
                embeddings=[e.tolist() for e in embeddings],
                metadatas=metas[i:i+BATCH],
                ids=ids[i:i+BATCH]
            )
        print(f"    [✓] Auto-ingested {len(BUILTIN_DOCUMENTS)} built-in knowledge entries")

    except Exception as e:
        print(f"    [!] Auto-ingest failed: {e}")


# ── Add Document ───────────────────────────────────────────

def add_document_to_store(
    content: bytes,
    filename: str,
    title: str,
    category: str,
    retriever: Optional[ChromaRetriever]
) -> int:
    """Add a new document to the vector store."""
    import chromadb
    from pathlib import Path as _Path
    from sentence_transformers import SentenceTransformer

    ext = _Path(filename).suffix.lower()
    if ext == ".pdf":
        import io, PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = "\n".join(p.extract_text() or "" for p in reader.pages)
    else:
        text = content.decode("utf-8", errors="ignore")

    # Simple chunking
    chunk_size, overlap = 512, 64
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i+chunk_size].strip()
        if chunk:
            chunks.append(chunk)

    if not chunks:
        return 0

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    existing = collection.count()
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, show_progress_bar=False, convert_to_numpy=True)

    collection.add(
        documents=chunks,
        embeddings=[e.tolist() for e in embeddings],
        metadatas=[{"source": title, "category": category, "filename": filename}] * len(chunks),
        ids=[f"chunk_{existing + i}" for i in range(len(chunks))]
    )

    print(f"[+] Added {len(chunks)} chunks from '{title}'")
    return len(chunks)
