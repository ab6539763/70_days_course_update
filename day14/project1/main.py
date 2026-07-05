# -*- coding: utf-8 -*-
"""Day 14 Stage Project 1 · 命令行多轮对话 AI 助手 CLI 入口。

运行：
  cd day14 && bash run.sh
  或
  python -m project1.main
"""

from __future__ import annotations

import sys
from pathlib import Path

# 教学阶段：将 day14 根目录加入 sys.path，便于 import sparktech 与 project1
_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sparktech.exceptions import SparkTechError  # noqa: E402

from project1.commands import CommandHandler, HELP_TEXT  # noqa: E402
from project1.llm_client import LLMClient, LLMClientError  # noqa: E402
from project1.session import ConversationSession  # noqa: E402
from project1.storage import DEFAULT_SESSIONS_DIR  # noqa: E402


BANNER = """
╔══════════════════════════════════════════════════════════╗
║  星火智服 · Day 14 Stage Project 1                       ║
║  命令行多轮对话 AI 助手（Week 2 阶段项目答辩）            ║
╚══════════════════════════════════════════════════════════╝
输入 /help 查看命令；直接输入文字开始对话。
""".strip()


def run_repl() -> int:
    """主 REPL 循环。"""
    print(BANNER)

    try:
        client = LLMClient()
    except SparkTechError as exc:
        print(f"[配置错误] {exc.message}")
        return 1

    session = ConversationSession()
    commands = CommandHandler(session, sessions_dir=DEFAULT_SESSIONS_DIR)
    print(client.describe())
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

        if commands.is_command(user_input):
            result = commands.handle(user_input)
            if result.message:
                print(result.message)
            if result.should_exit:
                return 0
            continue

        try:
            session.add_user_message(user_input)
            completion = client.chat(session.to_api_messages())
            session.add_assistant_message(completion.text)
            prefix = "[mock] " if completion.mock else ""
            print(f"\n助手> {prefix}{completion.text}\n")
        except ValueError as exc:
            print(f"[输入错误] {exc}")
        except LLMClientError as exc:
            print(f"[LLM 错误] {exc.message}")
        except SparkTechError as exc:
            print(f"[业务错误] {exc.message}")
        except Exception as exc:
            print(f"[未知错误] {exc}")

    return 0


def main() -> None:
    raise SystemExit(run_repl())


if __name__ == "__main__":
    main()
