# 🤖 AI Hacking Chatbot

> **⚠️ ETHICAL USE ONLY** — This tool is designed exclusively for **authorized penetration testing**, **CTF competitions**, **bug bounty hunting**, and **cybersecurity education**. Using this against systems without explicit written permission is illegal.

---

## 📌 What Is This?

An AI-powered chatbot specialized in **offensive and defensive cybersecurity**. It acts as your personal hacking assistant — trained on security frameworks (MITRE ATT&CK, OWASP, CVE data), capable of explaining exploits, generating payloads for practice environments, and guiding you through penetration testing workflows.

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| 🧠 LLM-Powered | Uses GPT-4 / Llama3 / Mistral for deep contextual understanding |
| 📚 RAG Knowledge Base | Retrieves from CVEs, MITRE ATT&CK, OWASP, HackTricks |
| 🕵️ Recon Assistant | Guides Nmap, Shodan, Sublist3r, Amass workflows |
| 💥 Exploit Explainer | Explains BoF, SQLi, XSS, LFI, RFI, XXE, SSRF in depth |
| 🔐 Payload Generator | Creates payloads for CTF/lab environments |
| 🐚 Shell Helper | Guides reverse/bind shell creation across platforms |
| 📝 Report Writer | Auto-generates pentest report sections |
| 🌐 Hacker-Themed UI | Dark matrix-green terminal aesthetic |

---

## 🗂️ Project Structure

```
hacking chat bot/
├── docs/                        # All documentation
│   ├── architecture.md          # System architecture
│   ├── api-docs.md              # Backend API reference
│   ├── frontend-guide.md        # Frontend UI documentation
│   ├── prompt-engineering.md    # Prompt engineering guide
│   ├── rag-knowledge-base.md    # RAG & knowledge base setup
│   ├── security-ethics.md       # Security & ethics guidelines
│   └── setup-deployment.md      # Installation & deployment guide
├── backend/                     # Python FastAPI backend
│   ├── main.py                  # Entry point
│   ├── chatbot.py               # Core chatbot logic
│   ├── rag_pipeline.py          # RAG retrieval pipeline
│   ├── knowledge_base/          # Vector store & documents
│   └── requirements.txt         # Python dependencies
├── frontend/                    # Web frontend
│   ├── index.html               # Main HTML
│   ├── style.css                # Hacker-themed styles
│   └── app.js                   # Frontend JavaScript
├── prompts/                     # System prompts
│   └── system_prompt.txt        # Core AI persona prompt
├── .env.example                 # Environment variable template
└── README.md                    # This file
```

---

## 🚀 Quick Start

```bash
# 1. Clone / navigate to project
cd "hacking chat bot"

# 2. Set up Python backend
cd backend
pip install -r requirements.txt

# 3. Configure environment
cp ../.env.example ../.env
# Customise .env as needed

# 4. Start the backend
python main.py

# 5. Open frontend
# Open frontend/index.html in a browser (or serve it)
```

---

## 📖 Documentation Index

| Document | Purpose |
|---|---|
| [Architecture](docs/architecture.md) | Full system design & data flow |
| [API Docs](docs/api-docs.md) | Backend endpoints & request/response formats |
| [Frontend Guide](docs/frontend-guide.md) | UI components & customization |
| [Prompt Engineering](docs/prompt-engineering.md) | How to craft system prompts |
| [RAG Knowledge Base](docs/rag-knowledge-base.md) | Setting up the vector DB & knowledge |
| [Security & Ethics](docs/security-ethics.md) | Guardrails, safety, and legal use |
| [Setup & Deployment](docs/setup-deployment.md) | Full installation guide |

---

## 🧑‍💻 Tech Stack

- **Backend**: Python 3.11+ · FastAPI · LangChain
- **AI Models**: Ollama (Llama3, Mistral) locally
- **Vector DB**: ChromaDB / FAISS
- **Frontend**: HTML · CSS · Vanilla JS (Matrix hacker theme)
- **Embeddings**: `all-MiniLM-L6-v2` locally via SentenceTransformers

---

## ⚖️ Legal Disclaimer

This tool is for **educational and authorized security testing ONLY**. The developer assumes no liability for misuse. Always obtain **written authorization** before testing any system.
