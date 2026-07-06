const API_BASE = (() => {
  const host = window.location.hostname || "127.0.0.1";
  const port = new URLSearchParams(window.location.search).get("api_port") || "8010";
  return `http://${host}:${port}`;
})();

let currentThreadId = null;

const els = {
  modeBadge: document.getElementById("modeBadge"),
  requestInput: document.getElementById("requestInput"),
  submitBtn: document.getElementById("submitBtn"),
  statusLine: document.getElementById("statusLine"),
  planBox: document.getElementById("planBox"),
  stepsBox: document.getElementById("stepsBox"),
  approvalPanel: document.getElementById("approvalPanel"),
  approvalReason: document.getElementById("approvalReason"),
  approvalPreview: document.getElementById("approvalPreview"),
  approveBtn: document.getElementById("approveBtn"),
  rejectBtn: document.getElementById("rejectBtn"),
  approvalComment: document.getElementById("approvalComment"),
  resultBox: document.getElementById("resultBox"),
};

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${text}`);
  }
  return res.json();
}

function renderState(state) {
  els.planBox.textContent = (state.plan || []).map((s, i) => `${i + 1}. ${s}`).join("\n") || "—";
  els.stepsBox.innerHTML = (state.steps || [])
    .map(
      (s) =>
        `<div class="step"><div class="agent">${s.agent}</div><div>${s.summary}</div></div>`
    )
    .join("") || "—";
  els.resultBox.textContent = JSON.stringify(state.result || {}, null, 2);
  els.statusLine.textContent = `thread=${state.thread_id} · status=${state.status}`;

  if (state.pending_approval && state.status === "awaiting_approval") {
    els.approvalPanel.hidden = false;
    els.approvalReason.textContent = state.pending_approval.reason || "";
    els.approvalPreview.textContent = JSON.stringify(state.pending_approval.preview, null, 2);
  } else {
    els.approvalPanel.hidden = true;
  }
}

async function bootstrap() {
  try {
    const health = await api("/api/health");
    els.modeBadge.textContent = health.mode;
  } catch (e) {
    els.statusLine.textContent = `后端未启动：${e.message}`;
  }
}

async function submitTask() {
  const request = els.requestInput.value.trim();
  if (!request) return;
  els.submitBtn.disabled = true;
  try {
    const created = await api("/api/tasks", {
      method: "POST",
      body: JSON.stringify({ request }),
    });
    currentThreadId = created.thread_id;
    const full = await api(`/api/tasks/${currentThreadId}`);
    renderState(full);
  } catch (e) {
    els.statusLine.textContent = `提交失败：${e.message}`;
  } finally {
    els.submitBtn.disabled = false;
  }
}

async function resume(decision) {
  if (!currentThreadId) return;
  const comment = els.approvalComment.value.trim() || undefined;
  try {
    const state = await api(`/api/tasks/${currentThreadId}/resume`, {
      method: "POST",
      body: JSON.stringify({ approval: { decision, comment } }),
    });
    renderState(state);
  } catch (e) {
    els.statusLine.textContent = `审批失败：${e.message}`;
  }
}

els.submitBtn.addEventListener("click", submitTask);
els.approveBtn.addEventListener("click", () => resume("approve"));
els.rejectBtn.addEventListener("click", () => resume("reject"));

bootstrap();
