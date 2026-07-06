# -*- coding: utf-8 -*-
"""Day 14 · CLI 斜杠命令处理器。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from project1.session import ConversationSession
from project1.storage import save_session

HELP_TEXT = """
星火智服 · 命令行多轮对话助手（Day 14 Stage Project 1）

斜杠命令：
  /help              显示本帮助
  /clear             清空对话历史（保留 system 提示词）
  /save [文件名]     保存当前会话到 data/sessions/
  /exit              退出程序（同 /quit）

直接输入文字即可与 AI 对话；多轮上下文由 ConversationSession 维护。
""".strip()


@dataclass
class CommandResult:
    """命令执行结果。"""

    handled: bool
    should_exit: bool = False
    message: str = ""


class CommandHandler:
    """解析并执行 /clear /save /exit /help 等命令。"""

    def __init__(
        self,
        session: ConversationSession,
        *,
        sessions_dir: Path | None = None,
    ) -> None:
        self.session = session
        self.sessions_dir = sessions_dir
        self._dispatch: dict[str, Callable[[list[str]], CommandResult]] = {
            "help": self._cmd_help,
            "clear": self._cmd_clear,
            "save": self._cmd_save,
            "exit": self._cmd_exit,
            "quit": self._cmd_exit,
        }

    def is_command(self, text: str) -> bool:
        return text.strip().startswith("/")

    def handle(self, text: str) -> CommandResult:
        raw = text.strip()
        if not raw.startswith("/"):
            return CommandResult(handled=False)

        parts = raw[1:].split()
        if not parts:
            return CommandResult(handled=True, message="未知命令。输入 /help 查看帮助。")

        name = parts[0].lower()
        args = parts[1:]
        handler = self._dispatch.get(name)
        if handler is None:
            return CommandResult(
                handled=True,
                message=f"未知命令 /{name}。输入 /help 查看帮助。",
            )
        return handler(args)

    def _cmd_help(self, _args: list[str]) -> CommandResult:
        return CommandResult(handled=True, message=HELP_TEXT)

    def _cmd_clear(self, _args: list[str]) -> CommandResult:
        removed = self.session.clear(keep_system=True)
        return CommandResult(
            handled=True,
            message=f"已清空对话历史，移除 {removed} 条消息（system 提示词已保留）。",
        )

    def _cmd_save(self, args: list[str]) -> CommandResult:
        try:
            if args:
                filename = args[0]
                if not filename.endswith(".json"):
                    filename += ".json"
                path = save_session(
                    self.session,
                    base_dir=self.sessions_dir,
                    path=(self.sessions_dir / filename) if self.sessions_dir else None,
                )
            else:
                path = save_session(self.session, base_dir=self.sessions_dir)
            return CommandResult(
                handled=True,
                message=f"会话已保存：{path}",
            )
        except Exception as exc:
            return CommandResult(handled=True, message=f"保存失败：{exc}")

    def _cmd_exit(self, _args: list[str]) -> CommandResult:
        return CommandResult(handled=True, should_exit=True, message="再见，星火智服助手已退出。")
