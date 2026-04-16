# 📚 RAG Knowledge Base Guide — AI Hacking Chatbot

## What is RAG?

**Retrieval-Augmented Generation (RAG)** enhances the LLM by giving it access to a custom knowledge base. Instead of relying only on what the model was trained on, the chatbot **retrieves relevant documents** from a vector store each time a question is asked and injects them into the prompt.

```
Without RAG:  User Query → LLM → Answer (limited to training data)
With RAG:     User Query → Retrieve Docs → LLM + Context → Accurate Answer
```

---

## Knowledge Base Sources

### Tier 1 — Must Have

| Source | Format | Description | Where to Get |
|---|---|---|---|
| **MITRE ATT&CK** | JSON | Full TTP framework, adversary techniques | [attack.mitre.org](https://attack.mitre.org) → Download JSON |
| **OWASP Top 10** | PDF/HTML | Web vulnerability catalog | [owasp.org](https://owasp.org/Top10) |
| **CVE Database** | JSON | Known vulnerabilities (NVD) | [nvd.nist.gov](https://nvd.nist.gov/vuln/data-feeds) |
| **HackTricks** | Markdown | Real-world hacking techniques | [github.com/carlospolop/hacktricks](https://github.com/carlospolop/hacktricks) |
| **PayloadsAllTheThings** | Markdown | Payload cheatsheets for every vuln type | [github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings) |

### Tier 2 — Highly Recommended

| Source | Description |
|---|---|
| OWASP Testing Guide (OTG) | Step-by-step web pentest methodology |
| GTFOBins | Unix binaries for privilege escalation |
| LOLBAS | Windows LOLBins for living-off-the-land |
| Exploit-DB advisories | Real exploit writeups |
| Your own pentest reports | Personalized context |

---

## Directory Structure

```
backend/
└── knowledge_base/
    ├── raw/                    # Original documents (before processing)
    │   ├── mitre_attack.json
    │   ├── owasp_top10.pdf
    │   ├── hacktricks/         # Cloned HackTricks repo
    │   └── payloads/           # PayloadsAllTheThings
    ├── chroma_db/              # ChromaDB persisted vector store
    └── ingest.py               # Script to process & index documents
```

---

## Setting Up the Vector Store

### Step 1 — Install Dependencies

```bash
pip install chromadb langchain langchain-community sentence-transformers
```

### Step 2 — Clone Knowledge Sources

```bash
# HackTricks
git clone https://github.com/carlospolop/hacktricks backend/knowledge_base/raw/hacktricks

# PayloadsAllTheThings
git clone https://github.com/swisskyrepo/PayloadsAllTheThings backend/knowledge_base/raw/payloads
```

### Step 3 — Run the Ingestion Script

```bash
python backend/knowledge_base/ingest.py
```

---

## Ingestion Script (`ingest.py`)

```python
import os
from pathlib import Path
from langchain_community.document_loaders import (
    DirectoryLoader, TextLoader, PyPDFLoader, JSONLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# ── Config ──────────────────────────────────────────────
RAW_DIR      = "backend/knowledge_base/raw"
CHROMA_PATH  = "backend/knowledge_base/chroma_db"
EMBED_MODEL  = "all-MiniLM-L6-v2"

CHUNK_SIZE    = 512
CHUNK_OVERLAP = 64

# ── Load Documents ───────────────────────────────────────
loaders = [
    DirectoryLoader(f"{RAW_DIR}/hacktricks",  glob="**/*.md",  loader_cls=TextLoader),
    DirectoryLoader(f"{RAW_DIR}/payloads",    glob="**/*.md",  loader_cls=TextLoader),
    DirectoryLoader(f"{RAW_DIR}",             glob="**/*.txt", loader_cls=TextLoader),
    DirectoryLoader(f"{RAW_DIR}",             glob="**/*.pdf", loader_cls=PyPDFLoader),
]

docs = []
for loader in loaders:
    try:
        docs.extend(loader.load())
    except Exception as e:
        print(f"[WARN] Loader error: {e}")

print(f"[+] Loaded {len(docs)} documents")

# ── Split Into Chunks ────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ".", " "]
)
chunks = splitter.split_documents(docs)
print(f"[+] Split into {len(chunks)} chunks")

# ── Embed & Store ────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=CHROMA_PATH
)
vectorstore.persist()
print(f"[✓] Indexed {len(chunks)} chunks into ChromaDB at {CHROMA_PATH}")
```

---

## RAG Pipeline (`rag_pipeline.py`)

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_PATH = "backend/knowledge_base/chroma_db"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K       = 5          # Number of chunks to retrieve
MIN_SCORE   = 0.3        # Minimum similarity threshold

def load_retriever():
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    return vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": TOP_K, "score_threshold": MIN_SCORE}
    )

def retrieve_context(query: str, retriever) -> str:
    docs = retriever.get_relevant_documents(query)
    if not docs:
        return ""   # No context found → fallback to general LLM
    return "\n\n".join([
        f"[Source: {d.metadata.get('source','unknown')}]\n{d.page_content}"
        for d in docs
    ])
```

---

## Adding Custom Documents via API

```bash
# Add a PDF
curl -X POST http://localhost:8000/knowledge/add \
  -F "file=@my_pentest_notes.pdf" \
  -F "title=My Pentest Notes 2024" \
  -F "category=custom"

# Add a markdown file
curl -X POST http://localhost:8000/knowledge/add \
  -F "file=@sqli_cheatsheet.md" \
  -F "title=SQLi Cheatsheet" \
  -F "category=web"
```

---

## Embedding Model Comparison

| Model | Provider | Speed | Quality | Privacy |
|---|---|---|---|---|
| `all-MiniLM-L6-v2` | SentenceTransformers (local) | Very fast | ★★★☆☆ | ✅ 100% local |

**Recommendation**: Use `all-MiniLM-L6-v2` for lightweight deployments and total privacy.

---

## Updating the Knowledge Base

```bash
# Re-run ingest to add new documents
python backend/knowledge_base/ingest.py

# Or update only a specific directory
python backend/knowledge_base/ingest.py --source raw/hacktricks --append
```

> **Note**: Full re-ingestion overwrites the vector store. Use `--append` flag to add without reprocessing existing chunks.
