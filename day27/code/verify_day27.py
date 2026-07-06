# -*- coding: utf-8 -*-
"""Day 27 验收脚本 —— Memory 与 RunnableWithMessageHistory。"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ["SPARKTECH_MOCK"] = "1"
os.environ.pop("OPENAI_API_KEY", None)

_TEST_DIR = Path(tempfile.mkdtemp(prefix="day27_verify_"))
os.environ["SPARKTECH_MEMORY_MODE"] = "memory"

from langchain_community.chat_message_histories import ChatMessageHistory  # noqa: E402
from langchain_community.chat_message_histories import SQLChatMessageHistory  # noqa: E402

from memory_demo import (  # noqa: E402
  WindowChatMessageHistory,
  demo_chat_message_history,
  demo_sqlite_history,
  demo_summary_memory,
  demo_window_memory,
)
from session_memory_chat import build_chain_with_history, get_session_history  # noqa: E402


def ok(msg: str) -> None:
  print(f"[OK] {msg}")


def fail(msg: str) -> None:
  print(f"[FAIL] {msg}")
  raise SystemExit(1)


def test_chat_message_history() -> None:
  h = demo_chat_message_history()
  assert len(h.messages) == 2
  assert h.messages[0].type == "human"
  ok("ChatMessageHistory in-memory")


def test_window_memory() -> None:
  h = demo_window_memory()
  assert len(h.messages) == 4, f"window k=2 应保留 4 条，实际 {len(h.messages)}"
  contents = [str(m.content) for m in h.messages]
  assert "第3轮" in contents[-2]
  assert "第1轮" not in " ".join(contents)
  ok("WindowChatMessageHistory k=2")


def test_summary_memory() -> None:
  h = demo_summary_memory()
  assert h.summary.startswith("历史摘要")
  assert len(h.messages) <= 4
  ok("SummaryChatMessageHistory")


def test_sqlite_persistence() -> None:
  db = _TEST_DIR / "test_memory.db"
  conn = f"sqlite:///{db}"
  sid = "verify-sqlite"

  h1 = SQLChatMessageHistory(session_id=sid, connection_string=conn)
  h1.clear()
  h1.add_user_message("持久化用户")
  h1.add_ai_message("持久化助手")

  h2 = SQLChatMessageHistory(session_id=sid, connection_string=conn)
  assert len(h2.messages) == 2
  ok("SQLChatMessageHistory SQLite persist")


def test_runnable_with_message_history() -> None:
  # 清空全局 store
  import session_memory_chat as smc  # noqa: E402

  smc._SESSION_STORE.clear()
  chain = build_chain_with_history()
  config = {"configurable": {"session_id": "verify-rwmh"}}

  r1 = chain.invoke({"user_input": "第一轮"}, config=config)
  assert r1

  r2 = chain.invoke({"user_input": "第二轮"}, config=config)
  assert r2

  hist = get_session_history("verify-rwmh")
  assert len(hist.messages) >= 4  # 2 轮 user+ai
  ok("RunnableWithMessageHistory multi-turn")


def test_session_isolation() -> None:
  import session_memory_chat as smc

  smc._SESSION_STORE.clear()
  chain = build_chain_with_history()

  chain.invoke(
    {"user_input": "会话A"},
    config={"configurable": {"session_id": "session-a"}},
  )
  chain.invoke(
    {"user_input": "会话B"},
    config={"configurable": {"session_id": "session-b"}},
  )

  ha = get_session_history("session-a")
  hb = get_session_history("session-b")
  assert len(ha.messages) >= 2
  assert len(hb.messages) >= 2
  ok("session_id isolation")


def main() -> None:
  print("=== Day 27 verify ===\n")
  test_chat_message_history()
  test_window_memory()
  test_summary_memory()
  test_sqlite_persistence()
  test_runnable_with_message_history()
  test_session_isolation()
  print("\n=== All checks passed ===")


if __name__ == "__main__":
  main()
