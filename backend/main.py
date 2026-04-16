"""
backend/main.py — FastAPI Entry Point for HackBot AI
Optimized for minimalist and smooth experience.
"""
import os
import sys
from pathlib import Path
from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

# --- Path Setup ---
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(PROJECT_DIR / ".env")

from chatbot import HackBot
from rag_pipeline import load_retriever, add_document_to_store

# --- App Setup ---
app = FastAPI(title="HackBot AI API", version="1.0.0")

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

RATE_LIMIT = os.getenv("RATE_LIMIT", "60")
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Startup LOGS ---
print("=" * 55)
print("  [INFO] HackBot AI — Cybersecurity Assistant")
print("=" * 55)

retriever = load_retriever()
bot = HackBot(retriever=retriever)

# --- Request Schemas ---
class ChatRequest(BaseModel):
    message:    str  = Field(..., min_length=1, max_length=4000)
    session_id: str  = Field(..., min_length=1, max_length=64)
    stream:     bool = False
    mode:       str  = "expert"

# --- Endpoints ---
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "llm_ready": bot.llm is not None,
        "rag_ready": retriever is not None,
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
    return {"response": response, "session_id": body.session_id, "sources": sources}

@app.get("/history/{session_id}")
async def get_history(session_id: str):
    history = bot._sessions.get(session_id)
    return {"session_id": session_id, "messages": history or []}

@app.post("/knowledge/add")
async def add_knowledge(
    file: UploadFile = File(...),
    title: str = Form(...),
    category: str = Form("custom")
):
    content = await file.read()
    chunks = add_document_to_store(content, file.filename, title, category, retriever)
    return {"message": "Indexed successfully.", "chunks_added": chunks}

# --- Main Run ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    print(f"[OK] HackBot API starting on: http://localhost:{port}")
    print("-" * 55)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug)
