# 🚀 Setup & Deployment Guide — AI Hacking Chatbot

## Prerequisites

| Requirement | Version | Purpose |
|---|---|---|
| Python | 3.11+ | Backend runtime |
| pip | Latest | Package manager |
| Node.js (optional) | 18+ | Only if serving frontend via npm |
| Ollama (if local LLM) | Latest | Run Llama3/Mistral locally |
| Git | Any | Clone knowledge sources |

---

## Option A — Local Setup with Ollama (Free, Private)

### Step 1 — Install Ollama

**Windows:**
```
Download from: https://ollama.ai/download
Run the installer, then open a new terminal.
```

**Linux/Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2 — Pull Required Models

```bash
# The main chat model (7B — runs on 8GB RAM)
ollama pull llama3

# Alternative: smaller & faster
ollama pull mistral

# Embedding model (for RAG)
ollama pull nomic-embed-text

# Optional: coding-focused model
ollama pull deepseek-coder
```

### Step 3 — Clone & Set Up the Project

```bash
# Navigate to the project
cd "hacking chat bot"

# Create Python virtual environment
python -m venv venv

# Activate the venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt
```

### Step 4 — Configure Environment Variables

```bash
# Copy the example file
copy .env.example .env

# Edit .env
notepad .env
```

Set the following in `.env`:
```env
# ── LLM Provider ──────────────────────────
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3

# ── Embeddings ─────────────────────────────
EMBEDDING_PROVIDER=local
EMBEDDING_MODEL=all-MiniLM-L6-v2

# ── Vector Store ───────────────────────────
CHROMA_PATH=backend/knowledge_base/chroma_db

# ── Server ─────────────────────────────────
PORT=8000
DEBUG=true

# ── Safety ─────────────────────────────────
SAFETY_FILTER=true
RATE_LIMIT=30                # requests per minute
```

### Step 5 — Build the Knowledge Base

```bash
# Clone HackTricks (large — ~500MB, takes a few minutes)
git clone --depth=1 https://github.com/carlospolop/hacktricks backend/knowledge_base/raw/hacktricks

# Clone PayloadsAllTheThings
git clone --depth=1 https://github.com/swisskyrepo/PayloadsAllTheThings backend/knowledge_base/raw/payloads

# Run ingestion (processes and indexes everything into ChromaDB)
python backend/knowledge_base/ingest.py
```

> ⏳ This step takes 5–15 minutes depending on your CPU and the size of the knowledge base.

### Step 6 — Start the Backend

```bash
python backend/main.py
```

Expected output:
```
[✓] Vector store loaded — 14,832 chunks
[✓] LLM: Ollama/llama3 connected
[✓] HackBot API running on http://localhost:8000
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 7 — Open the Frontend

Open `frontend/index.html` directly in your browser:
```
File → Open → navigate to frontend/index.html
```

Or serve it with Python:
```bash
python -m http.server 3000 --directory frontend
# Then open: http://localhost:3000
```

**You're ready!** Open the browser and start chatting.

---



## Running the Backend

```bash
# Development (auto-reload on file changes)
uvicorn backend.main:app --reload --port 8000

# Production
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Verifying Everything Works

```bash
# 1. Health check
curl http://localhost:8000/health

# Expected:
# {"status":"ok","llm_provider":"ollama","model":"llama3","knowledge_chunks":14832}

# 2. Test chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What is SQL injection?","session_id":"test-1"}'
```

---

## Common Issues & Fixes

| Problem | Cause | Fix |
|---|---|---|
| `Connection refused :8000` | Backend not started | Run `python backend/main.py` |
| `Ollama not found` | Ollama not installed | Install from ollama.ai |
| `Model not found` | Model not pulled | Run `ollama pull llama3` |
| `ChromaDB empty` | Ingest not run | Run `ingest.py` |
| `OPENAI_API_KEY invalid` | Wrong key | Check key on platform.openai.com |
| `Out of memory` | Model too large | Use `mistral` (smaller) or add more RAM |
| `Slow responses` | Large model, weak CPU | Use `ollama pull llama3:8b-instruct-q4_0` (quantized) |
| `CORS error` | Frontend blocked | Add frontend URL to `ALLOWED_ORIGINS` in `.env` |

---

## Docker Deployment (Optional)

```dockerfile
# Dockerfile (backend)
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t hackbot-api .
docker run -p 8000:8000 --env-file .env hackbot-api
```

---

## Production Checklist

- [ ] Set `DEBUG=false` in `.env`
- [ ] Add `X-API-Key` authentication
- [ ] Put backend behind Nginx reverse proxy
- [ ] Enable HTTPS with Let's Encrypt
- [ ] Set `RATE_LIMIT=10` (stricter in production)
- [ ] Disable the `/knowledge/add` endpoint or add admin auth
- [ ] Set up log rotation
- [ ] Monitor with Prometheus + Grafana (optional)
