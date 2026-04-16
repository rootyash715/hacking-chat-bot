"""
backend/knowledge_base/ingest.py — Ingest documents into ChromaDB vector store

Usage:
    python backend/knowledge_base/ingest.py [--source-dir <path>] [--reset] [--builtin-only]

This script uses the native ChromaDB client directly (no LangChain wrapper)
to avoid pydantic v1/v2 compatibility conflicts.
"""
import os
import sys
import shutil
import argparse
from pathlib import Path
from dotenv import load_dotenv

# ── Path Setup ────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_DIR = BACKEND_DIR.parent

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

load_dotenv(PROJECT_DIR / ".env")

CHROMA_PATH        = os.getenv("CHROMA_PATH", str(SCRIPT_DIR / "chroma_db"))
DEFAULT_RAW_DIR    = SCRIPT_DIR / "raw"
EMBED_MODEL        = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
EMBED_PROVIDER     = os.getenv("EMBEDDING_PROVIDER", "ollama").lower()
COLLECTION_NAME    = "hackbot_kb"

CHUNK_SIZE         = 512
CHUNK_OVERLAP      = 64
SUPPORTED_EXTS     = {".md", ".txt", ".pdf", ".rst", ".html"}


# ── Embedding ─────────────────────────────────────────────

def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts. Uses sentence-transformers locally (avoids pydantic conflict)."""
    from sentence_transformers import SentenceTransformer
    _model_name = "all-MiniLM-L6-v2"   # fast local model; no Ollama dependency for embedding
    model = SentenceTransformer(_model_name)
    vecs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return [v.tolist() for v in vecs]


# ── Text splitting ─────────────────────────────────────────

def split_text(text: str) -> list[str]:
    """Simple recursive character splitter."""
    if len(text) <= CHUNK_SIZE:
        return [text] if text.strip() else []

    separators = ["\n## ", "\n### ", "\n\n", "\n", ". ", " "]
    for sep in separators:
        parts = text.split(sep)
        if len(parts) > 1:
            chunks, current = [], ""
            for part in parts:
                candidate = (current + sep + part) if current else part
                if len(candidate) > CHUNK_SIZE:
                    if current.strip():
                        chunks.append(current.strip())
                    current = part
                else:
                    current = candidate
            if current.strip():
                chunks.append(current.strip())
            # Add overlap
            result = []
            for i, chunk in enumerate(chunks):
                result.append(chunk)
            return result
    # Fallback: hard split
    return [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP)]


# ── Document loading ──────────────────────────────────────

def load_documents(source_dir: Path) -> list[dict]:
    docs = []
    if not source_dir.exists():
        print(f"  ℹ️  Source dir not found: {source_dir}")
        return docs
    for filepath in sorted(source_dir.rglob("*")):
        if not filepath.is_file() or filepath.suffix.lower() not in SUPPORTED_EXTS:
            continue
        try:
            if filepath.suffix.lower() == ".pdf":
                import PyPDF2
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    text = "\n".join(p.extract_text() or "" for p in reader.pages)
            else:
                text = filepath.read_text(encoding="utf-8", errors="ignore")
            if len(text.strip()) < 50:
                continue
            relative = filepath.relative_to(source_dir)
            docs.append({
                "content": text,
                "source": str(relative).replace("\\", "/"),
                "category": relative.parts[0] if len(relative.parts) > 1 else "general",
                "filename": filepath.name,
            })
        except Exception as e:
            print(f"  [!] Failed to load {filepath.name}: {e}")
    print(f"  [✓] Loaded {len(docs)} documents from {source_dir}")
    return docs


def load_builtin_data() -> list[dict]:
    try:
        from builtin_data import BUILTIN_DOCUMENTS
    except ImportError:
        try:
            from knowledge_base.builtin_data import BUILTIN_DOCUMENTS
        except ImportError:
            print("  [!] builtin_data.py not found")
            return []
    docs = [
        {"content": e["content"], "source": e["title"], "category": e.get("category", "builtin"), "filename": "builtin"}
        for e in BUILTIN_DOCUMENTS
    ]
    print(f"  [✓] Loaded {len(docs)} built-in knowledge entries")
    return docs


# ── ChromaDB ingestion ────────────────────────────────────

def ingest(all_docs: list[dict], chroma_path: str, reset: bool = False):
    import chromadb

    if reset and Path(chroma_path).exists():
        print(f"\n[!] Resetting ChromaDB at: {chroma_path}")
        shutil.rmtree(chroma_path)

    Path(chroma_path).mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=chroma_path)

    # Get or create collection
    try:
        if reset:
            try:
                client.delete_collection(COLLECTION_NAME)
            except Exception:
                pass
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    except Exception as e:
        print(f"  [✗] Failed to get/create collection: {e}")
        sys.exit(1)

    # Chunk all docs
    print(f"\n[3/4] Chunking {len(all_docs)} documents...")
    all_chunks, all_metas, all_ids = [], [], []
    chunk_idx = collection.count()  # continue from existing

    for doc in all_docs:
        chunks = split_text(doc["content"])
        for chunk in chunks:
            if not chunk.strip():
                continue
            all_chunks.append(chunk)
            all_metas.append({"source": doc["source"], "category": doc["category"], "filename": doc["filename"]})
            all_ids.append(f"chunk_{chunk_idx}")
            chunk_idx += 1

    print(f"  [✓] {len(all_chunks)} chunks ready")

    # Embed in batches
    print(f"\n[4/4] Embedding and storing in ChromaDB...")
    BATCH = 64
    for i in range(0, len(all_chunks), BATCH):
        batch_texts  = all_chunks[i:i+BATCH]
        batch_metas  = all_metas[i:i+BATCH]
        batch_ids    = all_ids[i:i+BATCH]
        embeddings   = embed_texts(batch_texts)
        collection.add(documents=batch_texts, embeddings=embeddings, metadatas=batch_metas, ids=batch_ids)
        print(f"  → Stored batch {i//BATCH + 1}/{(len(all_chunks)-1)//BATCH + 1} ({len(batch_texts)} chunks)")

    total = collection.count()
    print(f"\n  [✓] ChromaDB now contains {total} total chunks")


# ── Main ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ingest documents into HackBot knowledge base")
    parser.add_argument("--source-dir", default=str(DEFAULT_RAW_DIR))
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--builtin-only", action="store_true")
    args = parser.parse_args()

    print("=" * 55)
    print("  📚 HackBot Knowledge Base Ingestion")
    print("=" * 55)

    chroma_path = os.path.abspath(CHROMA_PATH)

    # Load documents
    print("\n[1/4] Loading embedding model (sentence-transformers)...")
    print(f"  [✓] Will use sentence-transformers/all-MiniLM-L6-v2")

    print("\n[2/4] Loading documents...")
    all_docs = load_builtin_data()
    if not args.builtin_only:
        source_dir = Path(args.source_dir)
        if source_dir.exists():
            all_docs.extend(load_documents(source_dir))
        else:
            print(f"  ℹ️  No external docs at {source_dir}")

    if not all_docs:
        print("\n[✗] No documents to ingest!")
        sys.exit(1)

    ingest(all_docs, chroma_path, reset=args.reset)

    print("\n" + "=" * 55)
    print("  ✅ Ingestion complete!")
    print("=" * 55)


if __name__ == "__main__":
    main()
