/**
 * app.js — Heisenbug Protocol Frontend Logic
 */
/* global marked, hljs */

// ── Configuration ─────────────────────────────────────────
const CONFIG = {
    API_BASE: 'http://localhost:8000',
    STREAM: true,
    MAX_HISTORY: 20,
    MATRIX_ENABLED: true,
    MATRIX_SPEED: 40,
    MATRIX_DENSITY: 0.975,
    HEALTH_CHECK_INTERVAL: 30000, // 30s
};

// ── State ─────────────────────────────────────────────────
let sessionId = generateSessionId();
let currentMode = 'expert';
let inputHistory = [];
let inputHistoryIdx = -1;
let isLoading = false;
let isBackendOnline = false;
let sessions = JSON.parse(localStorage.getItem('heisenbug_sessions') || '{}');

// ── DOM References ────────────────────────────────────────
const messagesEl = document.getElementById('messages');
const inputEl = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const clearBtn = document.getElementById('clear-btn');
const newChatBtn = document.getElementById('new-chat-btn');
const modeSelect = document.getElementById('mode-select');
const historyList = document.getElementById('history-list');
const sessionNameEl = document.getElementById('session-name');
const sidebarEl = document.getElementById('sidebar');
const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
const statusDot = document.getElementById('status-dot');
const statusText = document.getElementById('status-text');

// Start Screen elements
const startScreen = document.getElementById('start-screen');
const chatScreen = document.getElementById('chat-screen');
const startBtn = document.getElementById('start-btn');

// ── Init ──────────────────────────────────────────────────
document.getElementById('boot-time').textContent = timestamp();
renderHistoryList();
if (CONFIG.MATRIX_ENABLED) initMatrixRain();
checkBackendHealth();
setInterval(checkBackendHealth, CONFIG.HEALTH_CHECK_INTERVAL);

// ── Start Protocol Transition ─────────────────────────────
startBtn.addEventListener('click', () => {
    startScreen.style.opacity = '0';
    startScreen.style.transform = 'scale(1.1)';
    
    setTimeout(() => {
        startScreen.classList.add('hidden');
        chatScreen.classList.remove('hidden');
        chatScreen.classList.add('revealing');
        inputEl.focus();
    }, 800);
});

// ── Health Check ──────────────────────────────────────────
async function checkBackendHealth() {
    try {
        const res = await fetch(`${CONFIG.API_BASE}/health`, { signal: AbortSignal.timeout(5000) });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setOnlineStatus(true, data);
    } catch (err) {
        setOnlineStatus(false);
    }
}

function setOnlineStatus(online, data = null) {
    isBackendOnline = online;
    if (online) {
        statusDot.className = 'dot-green';
        if (data && data.llm_ready) {
            statusText.textContent = 'ONLINE';
            statusDot.title = `Connected — ${data.llm_provider}/${data.model}`;
        } else if (data) {
            statusText.textContent = 'LIMITED';
            statusDot.className = 'dot-yellow';
            statusDot.title = 'Backend online but LLM not ready';
        } else {
            statusText.textContent = 'ONLINE';
        }
    } else {
        statusDot.className = 'dot-red';
        statusText.textContent = 'OFFLINE';
        statusDot.title = `Cannot reach backend at ${CONFIG.API_BASE}`;
    }
}

// ── Matrix Rain ───────────────────────────────────────────
function initMatrixRain() {
    const canvas = document.getElementById('matrix-canvas');
    const ctx = canvas.getContext('2d');
    let cols, drops;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        cols = Math.floor(canvas.width / 14);
        drops = Array(cols).fill(1);
    }

    resize();
    window.addEventListener('resize', resize);

    const chars = '01アイウエオカキクケコサシスセソタチABCDEFGHIJKLMNOP<>/\\{}[]';

    function draw() {
        ctx.fillStyle = 'rgba(8, 13, 10, 0.05)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#00f5d4';
        ctx.font = '13px "Space Grotesk", monospace';
        drops.forEach((y, i) => {
            const ch = chars[Math.floor(Math.random() * chars.length)];
            ctx.fillText(ch, i * 14, y * 14);
            if (y * 14 > canvas.height && Math.random() > CONFIG.MATRIX_DENSITY) drops[i] = 0;
            drops[i]++;
        });
    }

    setInterval(draw, CONFIG.MATRIX_SPEED);
}

// ── Utilities ─────────────────────────────────────────────
function generateSessionId() {
    return 'sess-' + Math.random().toString(36).slice(2, 10);
}

function timestamp() {
    return new Date().toLocaleTimeString('en-GB', { hour12: false });
}

function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function scrollToBottom() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

// ── Render Message ────────────────────────────────────────
function renderMessage(role, text, sources = []) {
    const div = document.createElement('div');
    div.className = `message ${role}`;

    const header = document.createElement('div');
    header.className = 'msg-header';
    const label = document.createElement('span');
    label.className = `label ${role === 'bot' ? 'bot-label' : role === 'error' ? '' : 'user-label'}`;
    label.textContent = role === 'bot' ? '[HEISENBUG]' : role === 'error' ? '[ERROR]' : '[YOU]';
    const ts = document.createElement('span');
    ts.className = 'timestamp';
    ts.textContent = timestamp();
    header.append(label, ts);

    const body = document.createElement('div');
    body.className = 'msg-body';

    if (role === 'bot' || role === 'error') {
        body.innerHTML = marked.parse(text || '');
        body.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));

        // Add copy buttons to code blocks
        body.querySelectorAll('pre').forEach(pre => {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.textContent = 'COPY';
            copyBtn.addEventListener('click', () => {
                const code = pre.querySelector('code');
                navigator.clipboard.writeText(code?.textContent || pre.textContent);
                copyBtn.textContent = '✓ COPIED';
                setTimeout(() => { copyBtn.textContent = 'COPY'; }, 2000);
            });
            pre.style.position = 'relative';
            pre.appendChild(copyBtn);
        });
    } else {
        body.textContent = text;
    }

    // Sources
    if (sources.length > 0) {
        const details = document.createElement('details');
        details.className = 'sources-block';
        details.innerHTML = `<summary>📎 ${sources.length} source(s)</summary>`;
        sources.forEach(s => {
            const p = document.createElement('p');
            p.textContent = `· ${s.title}: ${s.chunk}...`;
            details.appendChild(p);
        });
        body.appendChild(details);
    }

    div.append(header, body);
    messagesEl.appendChild(div);
    scrollToBottom();
    return { div, body };
}

// ── Loading Indicator ─────────────────────────────────────
function showLoading() {
    const div = document.createElement('div');
    div.className = 'message bot';
    div.id = 'loading-msg';

    const header = document.createElement('div');
    header.className = 'msg-header';
    const label = document.createElement('span');
    label.className = 'label bot-label';
    label.textContent = '[HEISENBUG]';
    const ts = document.createElement('span');
    ts.className = 'timestamp';
    ts.textContent = timestamp();
    header.append(label, ts);

    const body = document.createElement('div');
    body.className = 'msg-body';
    body.innerHTML = '<div class="loading-dots"><span>.</span><span>.</span><span>.</span></div> <span class="dim">Processing query...</span>';

    div.append(header, body);
    messagesEl.appendChild(div);
    scrollToBottom();
    return div;
}

function hideLoading() {
    const el = document.getElementById('loading-msg');
    if (el) el.remove();
}

// ── Streaming Bot Message ─────────────────────────────────
async function appendStreamingResponse(userMessage) {
    const loadingEl = showLoading();

    try {
        const response = await fetch(`${CONFIG.API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userMessage,
                session_id: sessionId,
                stream: true,
                mode: currentMode,
            }),
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        hideLoading();
        const { div, body } = renderMessage('bot', '');
        body.classList.add('typing-cursor');
        let fullText = '';

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const text = decoder.decode(value);
            const lines = text.split('\n').filter(l => l.startsWith('data: '));

            for (const line of lines) {
                try {
                    const data = JSON.parse(line.slice(6));
                    if (data.token) {
                        fullText += data.token;
                        body.innerHTML = marked.parse(fullText);
                        body.querySelectorAll('pre code').forEach(el => hljs.highlightElement(el));

                        // Add copy buttons
                        body.querySelectorAll('pre:not(.has-copy)').forEach(pre => {
                            pre.classList.add('has-copy');
                            const copyBtn = document.createElement('button');
                            copyBtn.className = 'copy-btn';
                            copyBtn.textContent = 'COPY';
                            copyBtn.addEventListener('click', () => {
                                const code = pre.querySelector('code');
                                navigator.clipboard.writeText(code?.textContent || pre.textContent);
                                copyBtn.textContent = '✓ COPIED';
                                setTimeout(() => { copyBtn.textContent = 'COPY'; }, 2000);
                            });
                            pre.style.position = 'relative';
                            pre.appendChild(copyBtn);
                        });

                        scrollToBottom();
                    }
                    if (data.done) {
                        body.classList.remove('typing-cursor');
                        if (data.sources?.length) {
                            const details = document.createElement('details');
                            details.className = 'sources-block';
                            details.innerHTML = `<summary>📎 ${data.sources.length} source(s)</summary>`;
                            data.sources.forEach(s => {
                                const p = document.createElement('p');
                                p.textContent = `· ${s.title}: ${s.chunk}...`;
                                details.appendChild(p);
                            });
                            body.appendChild(details);
                        }
                    }
                } catch (parseErr) {
                    // Skip malformed SSE lines
                }
            }
        }

        saveToSession(userMessage, fullText);

    } catch (err) {
        hideLoading();
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
            renderMessage('error',
                `⛔ **Backend Offline**\n\nCannot connect to \`${CONFIG.API_BASE}\`.\n\n` +
                `**To start the backend:**\n` +
                '```bash\ncd backend\npython main.py\n```\n' +
                `Make sure Ollama is running: \`ollama serve\``
            );
            setOnlineStatus(false);
        } else {
            renderMessage('error', `⛔ Connection error: ${err.message}`);
        }
    }
}

// ── Non-streaming fallback ────────────────────────────────
async function sendMessageNoStream(userMessage) {
    const loadingEl = showLoading();
    try {
        const res = await fetch(`${CONFIG.API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: userMessage,
                session_id: sessionId,
                stream: false,
                mode: currentMode,
            }),
        });
        hideLoading();
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        renderMessage('bot', data.response, data.sources || []);
        saveToSession(userMessage, data.response);
    } catch (err) {
        hideLoading();
        if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
            renderMessage('error',
                `⛔ **Backend Offline**\n\nCannot connect to \`${CONFIG.API_BASE}\`.\n\n` +
                `**To start the backend:**\n` +
                '```bash\ncd backend\npython main.py\n```'
            );
            setOnlineStatus(false);
        } else {
            renderMessage('error', `⛔ Error: ${err.message}`);
        }
    }
}

// ── Send Flow ─────────────────────────────────────────────
async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text || isLoading) return;

    isLoading = true;
    sendBtn.disabled = true;
    sendBtn.querySelector('span:first-child').textContent = 'SENDING...';
    inputEl.value = '';
    // charCountEl.textContent = '0 / 4000'; // Removed in HTML
    autoResize();

    // Track input history
    inputHistory.unshift(text);
    if (inputHistory.length > 50) inputHistory.pop();
    inputHistoryIdx = -1;

    renderMessage('user', text);

    // Update session name (first message)
    if (!sessions[sessionId]) {
        sessions[sessionId] = { name: text.slice(0, 35), messages: [] };
        sessionNameEl.textContent = `[ ${sessions[sessionId].name.toUpperCase()} ]`;
        renderHistoryList();
    }

    if (CONFIG.STREAM) {
        await appendStreamingResponse(text);
    } else {
        await sendMessageNoStream(text);
    }

    isLoading = false;
    sendBtn.disabled = false;
    sendBtn.querySelector('span:first-child').textContent = 'EXECUTE';
    inputEl.focus();
}

// ── Session Persistence ───────────────────────────────────
function saveToSession(userMsg, botMsg) {
    if (!sessions[sessionId]) sessions[sessionId] = { name: userMsg.slice(0, 35), messages: [] };
    sessions[sessionId].messages.push({ role: 'user', content: userMsg });
    sessions[sessionId].messages.push({ role: 'bot', content: botMsg });
    localStorage.setItem('heisenbug_sessions', JSON.stringify(sessions));
}

function renderHistoryList() {
    historyList.innerHTML = '';
    Object.entries(sessions).reverse().slice(0, CONFIG.MAX_HISTORY).forEach(([id, sess]) => {
        const item = document.createElement('div');
        item.className = `history-item${id === sessionId ? ' active' : ''}`;
        item.textContent = '> ' + (sess.name || 'Untitled');
        item.title = sess.name;
        item.addEventListener('click', () => loadSession(id));
        historyList.appendChild(item);
    });
}

function loadSession(id) {
    sessionId = id;
    messagesEl.innerHTML = '';
    sessionNameEl.textContent = `[ ${(sessions[id].name || 'SESSION').toUpperCase()} ]`;
    (sessions[id].messages || []).forEach(m => renderMessage(m.role, m.content));
    renderHistoryList();
}

// ── New Chat ──────────────────────────────────────────────
function newChat() {
    sessionId = generateSessionId();
    messagesEl.innerHTML = '';
    sessionNameEl.textContent = '[ NEW SESSION ]';
    renderHistoryList();
}

// ── Auto-resize textarea ──────────────────────────────────
function autoResize() {
    inputEl.style.height = 'auto';
    inputEl.style.height = Math.min(inputEl.scrollHeight, 140) + 'px';
}

// ── Events ────────────────────────────────────────────────
sendBtn.addEventListener('click', sendMessage);
newChatBtn.addEventListener('click', newChat);
clearBtn.addEventListener('click', () => { messagesEl.innerHTML = ''; });
modeSelect.addEventListener('change', e => {
    currentMode = e.target.value;
    document.getElementById('mode-label').textContent = 'MODE: ' + currentMode.toUpperCase();
});
toggleSidebarBtn.addEventListener('click', () => sidebarEl.classList.toggle('collapsed'));

inputEl.addEventListener('input', () => {
    autoResize();
    charCountEl.textContent = `${inputEl.value.length} / 4000`;
});

inputEl.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
    // Input history navigation
    if (e.key === 'ArrowUp') {
        e.preventDefault();
        inputHistoryIdx = Math.min(inputHistoryIdx + 1, inputHistory.length - 1);
        inputEl.value = inputHistory[inputHistoryIdx] || '';
        autoResize();
    }
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        inputHistoryIdx = Math.max(inputHistoryIdx - 1, -1);
        inputEl.value = inputHistoryIdx === -1 ? '' : inputHistory[inputHistoryIdx];
        autoResize();
    }
});

// Global shortcuts
document.addEventListener('keydown', e => {
    if (e.ctrlKey && e.key === 'l') { e.preventDefault(); messagesEl.innerHTML = ''; }
    if (e.ctrlKey && e.key === '/') { e.preventDefault(); inputEl.focus(); }
});

// Focus input on load
inputEl.focus();
