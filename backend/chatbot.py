"""
backend/chatbot.py — Core HackBot logic using LangChain (modernized)
"""
import os
import json
import asyncio
from pathlib import Path
from typing import AsyncGenerator, Optional
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate

load_dotenv()

# ── Resolve project root paths ────────────────────────────
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BACKEND_DIR.parent
PROMPTS_DIR = PROJECT_DIR / "prompts"

MAX_HISTORY_TURNS = 10  # Keep last 10 exchanges in context


# ── LLM Provider Selection ────────────────────────────────
def _build_llm():
    try:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            temperature=0.3,
        )
    except ImportError:
        # Fallback to community package
        from langchain_community.chat_models import ChatOllama as CommunityChatOllama
        return CommunityChatOllama(
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3"),
            temperature=0.3,
        )


# ── Safety Filter ─────────────────────────────────────────
BLOCK_KEYWORDS = [
    "hack my ex", "hack my wife", "hack my girlfriend", "hack my boyfriend",
    "hack my boss", "hack my teacher", "hack my neighbor",
    "deploy ransomware", "spread virus", "sell malware",
    "create botnet for hire",
]

def _is_blocked(message: str) -> bool:
    msg = message.lower()
    return any(kw in msg for kw in BLOCK_KEYWORDS)


# ── Prompt Templates ──────────────────────────────────────
MODE_ADDONS = {
    "beginner": "Explain all concepts from scratch. Assume zero prior knowledge.",
    "expert":   "Skip basics. Be technically precise and concise.",
    "ctf":      "Focus on CTF-specific techniques. Speed over stealth.",
    "oscp":     "Follow OSCP methodology. Avoid automated exploitation frameworks.",
    "redteam":  "Focus on stealth, persistence, and APT-style lateral movement.",
}

# Load system prompt safely
try:
    SYSTEM_PROMPT = (PROMPTS_DIR / "system_prompt.txt").read_text(encoding="utf-8")
except FileNotFoundError:
    SYSTEM_PROMPT = "You are HackBot — an elite AI assistant specialized in cybersecurity."
    print("[!] system_prompt.txt not found, using fallback prompt")

RAG_TEMPLATE = """{system_prompt}

{mode_addon}

Use the CONTEXT below to answer accurately. If context doesn't cover the answer, use your knowledge but say so.

CONTEXT:
{context}

Chat History:
{chat_history}

Operator: {question}
HackBot:"""

FALLBACK_TEMPLATE = """{system_prompt}

{mode_addon}

Chat History:
{chat_history}

Operator: {question}
HackBot:"""


# ── Simple Chat History Manager (replaces deprecated Memory) ─
def _format_history(messages: list, max_turns: int = MAX_HISTORY_TURNS) -> str:
    """Format the last N message pairs as a string for the prompt."""
    # Keep the last `max_turns * 2` messages (pairs of user + assistant)
    recent = messages[-(max_turns * 2):]
    lines = []
    for msg in recent:
        role = "Operator" if msg["role"] == "user" else "HackBot"
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)


# ── HackBot Class ─────────────────────────────────────────
class HackBot:
    def __init__(self, retriever=None):
        self.llm = None
        self.retriever = retriever
        self._sessions: dict[str, list] = {}   # session_id → message list
        self._llm_error = None

        # Try to initialize LLM — graceful failure
        try:
            self.llm = _build_llm()
            model = os.getenv("OLLAMA_MODEL", "llama3")
            print(f"[✓] Local LLM (Ollama) initialized: {model}")
        except Exception as e:
            self._llm_error = str(e)
            print(f"[!] LLM initialization failed: {e}")
            print("    The server will start, but chat will return errors until LLM is available.")

    def _build_prompt(self, mode: str, has_context: bool) -> PromptTemplate:
        addon = MODE_ADDONS.get(mode, MODE_ADDONS["expert"])
        template = RAG_TEMPLATE if has_context else FALLBACK_TEMPLATE
        input_vars = ["chat_history", "question"]
        if has_context:
            input_vars.append("context")
        return PromptTemplate(
            input_variables=input_vars,
            template=template
        ).partial(mode_addon=addon, system_prompt=SYSTEM_PROMPT)

    async def chat(self, message: str, session_id: str, mode: str = "expert"):
        # Safety check
        if _is_blocked(message):
            return (
                "⛔ HackBot cannot assist with that request. "
                "This tool is for authorized ethical hacking and education only.",
                []
            )

        # Check if LLM is available
        if self.llm is None:
            return (
                f"⚠️ LLM is not available. Error: {self._llm_error}\n\n"
                "**To fix this:**\n"
                "- Make sure Ollama is running (`ollama serve`) and the model is pulled (`ollama pull llama3`)",
                []
            )

        # Retrieve context from knowledge base
        docs = []
        context = ""
        sources = []
        if self.retriever:
            try:
                docs = self.retriever.invoke(message)
                context = "\n\n".join([d.page_content for d in docs]) if docs else ""
                sources = [{"title": d.metadata.get("source", "unknown"), "chunk": d.page_content[:200]} for d in docs]
            except Exception as e:
                print(f"[!] RAG retrieval failed: {e}")

        # Build prompt
        prompt = self._build_prompt(mode, has_context=bool(context))

        # Get chat history as formatted string
        session_messages = self._sessions.get(session_id, [])
        chat_history = _format_history(session_messages)

        # Build and run the chain using modern LCEL
        try:
            chain = prompt | self.llm
            inputs = {"question": message, "chat_history": chat_history}
            if context:
                inputs["context"] = context

            result = await asyncio.to_thread(chain.invoke, inputs)

            # Extract text from result (handles both string and AIMessage)
            if hasattr(result, 'content'):
                result_text = result.content
            else:
                result_text = str(result)

        except Exception as e:
            error_msg = str(e)
            if "connection" in error_msg.lower() or "refused" in error_msg.lower():
                result_text = (
                    "⚠️ Cannot connect to the LLM. Make sure Ollama is running "
                    "(`ollama serve`)."
                )
            else:
                result_text = f"⚠️ LLM Error: {error_msg}"
            return result_text, []

        # Store in session history
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        self._sessions[session_id].append({"role": "user",      "content": message})
        self._sessions[session_id].append({"role": "assistant", "content": result_text})

        return result_text.strip(), sources

    async def stream_response(self, message: str, session_id: str, mode: str = "expert") -> AsyncGenerator[str, None]:
        """Yield SSE tokens"""
        if _is_blocked(message):
            yield f"data: {json.dumps({'token': '⛔ Blocked by safety filter.'})}\n\n"
            yield f"data: {json.dumps({'done': True, 'sources': []})}\n\n"
            return

        response, sources = await self.chat(message, session_id, mode)

        # Stream word by word for typing effect
        for token in response.split(" "):
            yield f"data: {json.dumps({'token': token + ' '})}\n\n"
            await asyncio.sleep(0.02)

        yield f"data: {json.dumps({'done': True, 'sources': sources})}\n\n"

    def get_history(self, session_id: str) -> Optional[list]:
        return self._sessions.get(session_id)

    def clear_history(self, session_id: str):
        self._sessions.pop(session_id, None)

    def list_knowledge(self) -> dict:
        if self.retriever:
            try:
                vectorstore = self.retriever.vectorstore
                count = vectorstore._collection.count()
                return {"documents": [], "total_chunks": count}
            except Exception:
                pass
        return {"documents": [], "note": "Knowledge base not loaded or empty"}
