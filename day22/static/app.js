/**
 * Day 22 · 星火智服静态 Chat 交互
 *
 * 今日：本地 mock，无后端。
 * Day 24：设 USE_MOCK = false，配置 API_BASE，启用 fetchChat。
 */

'use strict';

// ---------------------------------------------------------------------------
// 配置
// ---------------------------------------------------------------------------

/** @type {boolean} Day 24 改为 false 以对接 FastAPI */
const USE_MOCK = true;

/** @type {string} Day 24 示例：'http://127.0.0.1:8000' */
const API_BASE = '';

const SESSION_ID = 'web-demo-001';
const WELCOME_MESSAGE =
  '您好，我是星火智服智能助手。\n您可以问我天气、订单（如 ST-10086），或打个招呼。';

/** mock 规则：与 Day 21 integrated_assistant 文案对齐 */
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
  '已收到您的消息。静态演示模式下，请尝试包含「天气」「订单」或「你好」等关键词。Day 24 将对接真实 API。';

// ---------------------------------------------------------------------------
// DOM
// ---------------------------------------------------------------------------

const messageList = document.getElementById('message-list');
const userInput = document.getElementById('user-input');
const btnSend = document.getElementById('btn-send');
const btnClear = document.getElementById('btn-clear');

let isReplying = false;

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

// ---------------------------------------------------------------------------
// 消息渲染
// ---------------------------------------------------------------------------

/**
 * @param {'user' | 'assistant'} role
 * @param {string} text
 * @returns {HTMLElement} bubble 元素
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
 * 打字机效果写入 bubble
 * @param {HTMLElement} element
 * @param {string} text
 * @param {number} delayMs
 */
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
// 发送逻辑
// ---------------------------------------------------------------------------

async function mockReply(userText) {
  await sleep(400);
  const reply = pickMockReply(userText);
  const bubble = appendMessage('assistant', '');
  await typewriterEffect(bubble, reply);
}

/**
 * Day 24 启用：对接 FastAPI POST /api/chat
 * @param {string} message
 * @returns {Promise<{reply: string, session_id?: string, tools_used?: string[]}>}
 */
async function fetchChat(message) {
  const url = `${API_BASE}/api/chat`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      session_id: SESSION_ID,
      stream: false,
    }),
  });
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

/*
// Day 24+ 流式 SSE 预留（今日不启用）：
//
// async function fetchChatStream(message, onDelta) {
//   const res = await fetch(`${API_BASE}/api/chat/stream`, {
//     method: 'POST',
//     headers: { 'Content-Type': 'application/json' },
//     body: JSON.stringify({ message, session_id: SESSION_ID, stream: true }),
//   });
//   const reader = res.body.getReader();
//   const decoder = new TextDecoder();
//   while (true) {
//     const { done, value } = await reader.read();
//     if (done) break;
//     const chunk = decoder.decode(value, { stream: true });
//     // 解析 SSE data: {...} 行，调用 onDelta(delta)
//   }
// }
*/

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
      const data = await fetchChat(text);
      const bubble = appendMessage('assistant', '');
      await typewriterEffect(bubble, data.reply || '');
    }
  } catch (err) {
    console.error('[chat]', err);
    appendMessage(
      'assistant',
      `请求失败：${err.message}。请确认 Day 24 后端已启动且 CORS 已配置。`
    );
  } finally {
    isReplying = false;
    setInputEnabled(true);
    userInput.focus();
  }
}

function clearChat() {
  if (isReplying) return;
  messageList.innerHTML = '';
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

function init() {
  initEventListeners();
  appendMessage('assistant', WELCOME_MESSAGE);
  userInput.focus();
}

init();
