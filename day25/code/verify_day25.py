# -*- coding: utf-8 -*-
"""Day 25 验收脚本 —— LangChain 入门 + Day 14 迁移 mock 模式。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ["SPARKTECH_MOCK"] = "1"
os.environ.pop("OPENAI_API_KEY", None)

from langchain_core.messages import AIMessage, HumanMessage  # noqa: E402

from langchain_chat import (  # noqa: E402
    LangChainSession,
    build_chat_chain,
    run_turn,
    save_session,
)
from mock_llm import build_chat_model, is_mock_mode  # noqa: E402
from prompt_templates_lc import (  # noqa: E402
    build_chat_prompt,
    build_simple_chat_prompt,
    build_string_prompt,
    format_chat_messages,
    format_string_prompt,
)


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_mock_mode() -> None:
    assert is_mock_mode()
    llm = build_chat_model()
    res = llm.invoke([HumanMessage(content="你好")])
    assert res.content
    ok("FakeListChatModel mock mode")


def test_prompt_template() -> None:
    text = format_string_prompt("星火智服", language="英文")
    assert "星火智服" in text
    assert "英文" in text

    tpl = build_string_prompt()
    assert set(tpl.input_variables) == {"product", "language"}
    ok("PromptTemplate format")


def test_chat_prompt_template() -> None:
    prompt = build_chat_prompt()
    msgs = prompt.format_messages(
        user_input="LangChain 是什么？",
        history=[HumanMessage(content="hi"), AIMessage(content="hello")],
    )
    assert len(msgs) >= 3
    assert any("LangChain" in str(m.content) for m in msgs)

    simple = build_simple_chat_prompt()
    assert "user_input" in simple.input_variables
    ok("ChatPromptTemplate + MessagesPlaceholder")


def test_format_chat_messages() -> None:
    msgs = format_chat_messages("测试")
    roles = [getattr(m, "type", "") for m in msgs]
    assert "human" in roles or "user" in str(roles)
    ok("format_chat_messages helper")


def test_langchain_session() -> None:
    session = LangChainSession(session_id="verify-s1")
    session.add_user("第一轮")
    session.add_assistant("回复一")
    assert len(session.history) == 2
    removed = session.clear()
    assert removed == 2
    assert len(session.history) == 0
    ok("LangChainSession clear/history")


def test_chat_chain_invoke() -> None:
    chain = build_chat_chain()
    session = LangChainSession(session_id="verify-chain")
    reply = run_turn(chain, session, "你好", call_index=1)
    assert "mock" in reply.lower() or "收到" in reply
    assert len(session.history) == 2
    ok("prompt | llm chain run_turn")


def test_save_session() -> None:
    session = LangChainSession(session_id="verify-save")
    session.add_user("保存测试")
    session.add_assistant("ok")
    path = save_session(session, "verify_day25_session.json")
    assert path.exists()
    data = path.read_text(encoding="utf-8")
    assert "verify-save" in data
    ok("save_session JSON")


def main() -> None:
    print("=== Day 25 verify ===\n")
    test_mock_mode()
    test_prompt_template()
    test_chat_prompt_template()
    test_format_chat_messages()
    test_langchain_session()
    test_chat_chain_invoke()
    test_save_session()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
