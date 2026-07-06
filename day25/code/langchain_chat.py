# -*- coding: utf-8 -*-
"""Day 25 · 用 LangChain 重写 Day 14 命令行多轮对话助手。

运行：
  cd day25/code && python langchain_chat.py
  或
  cd day25 && bash run.sh
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda

from mock_llm import build_chat_model, is_mock_mode, mock_reply_for_user
from prompt_templates_lc import DEFAULT_SYSTEM_PROMPT, build_chat_prompt

CODE_DIR = Path(__file__).resolve().parent
SESSIONS_DIR = CODE_DIR / "data" / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

HELP_TEXT = """
星火智服 · Day 25 LangChain CLI（由 Day 14 project1 迁移）

斜杠命令：
  /help              显示本帮助
  /clear             清空对话历史（保留 system）
  /save [文件名]     保存会话到 data/sessions/
  /exit              退出（同 /quit）

直接输入文字即可对话；底层使用 ChatPromptTemplate + ChatModel。
""".strip()

BANNER = """
╔══════════════════════════════════════════════════════════╗
║  星火智服 · Day 25 LangChain CLI                         ║
║  Phase2：将 Day 14 助手迁移到 LangChain 栈               ║
╚══════════════════════════════════════════════════════════╝
输入 /help 查看命令；直接输入文字开始对话。
""".strip()


class LangChainSession:
    """维护 LangChain Message 列表的会话对象。"""

    def __init__(
        self,
        *,
        session_id: str | None = None,
        title: str = "未命名会话",
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    ) -> None:
        self.session_id = session_id or uuid4().hex[:12]
        self.title = title
        now = datetime.now(timezone.utc).isoformat()
        self.created_at = now
        self.updated_at = now
        self._messages: list[BaseMessage] = [SystemMessage(content=system_prompt)]

    @property
    def history(self) -> list[BaseMessage]:
        """供 ChatPromptTemplate MessagesPlaceholder 使用的历史（不含 system）。"""
        return [m for m in self._messages if not isinstance(m, SystemMessage)]

    def add_user(self, text: str) -> None:
        self._messages.append(HumanMessage(content=text))
        self._touch()

    def add_assistant(self, text: str) -> None:
        self._messages.append(AIMessage(content=text))
        self._touch()

    def clear(self, *, keep_system: bool = True) -> int:
        before = len(self._messages)
        if keep_system:
            self._messages = [m for m in self._messages if isinstance(m, SystemMessage)]
        else:
            self._messages = []
        self._touch()
        return before - len(self._messages)

    def summary(self) -> str:
        user_count = sum(1 for m in self._messages if isinstance(m, HumanMessage))
        assistant_count = sum(1 for m in self._messages if isinstance(m, AIMessage))
        return (
            f"会话 {self.session_id} | {self.title} | "
            f"共 {len(self._messages)} 条（user={user_count}, assistant={assistant_count}）"
        )

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": [
                {"role": _role_of(m), "content": str(m.content)} for m in self._messages
            ],
        }

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc).isoformat()


def _role_of(msg: BaseMessage) -> str:
    if isinstance(msg, SystemMessage):
        return "system"
    if isinstance(msg, HumanMessage):
        return "user"
    if isinstance(msg, AIMessage):
        return "assistant"
    return getattr(msg, "type", "unknown")


def save_session(session: LangChainSession, filename: str | None = None) -> Path:
    """保存会话 JSON 到 data/sessions/。"""
    name = filename or f"{session.session_id}.json"
    if not name.endswith(".json"):
        name += ".json"
    path = SESSIONS_DIR / name
    path.write_text(json.dumps(session.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_chat_chain():
    """构建 prompt | llm 链（Day 25 核心）。"""
    prompt = build_chat_prompt()
    llm = build_chat_model()

    def _inject_history(inputs: dict) -> dict:
        return {
            "user_input": inputs["user_input"],
            "history": inputs.get("history", []),
        }

    return RunnableLambda(_inject_history) | prompt | llm


def run_turn(chain, session: LangChainSession, user_input: str, *, call_index: int) -> str:
    """执行一轮对话并更新 session。"""
    session.add_user(user_input)

    if is_mock_mode():
        # FakeListChatModel 不读上下文，用 Day 14 风格 mock 文案增强教学对比
        reply = mock_reply_for_user(user_input, call_index=call_index)
    else:
        result = chain.invoke(
            {"user_input": user_input, "history": session.history[:-1]}
        )
        reply = str(getattr(result, "content", result))

    session.add_assistant(reply)
    return reply


def handle_command(text: str, session: LangChainSession) -> tuple[bool, bool, str]:
    """处理斜杠命令。返回 (handled, should_exit, message)。"""
    raw = text.strip()
    if not raw.startswith("/"):
        return False, False, ""

    parts = raw[1:].split()
    if not parts:
        return True, False, "未知命令。输入 /help 查看帮助。"

    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "help":
        return True, False, HELP_TEXT
    if cmd in ("exit", "quit"):
        return True, True, "再见，星火智服 LangChain 助手已退出。"
    if cmd == "clear":
        removed = session.clear(keep_system=True)
        return True, False, f"已清空对话历史，移除 {removed} 条消息（system 已保留）。"
    if cmd == "save":
        try:
            filename = args[0] if args else None
            path = save_session(session, filename)
            return True, False, f"会话已保存：{path}"
        except Exception as exc:
            return True, False, f"保存失败：{exc}"

    return True, False, f"未知命令 /{cmd}。输入 /help 查看帮助。"


def run_repl() -> int:
    """主 REPL 循环。"""
    print(BANNER)
    os.environ.setdefault("SPARKTECH_MOCK", "1")

    session = LangChainSession()
    chain = build_chat_chain()
    call_index = 0

    mode = "mock" if is_mock_mode() else "live"
    print(f"LangChain ChatModel mode={mode}")
    print(session.summary())
    print()

    while True:
        try:
            user_input = input("你> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已中断，输入 /exit 可正常退出。")
            continue

        if not user_input:
            continue

        handled, should_exit, message = handle_command(user_input, session)
        if handled:
            if message:
                print(message)
            if should_exit:
                return 0
            continue

        try:
            call_index += 1
            reply = run_turn(chain, session, user_input, call_index=call_index)
            prefix = "[mock] " if is_mock_mode() else ""
            print(f"\n助手> {prefix}{reply}\n")
        except Exception as exc:
            print(f"[错误] {exc}")

    return 0


def main() -> None:
    raise SystemExit(run_repl())


if __name__ == "__main__":
    main()
