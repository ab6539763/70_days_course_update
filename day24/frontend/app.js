/**
 * Day 24 · 星火智服 Web Chat — 全栈 SSE 联调
 *
 * - 对接 FastAPI POST /api/chat/stream（SSE）
 * - session_id 持久化 localStorage
 * - 流式打字机：逐 delta 追加到 assistant 气泡
 */

'use strict';

// ---------------------------------------------------------------------------
// 配置
// ---------------------------------------------------------------------------

/** @type {boolean} 设为 true 可离线演示（不请求后端） */
const USE_MOCK = false;

/** @type {string} FastAPI 后端地址 */
const API_BASE = 'http://127.0.0.1:8000';

const SESSION_STORAGE_KEY = 'xinghuo_session_id';
const WELCOME_MESSAGE =
  '您好，我是星火智服智能助手。\n您可以问我天气、订单（如 ST-10086），或打个招呼。';

const MOCK_RESPONSES = [
  {
    keywords: ['天气', '气温', '温度', '下雨'],
    reply: (text) => {
      const city = extractCity(text);
      return `${city}当前天气：晴，26°C，湿度 58%。（数据来源：mock_weather_api）`;
    },
  },
  {
    keywords: ['订单', '物流', 'ST-', 'st-'],
    reply: () =>
      '订单 ST-10086：已发货，承运 顺丰，预计 2026-07-08 送达。',
  },
  {
    keywords: ['你好', '您好', 'hello', 'hi'],
    reply: () => '您好！很高兴为您服务，请问有什么可以帮您？',
  },
  {
    keywords: ['帮助', 'help'],
    reply: () =>
      '我可以帮您：\n1. 查询天气（例：上海天气）\n2. 查询订单（例：ST-10086）\n3. 日常问候',
  },
];

const DEFAULT_MOCK_REPLY =
  '已收到您的消息。本地 mock 模式，请尝试「天气」「订单」或「你好」。';

// ---------------------------------------------------------------------------
// DOM
// ---------------------------------------------------------------------------

const messageList = document.getElementById('message-list');
const userInput = document.getElementById('user-input');
const btnSend = document.getElementById('btn-send');
const btnClear = document.getElementById('btn-clear');
const statusBadge = document.getElementById('status-badge');

let isReplying = false;
let sessionId = loadOrCreateSessionId();

// ---------------------------------------------------------------------------
// Session
// ---------------------------------------------------------------------------

function loadOrCreateSessionId() {
  let id = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!id) {
    id = `web-${Date.now().toString(36)}`;
    localStorage.setItem(SESSION_STORAGE_KEY, id);
  }
  return id;
}

// ---------------------------------------------------------------------------
// 工具函数
// ---------------------------------------------------------------------------

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function extractCity(text) {
  const markers = ['天气', '气温', '温度'];
  for (const marker of markers) {
    const idx = text.indexOf(marker);
    if (idx > 0) {
      const prefix = text.slice(0, idx).replace(/[查的帮我一下怎样如何\s]/g, '');
      if (prefix.length >= 2) return prefix.slice(-6);
    }
  }
  return '上海';
}

function pickMockReply(userText) {
  const text = userText.trim();
  for (const rule of MOCK_RESPONSES) {
    if (rule.keywords.some((kw) => text.includes(kw))) {
      return typeof rule.reply === 'function' ? rule.reply(text) : rule.reply;
    }
  }
  return DEFAULT_MOCK_REPLY;
}

function scrollToBottom() {
  messageList.scrollTop = messageList.scrollHeight;
}

function setInputEnabled(enabled) {
  userInput.disabled = !enabled;
  btnSend.disabled = !enabled;
}

function setStatusBadge(text, className) {
  statusBadge.textContent = text;
  statusBadge.className = `status-badge ${className || ''}`.trim();
}

// ---------------------------------------------------------------------------
// 消息渲染
// ---------------------------------------------------------------------------

/**
 * @param {'user' | 'assistant'} role
 * @param {string} text
 * @returns {HTMLElement}
 */
function appendMessage(role, text) {
  const row = document.createElement('div');
  row.className = `message ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;

  row.appendChild(bubble);
  messageList.appendChild(row);
  scrollToBottom();
  return bubble;
}

/**
 * 创建空的 assistant 气泡，供流式写入
 * @returns {HTMLElement}
 */
function createStreamingBubble() {
  const bubble = appendMessage('assistant', '');
  bubble.classList.add('streaming');
  return bubble;
}

async function typewriterEffect(element, text, delayMs = 18) {
  element.classList.add('typing');
  element.textContent = '';
  for (const ch of text) {
    element.textContent += ch;
    scrollToBottom();
    await sleep(delayMs);
  }
  element.classList.remove('typing');
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------

async function checkHealth() {
  if (USE_MOCK) {
    setStatusBadge('本地 Mock', 'mock');
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const label = data.mode === 'mock' ? 'Mock 已连接' : 'Live 已连接';
    setStatusBadge(label, data.mode === 'mock' ? 'mock online' : 'online');
  } catch (err) {
    console.warn('[health]', err);
    setStatusBadge('后端离线', 'offline');
  }
}

async function loadHistory() {
  if (USE_MOCK) return;

  try {
    const res = await fetch(
      `${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}/history`
    );
    if (!res.ok) return;
    const data = await res.json();
    if (!data.messages || data.messages.length === 0) {
      appendMessage('assistant', WELCOME_MESSAGE);
      return;
    }
    for (const msg of data.messages) {
      if (msg.role === 'user' || msg.role === 'assistant') {
        appendMessage(msg.role, msg.content);
      }
    }
  } catch (err) {
    console.warn('[history]', err);
    appendMessage('assistant', WELCOME_MESSAGE);
  }
}

/**
 * 解析 SSE 文本块（fetch ReadableStream）
 * @param {string} buffer
 * @returns {{ events: object[], remainder: string }}
 */
function parseSSEBuffer(buffer) {
  const events = [];
  const parts = buffer.split('\n\n');
  const remainder = parts.pop() || '';

  for (const part of parts) {
    const lines = part.split('\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          events.push(JSON.parse(line.slice(6)));
        } catch (e) {
          console.warn('SSE JSON parse error', e);
        }
      }
    }
  }
  return { events, remainder };
}

/**
 * SSE 流式聊天
 * @param {string} message
 * @param {(delta: string) => void} onDelta
 * @returns {Promise<{ tools_used?: string[], message_id?: number }>}
 */
async function fetchChatStream(message, onDelta) {
  const res = await fetch(`${API_BASE}/api/chat/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: sessionId,
      stream: true,
    }),
  });

  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`HTTP ${res.status}: ${detail.slice(0, 120)}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  let meta = {};

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const { events, remainder } = parseSSEBuffer(buffer);
    buffer = remainder;

    for (const evt of events) {
      if (evt.event === 'delta' && evt.delta) {
        onDelta(evt.delta);
      } else if (evt.event === 'done') {
        meta = {
          tools_used: evt.tools_used || [],
          message_id: evt.message_id,
        };
      } else if (evt.event === 'error') {
        throw new Error(evt.error || '流式响应错误');
      }
    }
  }

  return meta;
}

async function clearSessionRemote() {
  if (USE_MOCK) return;
  await fetch(`${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  });
}

// ---------------------------------------------------------------------------
// 发送逻辑
// ---------------------------------------------------------------------------

async function mockReply(userText) {
  await sleep(400);
  const reply = pickMockReply(userText);
  const bubble = appendMessage('assistant', '');
  await typewriterEffect(bubble, reply);
}

async function apiStreamReply(userText) {
  const bubble = createStreamingBubble();
  let fullText = '';

  await fetchChatStream(userText, (delta) => {
    fullText += delta;
    bubble.textContent = fullText;
    scrollToBottom();
  });

  bubble.classList.remove('streaming');
}

async function sendMessage() {
  if (isReplying) return;

  const text = userInput.value.trim();
  if (!text) return;

  isReplying = true;
  setInputEnabled(false);

  appendMessage('user', text);
  userInput.value = '';
  userInput.style.height = 'auto';

  try {
    if (USE_MOCK) {
      await mockReply(text);
    } else {
      await apiStreamReply(text);
    }
  } catch (err) {
    console.error('[chat]', err);
    appendMessage(
      'assistant',
      `请求失败：${err.message}。请确认后端已启动（bash run.sh）且 CORS 已配置。`
    );
  } finally {
    isReplying = false;
    setInputEnabled(true);
    userInput.focus();
  }
}

async function clearChat() {
  if (isReplying) return;
  messageList.innerHTML = '';
  try {
    await clearSessionRemote();
  } catch (err) {
    console.warn('[clear]', err);
  }
  appendMessage('assistant', WELCOME_MESSAGE);
}

// ---------------------------------------------------------------------------
// 初始化
// ---------------------------------------------------------------------------

function autoResizeTextarea() {
  userInput.style.height = 'auto';
  userInput.style.height = `${Math.min(userInput.scrollHeight, 128)}px`;
}

function initEventListeners() {
  btnSend.addEventListener('click', () => {
    sendMessage();
  });

  btnClear.addEventListener('click', () => {
    if (window.confirm('确定清空对话记录？')) {
      clearChat();
    }
  });

  userInput.addEventListener('input', autoResizeTextarea);

  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

async function init() {
  initEventListeners();
  await checkHealth();
  await loadHistory();
  if (USE_MOCK && messageList.children.length === 0) {
    appendMessage('assistant', WELCOME_MESSAGE);
  }
  userInput.focus();
}

init();
