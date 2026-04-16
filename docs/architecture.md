# 🏗️ System Architecture — AI Hacking Chatbot

## Overview

The AI Hacking Chatbot follows a **RAG-enhanced LLM architecture** with a Python backend and a browser-based hacker-themed frontend. The system is designed to be modular, allowing you to swap the underlying LLM (OpenAI ↔ Ollama) without changing the rest of the stack.

---

## High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      FRONTEND (Browser)                  │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Hacker UI (HTML/CSS/JS) — Matrix Theme          │   │
│  │  - Chat window                                    │   │
│  │  - Input terminal                                 │   │
│  │  - History sidebar                                │   │
│  └────────────────────┬─────────────────────────────┘   │
└───────────────────────┼─────────────────────────────────┘
                        │ HTTP REST / WebSocket
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI/Python)                 │
│                                                          │
│  ┌─────────────┐    ┌────────────────┐                   │
│  │  API Layer  │───►│  Chatbot Core  │                   │
│  │  (FastAPI)  │    │  (chatbot.py)  │                   │
│  └─────────────┘    └───────┬────────┘                   │
│                             │                            │
│              ┌──────────────▼──────────────┐            │
│              │     LangChain Orchestrator   │            │
│              │  - Prompt Template           │            │
│              │  - Conversation Memory       │            │
│              │  - Chain Assembly            │            │
│              └──────┬───────────┬───────────┘            │
│                     │           │                        │
│          ┌──────────▼──┐   ┌───▼──────────────┐         │
│          │  RAG Engine  │   │   LLM Provider   │         │
│          │  (retriever) │   │  OpenAI / Ollama │         │
│          └──────┬───────┘   └──────────────────┘         │
│                 │                                        │
│         ┌───────▼────────┐                              │
│         │  Vector Store  │                              │
│         │  (ChromaDB /   │                              │
│         │   FAISS)       │                              │
│         └───────┬────────┘                              │
│                 │                                        │
│         ┌───────▼────────┐                              │
│         │  Knowledge Base│                              │
│         │  - CVE Data    │                              │
│         │  - MITRE ATT&CK│                              │
│         │  - OWASP Top 10│                              │
│         │  - HackTricks  │                              │
│         │  - Custom Docs │                              │
│         └────────────────┘                              │
└─────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Frontend Layer

| Component | Technology | Purpose |
|---|---|---|
| Chat UI | HTML5 + CSS3 | Render conversation, terminal styling |
| State Manager | Vanilla JS | Track messages, session history |
| API Client | `fetch()` / WebSocket | Send queries, receive streaming responses |
| Syntax Highlighter | Highlight.js | Render code blocks in responses |

**Key behaviour**: The frontend sends a POST request to `/chat` with `{ message, session_id }` and streams back the response token-by-token for a terminal-typing effect.

---

### 2. API Layer (FastAPI)

| Endpoint | Method | Description |
|---|---|---|
| `/chat` | POST | Main chat endpoint |
| `/history/{session_id}` | GET | Retrieve chat history |
| `/knowledge/add` | POST | Add documents to knowledge base |
| `/health` | GET | Health check |

The API layer validates input, manages sessions, and passes the query to the Chatbot Core.

---

### 3. Chatbot Core (LangChain)

The core orchestrates multiple LangChain components:

```
User Query
    │
    ▼
┌───────────────────┐
│  Input Guard      │  ← Detects clearly illegal intent
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Query Rewriter   │  ← Reformulates for better retrieval
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  RAG Retriever    │  ← Fetches top-K relevant documents
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Prompt Template  │  ← Combines context + chat history
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  LLM (GPT/Llama)  │  ← Generates the response
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Output Formatter │  ← Formats code, commands, tables
└────────┬──────────┘
         │
         ▼
     Response
```

---

### 4. RAG Pipeline

The **Retrieval-Augmented Generation** pipeline is the brain of the chatbot's specialized knowledge:

**Ingestion Phase (one-time / periodic):**
```
Raw Documents (PDFs, Markdown, TXT, URLs)
    │
    ▼
Document Loader (LangChain loaders)
    │
    ▼
Text Splitter (chunk_size=512, overlap=64)
    │
    ▼
Embedding Model (nomic-embed-text / OpenAI)
    │
    ▼
Vector Store (ChromaDB persisted to disk)
```

**Query Phase (every chat message):**
```
User Query
    │
    ▼
Embed Query → Vector
    │
    ▼
Similarity Search (top-5 chunks)
    │
    ▼
Retrieved Context → Injected into Prompt
```

---

### 5. LLM Providers

The system supports two backends, switchable via `.env`:

#### Option A — OpenAI (Cloud, Recommended for power)
- Model: `gpt-4o` or `gpt-4o-mini`
- Requires: `OPENAI_API_KEY`
- Pros: Most capable, no local hardware needed
- Cons: Costs money, sends data to OpenAI

#### Option B — Ollama (Local, Recommended for privacy)
- Models: `llama3`, `mistral`, `deepseek-coder`
- Requires: Ollama installed locally
- Pros: Free, fully private/offline
- Cons: Needs good GPU/CPU (8GB+ RAM)

---

### 6. Knowledge Base Sources

| Source | Type | Content |
|---|---|---|
| MITRE ATT&CK | JSON/CSV | TTP mappings, adversary techniques |
| OWASP Top 10 | PDF/HTML | Web vulnerability categories |
| CVE Database | JSON | Known vulnerability details |
| HackTricks | Scraped MD | Real-world hacking techniques |
| Custom Reports | PDF/TXT | Your own pentesting notes |
| PayloadsAllTheThings | MD | Payload cheatsheets |

---

## Data Flow Example

```
User: "How do I exploit a blind SQLi with time-based payloads?"

1. Query → FastAPI /chat endpoint
2. Query is embedded → vector search in ChromaDB
3. Top 5 chunks retrieved (from OWASP + HackTricks SQLi docs)
4. Prompt assembled: [system_prompt + retrieved_context + chat_history + user_query]
5. GPT-4o / Llama3 generates response with:
   - Explanation of time-based blind SQLi
   - Example payloads (for lab/CTF use)
   - sqlmap commands
   - Mitigation advice
6. Response streamed back to frontend
7. Frontend renders with syntax highlighting
```

---

## Scalability Considerations

| Concern | Solution |
|---|---|
| Many concurrent users | Use async FastAPI + connection pooling |
| Large knowledge base | Use FAISS (faster) or Qdrant (scalable) |
| Response speed | Stream tokens, use Llama3-8B locally for fast inference |
| Memory / context | Use LangChain ConversationSummaryMemory for long chats |
| Cost control | Use `gpt-4o-mini` instead of `gpt-4o` for cheaper inference |
