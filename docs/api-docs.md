# 🔌 API Documentation — AI Hacking Chatbot Backend

## Base URL

```
http://localhost:8000
```

All responses are in JSON format unless streaming is requested.

---

## Authentication

> Currently, there is no authentication for local development. For production, add an API key header:

```
X-API-Key: your_secret_key
```

---

## Endpoints

---

### `POST /chat`

The primary endpoint for sending a message to the chatbot.

**Request Body:**
```json
{
  "message": "How do I enumerate SMB shares using Nmap?",
  "session_id": "user-abc123",
  "stream": true
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | string | ✅ | The user's query |
| `session_id` | string | ✅ | Unique ID per user/session |
| `stream` | boolean | ❌ | If true, stream tokens (default: false) |

**Response (non-streaming):**
```json
{
  "response": "To enumerate SMB shares, you can use:\n\n```bash\nnmap -p 445 --script smb-enum-shares -v <target>\n```\n\nThis runs the NSE script `smb-enum-shares` against port 445...",
  "session_id": "user-abc123",
  "sources": [
    {
      "title": "HackTricks - SMB Enumeration",
      "chunk": "SMB enumeration is critical during the recon phase..."
    }
  ],
  "tokens_used": 312
}
```

**Response (streaming):**
- Content-Type: `text/event-stream`
- Sends SSE (Server-Sent Events) chunks:
```
data: {"token": "To"}
data: {"token": " enumerate"}
data: {"token": " SMB"}
...
data: {"done": true, "sources": [...]}
```

**Error Response:**
```json
{
  "error": "Message flagged by safety filter.",
  "code": "SAFETY_BLOCK",
  "status": 400
}
```

---

### `GET /history/{session_id}`

Retrieve the full chat history for a session.

**URL Params:**
| Param | Type | Description |
|---|---|---|
| `session_id` | string | The session identifier |

**Response:**
```json
{
  "session_id": "user-abc123",
  "messages": [
    {
      "role": "user",
      "content": "How do I enumerate SMB shares?",
      "timestamp": "2026-02-23T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "To enumerate SMB shares, you can use...",
      "timestamp": "2026-02-23T10:00:02Z"
    }
  ]
}
```

---

### `DELETE /history/{session_id}`

Clear the chat history for a session.

**Response:**
```json
{
  "message": "History cleared for session user-abc123"
}
```

---

### `POST /knowledge/add`

Add a document to the knowledge base vector store.

**Request Body (multipart/form-data):**
| Field | Type | Description |
|---|---|---|
| `file` | File | PDF, TXT, or Markdown file |
| `title` | string | Label for the document |
| `category` | string | e.g., "web", "network", "malware" |

**Response:**
```json
{
  "message": "Document indexed successfully.",
  "chunks_added": 47,
  "title": "OWASP Top 10 2023"
}
```

---

### `GET /knowledge/list`

List all documents currently in the knowledge base.

**Response:**
```json
{
  "documents": [
    { "title": "MITRE ATT&CK v14", "chunks": 1240, "category": "framework" },
    { "title": "OWASP Top 10 2023", "chunks": 47, "category": "web" },
    { "title": "HackTricks - SQLi", "chunks": 89, "category": "web" }
  ]
}
```

---

### `GET /health`

Check if the backend server is running.

**Response:**
```json
{
  "status": "ok",
  "llm_provider": "ollama",
  "model": "llama3",
  "vector_store": "chromadb",
  "knowledge_chunks": 1376
}
```

---

## Error Codes

| Code | HTTP Status | Meaning |
|---|---|---|
| `SAFETY_BLOCK` | 400 | Query blocked by safety filter |
| `SESSION_NOT_FOUND` | 404 | No history for given session_id |
| `LLM_ERROR` | 503 | LLM provider unavailable |
| `INVALID_REQUEST` | 422 | Missing or invalid fields |
| `VECTOR_ERROR` | 500 | Vector store failure |

---

## Python SDK Example

```python
import requests

BASE = "http://localhost:8000"

def chat(message: str, session_id: str = "default") -> str:
    res = requests.post(f"{BASE}/chat", json={
        "message": message,
        "session_id": session_id,
        "stream": False
    })
    return res.json()["response"]

# Example
reply = chat("Explain SQL injection with an example payload.")
print(reply)
```

---

## cURL Examples

```bash
# Send a chat message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is SSRF?", "session_id": "sess-1"}'

# Get chat history
curl http://localhost:8000/history/sess-1

# Health check
curl http://localhost:8000/health

# Add a document
curl -X POST http://localhost:8000/knowledge/add \
  -F "file=@owasp_top10.pdf" \
  -F "title=OWASP Top 10 2023" \
  -F "category=web"
```
