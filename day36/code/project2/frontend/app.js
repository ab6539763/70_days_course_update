/**
 * Project 2 · 企业知识库问答 — 前端
 *
 * - 多格式文档上传
 * - SSE 流式问答 + 引用徽章
 * - 会话持久化
 */

'use strict';

const API_BASE = 'http://127.0.0.1:8000';
const SESSION_STORAGE_KEY = 'sparktech_kb_session_id';
const WELCOME_MESSAGE =
  '您好，我是星火智服企业知识库助手。\n' +
  '左侧可上传 txt/md/pdf 文档；您可以问「退款政策」「API Key 申请」等问题，' +
  '回答将附带引用来源。';

const messageList = document.getElementById('message-list');
const userInput = document.getElementById('user-input');
const btnSend = document.getElementById('btn-send');
const btnClear = document.getElementById('btn-clear');
const btnRebuild = document.getElementById('btn-rebuild');
const btnUpload = document.getElementById('btn-upload');
const fileInput = document.getElementById('file-input');
const docList = document.getElementById('doc-list');
const statusBadge = document.getElementById('status-badge');

let isReplying = false;
let sessionId = loadOrCreateSessionId();
let pendingFiles = [];

function loadOrCreateSessionId() {
  let id = localStorage.getItem(SESSION_STORAGE_KEY);
  if (!id) {
    id = `kb-${Date.now().toString(36)}`;
    localStorage.setItem(SESSION_STORAGE_KEY, id);
  }
  return id;
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

function formatDocMeta(doc) {
  return `${doc.file_type.toUpperCase()} · ${doc.chunk_count} 块 · ${doc.status}`;
}

function renderDocList(documents) {
  docList.innerHTML = '';
  if (!documents.length) {
    const li = document.createElement('li');
    li.textContent = '暂无文档，请上传样本或查看 data/sample_docs';
    docList.appendChild(li);
    return;
  }
  for (const doc of documents) {
    const li = document.createElement('li');
    li.innerHTML = `<span class="name">${escapeHtml(doc.filename)}</span>${formatDocMeta(doc)}`;
    docList.appendChild(li);
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function buildCitationBadges(citations) {
  const wrap = document.createElement('div');
  wrap.className = 'citations';
  if (!citations || !citations.length) return wrap;

  citations.forEach((cite, idx) => {
    const badge = document.createElement('span');
    badge.className = 'citation-badge';
    badge.title = cite.snippet || '';
    badge.innerHTML =
      `<span class="idx">[${idx + 1}]</span>` +
      `<span class="source">${escapeHtml(cite.source)}</span>`;
    badge.addEventListener('click', () => {
      alert(`来源：${cite.source}\n\n${cite.snippet}\n\nscore: ${cite.score}`);
    });
    wrap.appendChild(badge);
  });
  return wrap;
}

function appendMessage(role, text, citations = []) {
  const row = document.createElement('div');
  row.className = `message ${role}`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  row.appendChild(bubble);

  if (role === 'assistant' && citations.length) {
    row.appendChild(buildCitationBadges(citations));
  }

  messageList.appendChild(row);
  scrollToBottom();
  return { row, bubble };
}

function createStreamingAssistant() {
  const row = document.createElement('div');
  row.className = 'message assistant';

  const bubble = document.createElement('div');
  bubble.className = 'bubble streaming';
  row.appendChild(bubble);

  const citeWrap = document.createElement('div');
  citeWrap.className = 'citations';
  row.appendChild(citeWrap);

  messageList.appendChild(row);
  scrollToBottom();
  return { row, bubble, citeWrap };
}

function renderCitations(container, citations) {
  container.innerHTML = '';
  const badges = buildCitationBadges(citations);
  container.replaceWith(badges);
  return badges;
}

function parseSSEBuffer(buffer) {
  const events = [];
  const parts = buffer.split('\n\n');
  const remainder = parts.pop() || '';

  for (const part of parts) {
    for (const line of part.split('\n')) {
      if (line.startsWith('data: ')) {
        try {
          events.push(JSON.parse(line.slice(6)));
        } catch (e) {
          console.warn('SSE parse error', e);
        }
      }
    }
  }
  return { events, remainder };
}

async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const label =
      data.mode === 'mock'
        ? `Mock · ${data.chunk_count} 块`
        : `Live · ${data.chunk_count} 块`;
    setStatusBadge(label, data.mode === 'mock' ? 'mock online' : 'online');
  } catch (err) {
    console.warn('[health]', err);
    setStatusBadge('后端离线', 'offline');
  }
}

async function loadDocuments() {
  try {
    const res = await fetch(`${API_BASE}/api/documents`);
    if (!res.ok) return;
    const data = await res.json();
    renderDocList(data.documents || []);
  } catch (err) {
    console.warn('[documents]', err);
  }
}

async function loadHistory() {
  try {
    const res = await fetch(
      `${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}/history`
    );
    if (!res.ok) {
      appendMessage('assistant', WELCOME_MESSAGE);
      return;
    }
    const data = await res.json();
    if (!data.messages || data.messages.length === 0) {
      appendMessage('assistant', WELCOME_MESSAGE);
      return;
    }
    for (const msg of data.messages) {
      if (msg.role === 'user' || msg.role === 'assistant') {
        appendMessage(msg.role, msg.content, msg.citations || []);
      }
    }
  } catch (err) {
    console.warn('[history]', err);
    appendMessage('assistant', WELCOME_MESSAGE);
  }
}

async function fetchChatStream(message, onCitations, onDelta) {
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
  let meta = { citations: [], message_id: null };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const { events, remainder } = parseSSEBuffer(buffer);
    buffer = remainder;

    for (const evt of events) {
      if (evt.event === 'citations' && evt.citations) {
        meta.citations = evt.citations;
        onCitations(evt.citations);
      } else if (evt.event === 'delta' && evt.delta) {
        onDelta(evt.delta);
      } else if (evt.event === 'done') {
        meta.citations = evt.citations || meta.citations;
        meta.message_id = evt.message_id;
      } else if (evt.event === 'error') {
        throw new Error(evt.error || '流式响应错误');
      }
    }
  }

  return meta;
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

  const { bubble, citeWrap } = createStreamingAssistant();
  let fullText = '';
  let citations = [];

  try {
    await fetchChatStream(
      text,
      (cites) => {
        citations = cites;
        const badges = buildCitationBadges(cites);
        citeWrap.replaceWith(badges);
        scrollToBottom();
      },
      (delta) => {
        fullText += delta;
        bubble.textContent = fullText;
        scrollToBottom();
      }
    );
    bubble.classList.remove('streaming');
    if (!citations.length && citeWrap.parentNode) {
      citeWrap.remove();
    }
  } catch (err) {
    console.error('[chat]', err);
    bubble.classList.remove('streaming');
    bubble.textContent = `请求失败：${err.message}。请确认 bash run.sh 已启动。`;
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
    await fetch(`${API_BASE}/api/sessions/${encodeURIComponent(sessionId)}`, {
      method: 'DELETE',
    });
  } catch (err) {
    console.warn('[clear]', err);
  }
  appendMessage('assistant', WELCOME_MESSAGE);
}

async function rebuildIndex() {
  if (!window.confirm('确定重建知识库索引？')) return;
  try {
    const res = await fetch(`${API_BASE}/api/kb/rebuild`, { method: 'POST' });
    const data = await res.json();
    alert(data.message || '重建完成');
    await loadDocuments();
    await checkHealth();
  } catch (err) {
    alert(`重建失败：${err.message}`);
  }
}

function onFileSelect() {
  pendingFiles = Array.from(fileInput.files || []);
  btnUpload.disabled = pendingFiles.length === 0;
  btnUpload.textContent =
    pendingFiles.length > 0
      ? `上传 ${pendingFiles.length} 个文件`
      : '上传并建库';
}

async function uploadFiles() {
  if (!pendingFiles.length) return;
  const form = new FormData();
  for (const f of pendingFiles) {
    form.append('files', f);
  }

  btnUpload.disabled = true;
  btnUpload.textContent = '上传中…';

  try {
    const res = await fetch(`${API_BASE}/api/documents/upload`, {
      method: 'POST',
      body: form,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    const data = await res.json();
    alert(data.message || '上传成功');
    pendingFiles = [];
    fileInput.value = '';
    btnUpload.textContent = '上传并建库';
    await loadDocuments();
    await checkHealth();
  } catch (err) {
    alert(`上传失败：${err.message}`);
    btnUpload.disabled = false;
  }
}

function autoResizeTextarea() {
  userInput.style.height = 'auto';
  userInput.style.height = `${Math.min(userInput.scrollHeight, 128)}px`;
}

function initEventListeners() {
  btnSend.addEventListener('click', sendMessage);
  btnClear.addEventListener('click', () => {
    if (window.confirm('确定清空对话？')) clearChat();
  });
  btnRebuild.addEventListener('click', rebuildIndex);
  btnUpload.addEventListener('click', uploadFiles);
  fileInput.addEventListener('change', onFileSelect);

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
  await loadDocuments();
  await loadHistory();
  userInput.focus();
}

init();
