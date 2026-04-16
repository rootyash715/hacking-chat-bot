"""
backend/chatbot.py — Minimalist HackBot AI core.
Optimized for OpenRouter & simplified RAG integration.
"""
import os
import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

# --- Path Configuration ---
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
PROMPTS_DIR = PROJECT_DIR / "prompts"

MAX_HISTORY_TURNS = 10

# --- LLM Provider Selection (OpenRouter) ---
def _build_llm():
    api_key   = os.getenv("OPENROUTER_API_KEY")
    model_name = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
    
    if not api_key:
        print("[!] Warning: OPENROUTER_API_KEY not found in environment.")
        return None

    return ChatOpenAI(
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=api_key,
        model_name=model_name,
        temperature=0.3,
        default_headers={
            "HTTP-Referer": "https://github.com/rootyash715/hacking-chat-bot",
            "X-Title": "HackBot AI",
        }
    )

# --- Safety Filter ---
BLOCK_KEYWORDS = ["hack my ex", "hack my wife", "hack my boss", "deploy ransomware"]

def _is_blocked(message: str) -> bool:
    msg = message.lower()
    return any(kw in msg for kw in BLOCK_KEYWORDS)

# --- Prompts ---
MODE_ADDONS = {
    "beginner": "Explain concepts from scratch.",
    "expert":   "Be technical and concise.",
    "ctf":      "Focus on CTF flags and speed.",
    "oscp":      "Follow OSCP methodology.",
}

# --- Persona ---
try:
    SYSTEM_PROMPT = (PROMPTS_DIR / "system_prompt.txt").read_text(encoding="utf-8")
except FileNotFoundError:
    SYSTEM_PROMPT = "You are HackBot, an elite cybersecurity AI."

RAG_TEMPLATE = """{system_prompt}
Mode: {mode_addon}

CONTEXT:
{context}

History:
{chat_history}

Operator: {question}
HackBot:"""

FALLBACK_TEMPLATE = """{system_prompt}
Mode: {mode_addon}

History:
{chat_history}

Operator: {question}
HackBot:"""

def _format_history(messages: list) -> str:
    recent = messages[-20:] # Last 10 exchanges
    return "\n".join([f"{'Operator' if m['role'] == 'user' else 'AI'}: {m['content']}" for m in recent])

# --- HackBot Core ---
class HackBot:
    def __init__(self, retriever=None):
        self.llm = _build_llm()
        self.retriever = retriever
        self._sessions = {} # session_id -> list of messages

        if self.llm:
            print(f"[INFO] ChatBot initialized with {os.getenv('OPENROUTER_MODEL')}")
        else:
            print("[ERROR] Failed to initialize LLM. Check API Key.")

    async def chat(self, message: str, session_id: str, mode: str = "expert"):
        if _is_blocked(message):
            return "Blocked: Ethical policy violation.", []

        if not self.llm:
            return "API Key missing or invalid.", []

        # RAG Retrieval
        context, sources = "", []
        if self.retriever:
            try:
                docs = self.retriever.invoke(message)
                context = "\n\n".join([d.page_content for d in docs])
                sources = [{"title": d.metadata.get("source", "kb"), "chunk": d.page_content[:150]} for d in docs]
            except Exception as e:
                print(f"[WARN] RAG failed: {e}")

        # Prompt & History
        history_str = _format_history(self._sessions.get(session_id, []))
        template = RAG_TEMPLATE if context else FALLBACK_TEMPLATE
        full_prompt = template.format(
            system_prompt=SYSTEM_PROMPT,
            mode_addon=MODE_ADDONS.get(mode, ""),
            context=context,
            chat_history=history_str,
            question=message
        )

        try:
            # Simple direct invoke
            result = await asyncio.to_thread(self.llm.invoke, full_prompt)
            result_text = result.content if hasattr(result, "content") else str(result)
        except Exception as e:
            return f"Error connecting to OpenRouter: {e}", []

        # Save History
        if session_id not in self._sessions: self._sessions[session_id] = []
        self._sessions[session_id].append({"role": "user", "content": message})
        self._sessions[session_id].append({"role": "assistant", "content": result_text})

        return result_text.strip(), sources

    async def stream_response(self, message: str, session_id: str, mode: str = "expert") -> AsyncGenerator[str, None]:
        res, sources = await self.chat(message, session_id, mode)
        for token in res.split(" "):
            yield f"data: {json.dumps({'token': token + ' '})}\n\n"
            await asyncio.sleep(0.01)
        yield f"data: {json.dumps({'done': True, 'sources': sources})}\n\n"
