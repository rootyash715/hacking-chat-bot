# 🎨 Frontend Guide — AI Hacking Chatbot

## Overview

The frontend is a **single-page application** built with vanilla HTML, CSS, and JavaScript. It features a full **matrix/hacker terminal aesthetic** with green-on-black color scheme, glitch animations, and a typewriter streaming effect for AI responses.

---

## File Structure

```
frontend/
├── index.html      # Main page structure
├── style.css       # All styles (matrix theme, animations)
└── app.js          # Logic (API calls, DOM, streaming, history)
```

---

## UI Layout

```
┌──────────────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════════════╗   │
│  ║  [⚡] HackBot AI         [Clear] [About]          ║   │  ← Top Bar
│  ╚═══════════════════════════════════════════════════╝   │
│  ┌────────────┐  ┌───────────────────────────────────┐   │
│  │            │  │                                   │   │
│  │  HISTORY   │  │          CHAT AREA                │   │
│  │  SIDEBAR   │  │   (messages appear here)          │   │
│  │            │  │                                   │   │
│  │  > Session │  │  [BOT]: Ready. Enter your target. │   │
│  │  > Session │  │  [YOU]: How do I scan ports?      │   │
│  │  > Session │  │  [BOT]: Use nmap -sV -p- ...      │   │
│  │            │  │                                   │   │
│  └────────────┘  └───────────────────────────────────┘   │
│                  ┌───────────────────────────────────┐   │
│                  │  > ░ Type your command...         │   │  ← Input
│                  │                      [EXECUTE ▶]  │   │
│                  └───────────────────────────────────┘   │
│  [Matrix rain background animation runs behind all]       │
└──────────────────────────────────────────────────────────┘
```

---

## Color Palette

| Variable | Value | Usage |
|---|---|---|
| `--bg-primary` | `#0a0a0a` | Main background |
| `--bg-secondary` | `#0d1117` | Chat area background |
| `--bg-panel` | `#111820` | Sidebar, input panel |
| `--accent-green` | `#00ff41` | Primary text, borders |
| `--accent-green-dim` | `#00aa2b` | Secondary text |
| `--accent-red` | `#ff0040` | Error messages, warnings |
| `--accent-cyan` | `#00ffff` | AI response text |
| `--text-muted` | `#4a5568` | Timestamps, labels |
| `--font-mono` | `'Fira Code', monospace` | All text |

---

## Component Details

### 1. Matrix Rain Background
- `<canvas>` element behind all content
- Renders animated falling green kanji/ASCII characters
- Fully configurable: speed, density, color fade
- Runs on `requestAnimationFrame` for smooth 60fps

### 2. Chat Bubble Types

**User Message:**
```html
<div class="message user">
  <span class="label">[YOU]</span>
  <p>How do I scan open ports?</p>
  <span class="timestamp">12:34:56</span>
</div>
```

**Bot Message (with code):**
```html
<div class="message bot">
  <span class="label">[HACKBOT]</span>
  <div class="content">
    <p>Use Nmap to scan all ports:</p>
    <pre><code class="language-bash">nmap -sV -p- -T4 &lt;target&gt;</code></pre>
  </div>
  <span class="timestamp">12:34:58</span>
</div>
```

### 3. Streaming Typewriter Effect
When `stream: true` is used, the bot response types out character by character using SSE:
```javascript
const evtSource = new EventSource('/chat/stream?session_id=...');
evtSource.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.token) appendToken(data.token);
    if (data.done)  finalizeMessage(data.sources);
};
```

### 4. Syntax Highlighting
Using **Highlight.js** CDN for automatic code highlighting:
- Bash/Shell commands
- Python scripts
- JavaScript payloads
- SQL injection payloads

### 5. Sidebar — Session History
- Lists previous sessions stored in `localStorage`
- Click to reload a past session
- Sessions auto-named from first message (truncated)

---

## Key JavaScript Functions

| Function | Description |
|---|---|
| `sendMessage()` | Reads input, sends POST to `/chat`, renders reply |
| `renderMessage(role, text)` | Creates a styled chat bubble in DOM |
| `streamResponse(sessionId)` | Opens SSE connection, streams tokens |
| `initMatrixRain()` | Starts canvas matrix animation |
| `loadHistory(sessionId)` | Fetches and restores a past session |
| `clearChat()` | Clears DOM and deletes session history |
| `highlightCode()` | Applies Highlight.js to new code blocks |
| `scrollToBottom()` | Auto-scrolls chat area after each message |

---

## Configuration (top of `app.js`)

```javascript
const CONFIG = {
    API_BASE: 'http://localhost:8000',  // Backend URL
    SESSION_ID: generateSessionId(),    // Unique per tab
    STREAM: true,                       // Enable streaming
    MAX_HISTORY: 10,                    // History entries in sidebar
    MATRIX_SPEED: 50,                   // Canvas animation speed (ms)
    MATRIX_DENSITY: 0.97,              // Character density
    TYPING_SPEED: 15,                  // ms per character (fallback)
};
```

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Enter` | Send message |
| `Shift + Enter` | New line in input |
| `Ctrl + L` | Clear chat |
| `↑ / ↓` | Navigate input history |
| `Ctrl + /` | Focus input box |

---

## Customization Guide

### Change the LLM persona display name
In `index.html`, update:
```html
<span class="bot-name">[HACKBOT]</span>
```

### Change accent color (e.g., red theme)
In `style.css`:
```css
:root {
    --accent-green: #ff0040;  /* Change to red */
    --accent-cyan:  #ff6600;  /* Change secondary */
}
```

### Disable matrix rain (better performance)
In `app.js`, set:
```javascript
const CONFIG = { ..., MATRIX_ENABLED: false };
```

---

## External Libraries (CDN, no install needed)

```html
<!-- Highlight.js for code syntax highlighting -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>

<!-- Marked.js for Markdown rendering -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@300;400;500&display=swap" rel="stylesheet">
```
