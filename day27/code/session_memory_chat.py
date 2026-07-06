# -*- coding: utf-8 -*-
"""Day 27 · RunnableWithMessageHistory 多轮会话 CLI。

运行：
  cd day27/code && python session_memory_chat.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables.history import RunnableWithMessageHistory

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from memory_demo import WindowChatMessageHistory  # noqa: E402
from mock_llm import build_chat_model, is_mock_mode, mock_reply_for_user  # noqa: E402

DATA_DIR = CODE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
SQLITE_PATH = DATA_DIR / "sessions.db"

# 全局 session 存储：memory / window / sqlite 三种后端
_SESSION_STORE: dict[str, BaseChatMessageHistory] = {}
_MEMORY_MODE = os.getenv("SPARKTECH_MEMORY_MODE", "memory")  # memory | window | sqlite

HELP_TEXT = """
星火智服 · Day 27 Memory CLI

斜杠命令：
  /help              显示帮助
  /session <id>      切换会话 ID（默认 default）
  /history           打印当前会话历史条数
  /clear             清空当前会话历史
  /mode <类型>       切换 memory / window / sqlite
  /exit              退出

环境变量 SPARKTECH_MEMORY_MODE 可设默认后端。
""".strip()

BANNER = """
╔══════════════════════════════════════════════════════════╗
║  星火智服 · Day 27 Memory + RunnableWithMessageHistory   ║
║  Phase2：多轮记忆接 LangChain 栈                          ║
╚══════════════════════════════════════════════════════════╝
""".strip()


def _sqlite_connection() -> str:
  return f"sqlite:///{SQLITE_PATH}"


def create_history(session_id: str) -> BaseChatMessageHistory:
  """按模式创建 ChatMessageHistory 后端。"""
  if _MEMORY_MODE == "window":
    return WindowChatMessageHistory(k=2)
  if _MEMORY_MODE == "sqlite":
    return SQLChatMessageHistory(
      session_id=session_id,
      connection_string=_sqlite_connection(),
    )
  return ChatMessageHistory()


def get_session_history(session_id: str) -> BaseChatMessageHistory:
  """RunnableWithMessageHistory 所需的 history 工厂。"""
  if session_id not in _SESSION_STORE:
    _SESSION_STORE[session_id] = create_history(session_id)
  return _SESSION_STORE[session_id]


def build_chain_with_history():
  """构建带记忆的 LCEL 链。"""
  prompt = ChatPromptTemplate.from_messages(
    [
      ("system", "你是星火智服助手，结合历史简洁回答。"),
      MessagesPlaceholder(variable_name="history"),
      ("human", "{user_input}"),
    ]
  )
  llm = build_chat_model()

  if is_mock_mode():
    # mock：直接消费 RunnableWithMessageHistory 注入的 dict（勿先过 Prompt）
    def _mock_invoke(inputs: dict) -> str:
      history = inputs.get("history", [])
      user = inputs.get("user_input", "")
      return mock_reply_for_user(user, call_index=len(history) // 2 + 1)

    core = RunnableLambda(_mock_invoke)
  else:
    core = prompt | llm | StrOutputParser()

  return RunnableWithMessageHistory(
    core,
    get_session_history,
    input_messages_key="user_input",
    history_messages_key="history",
  )


def handle_command(
  text: str,
  *,
  current_session: str,
) -> tuple[bool, bool, str, str]:
  """返回 handled, should_exit, message, new_session_id。"""
  global _MEMORY_MODE

  raw = text.strip()
  if not raw.startswith("/"):
    return False, False, "", current_session

  parts = raw[1:].split()
  if not parts:
    return True, False, "未知命令", current_session

  cmd = parts[0].lower()
  args = parts[1:]

  if cmd == "help":
    return True, False, HELP_TEXT, current_session
  if cmd in ("exit", "quit"):
    return True, True, "再见。", current_session
  if cmd == "history":
    hist = get_session_history(current_session)
    return True, False, f"会话 {current_session} 共 {len(hist.messages)} 条消息。", current_session
  if cmd == "clear":
    hist = get_session_history(current_session)
    hist.clear()
    return True, False, "已清空当前会话历史。", current_session
  if cmd == "session" and args:
    sid = args[0]
    get_session_history(sid)  # 预创建
    return True, False, f"已切换会话：{sid}", sid
  if cmd == "mode" and args:
    mode = args[0].lower()
    if mode not in ("memory", "window", "sqlite"):
      return True, False, "支持：memory / window / sqlite", current_session
    _MEMORY_MODE = mode
    _SESSION_STORE.clear()
    return True, False, f"Memory 模式已切换为 {_MEMORY_MODE}（已重置 store）", current_session

  return True, False, f"未知命令 /{cmd}", current_session


def run_repl() -> int:
  print(BANNER)
  os.environ.setdefault("SPARKTECH_MOCK", "1")

  chain = build_chain_with_history()
  session_id = "default"
  call_count = 0

  print(f"mode={_MEMORY_MODE} | mock={is_mock_mode()} | session={session_id}")
  print("输入 /help 查看命令\n")

  while True:
    try:
      user_input = input("你> ").strip()
    except (EOFError, KeyboardInterrupt):
      print("\n已中断。")
      continue

    if not user_input:
      continue

    handled, should_exit, message, session_id = handle_command(
      user_input, current_session=session_id
    )
    if handled:
      if message:
        print(message)
      if should_exit:
        return 0
      continue

    try:
      call_count += 1
      config = {"configurable": {"session_id": session_id}}
      reply = chain.invoke({"user_input": user_input}, config=config)
      prefix = "[mock] " if is_mock_mode() else ""
      print(f"\n助手> {prefix}{reply}\n")
    except Exception as exc:
      print(f"[错误] {exc}")

  return 0


def main() -> None:
  raise SystemExit(run_repl())


if __name__ == "__main__":
  main()
