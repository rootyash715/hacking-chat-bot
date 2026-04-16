"""
backend/main.py — FastAPI entry point for HackBot AI
"""
import os
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

# ── Path Setup ───────────────────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent

# Add backend dir to sys.path so imports work when running from any CWD
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Load .env from project root
dotenv_path = PROJECT_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()  # fallback to default .env search

from chatbot import HackBot
from rag_pipeline import load_retriever, add_document_to_store

# ── App Setup ────────────────────────────────────────────
app = FastAPI(
    title="HackBot AI API",
    description="AI-powered cybersecurity assistant",
    version="1.0.0"
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

RATE_LIMIT = os.getenv("RATE_LIMIT", "30")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialize Components (graceful) ─────────────────────
print("=" * 55)
print("  ⚡ HackBot AI — Cybersecurity Assistant")
print("=" * 55)

retriever = None
try:
    retriever = load_retriever()
    if retriever:
        print("[✓] RAG retriever ready")
    else:
        print("[!] RAG disabled — chat will use LLM knowledge only")
except Exception as e:
    print(f"[!] RAG initialization failed: {e}")
    print("    Chat will use LLM knowledge only")

bot = HackBot(retriever=retriever)


# ── Request Schemas ──────────────────────────────────────
class ChatRequest(BaseModel):
    message:    str  = Field(..., min_length=1, max_length=4000)
    session_id: str  = Field(..., min_length=1, max_length=64)
    stream:     bool = False
    mode:       str  = "expert"   # expert | beginner | ctf | oscp | redteam


# ── Endpoints ────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "llm_provider": "ollama",
        "model":        os.getenv("OLLAMA_MODEL", "llama3"),
        "llm_ready":    bot.llm is not None,
        "rag_ready":    retriever is not None,
        "vector_store": "chromadb",
    }


@app.post("/chat")
@limiter.limit(f"{RATE_LIMIT}/minute")
async def chat(request: Request, body: ChatRequest):
    if body.stream:
        return StreamingResponse(
            bot.stream_response(body.message, body.session_id, body.mode),
            media_type="text/event-stream"
        )
    response, sources = await bot.chat(body.message, body.session_id, body.mode)
    return {
        "response":   response,
        "session_id": body.session_id,
        "sources":    sources,
    }


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    history = bot.get_history(session_id)
    if history is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": history}


@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    bot.clear_history(session_id)
    return {"message": f"History cleared for session {session_id}"}


@app.post("/knowledge/add")
async def add_knowledge(
    file:     UploadFile = File(...),
    title:    str        = Form(...),
    category: str        = Form("custom")
):
    if retriever is None:
        raise HTTPException(status_code=503, detail="RAG is not available. Check embedding model configuration.")
    content = await file.read()
    chunks = add_document_to_store(content, file.filename, title, category, retriever)
    return {"message": "Document indexed successfully.", "chunks_added": chunks, "title": title}


@app.get("/knowledge/list")
async def list_knowledge():
    return bot.list_knowledge()


# ── Run ──────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    print(f"[✓] HackBot starting on http://localhost:{port}")
    print("-" * 55)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)
