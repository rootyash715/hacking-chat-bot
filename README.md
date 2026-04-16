# 🌐 Heisenbug Protocol — Cybersecurity AI Assistant

> **⚠️ ETHICAL USE ONLY** — This tool is designed exclusively for **authorized penetration testing**, **CTF competitions**, **bug bounty hunting**, and **cybersecurity education**. Using this against systems without explicit written permission is illegal.

---

## 📌 Protocol Overview

The **Heisenbug Protocol** is a premium, AI-powered hacking assistant specialized in **offensive and defensive cybersecurity**. It acts as your personal SOC companion — trained on security frameworks (MITRE ATT&CK, OWASP, CVE data), capable of explaining exploits, and guiding you through advanced penetration testing workflows.

The system is built on the philosophy that **detection alters the observed**, providing a sleek, stealthy, and high-performance terminal interface for ethical hackers.

---

## 🎯 Key Features

| Feature | Description |
|---|---|
| 🧠 Neural Core | Powered by OpenRouter (Gemini 2.0 / GPT-4) for state-of-the-art hacking logic |
| 📚 Abyssal Knowledge | RAG-powered retrieval from CVEs, MITRE ATT&CK, and HackTricks |
| 🕵️ Advanced Recon | Guidance for Nmap, Shodan, and automated subdomain enumeration |
| 💥 Vulnerability Lab | Deep explanations of SQLi, XSS, SSRF, and kernel exploits |
| 🐚 Shell Matrix | Optimized payloads for multi-platform reverse shells |
| 🌐 Cinematic UI | "Abyssal Green" design system with fluid terminal transitions |

---

## 🚀 Quick Start (Local Setup)

Follow these steps to initialize the protocol on your local machine:

### 1. Initialize Repository
```bash
git clone https://github.com/rootyash715/hacking-chat-bot
cd hacking-chat-bot
```

### 2. Configure Backend
Ensure you have Python 3.11+ installed.
```bash
cd backend
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory (copy from `.env.example`).
**IMPORTANT**: You will need an **OpenRouter API Key** to power the AI core.

1.  Get a key at [openrouter.ai](https://openrouter.ai/keys).
2.  Add it to `.env`: `OPENROUTER_API_KEY=your_key_here`.

### 4. Ignite System
```bash
python main.py
```

### 5. Access Terminal
Open `frontend/index.html` in your browser (or serve it locally). Click **INITIALIZE PROTOCOL** to begin the session.

---

## 🧑‍💻 Tech Stack

- **Neural Hub**: OpenRouter (Google Gemini 2.0 Flash / OpenAI GPT-4)
- **Framework**: Python 3.11+ · FastAPI · LangChain
- **Vector DB**: ChromaDB (stored in `backend/knowledge_base/chroma_db`)
- **Frontend**: Vanilla HTML5 · CSS3 (Abyssal Green Design) · JS ES6
- **Embeddings**: Local `all-MiniLM-L6-v2` for low-latency context matching

---

## ⚖️ Legal Disclaimer

This tool is for **educational and authorized security testing ONLY**. The developer assumes no liability for misuse. Always obtain **written authorization** before testing any system.
