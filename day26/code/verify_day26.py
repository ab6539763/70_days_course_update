# -*- coding: utf-8 -*-
"""Day 26 验收脚本 —— LCEL、OutputParser、Parallel。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

os.environ["SPARKTECH_MOCK"] = "1"
os.environ.pop("OPENAI_API_KEY", None)

from lcel_chain_demo import (  # noqa: E402
    build_json_chain,
    build_parallel_chain,
    build_pydantic_chain,
    build_simple_lcel_chain,
)
from translation_chain import build_translation_chain, translate  # noqa: E402


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def test_simple_lcel() -> None:
    chain = build_simple_lcel_chain()
    out = chain.invoke({"question": "什么是 LCEL？"})
    assert isinstance(out, str) and len(out) > 0
    ok(f"prompt | llm | StrOutputParser → {out[:40]}...")


def test_json_parser() -> None:
    chain = build_json_chain()
    data = chain.invoke({"ticket_id": "TK-100"})
    assert isinstance(data, dict)
    assert data.get("ticket_id")
    assert "status" in data
    ok("JsonOutputParser")


def test_pydantic_parser() -> None:
    chain = build_pydantic_chain()
    data = chain.invoke({"ticket_id": "TK-200", "user_text": "太慢了"})
    assert data["ticket_id"] == "TK-200"
    assert data["sentiment"] in ("positive", "neutral", "negative")
    ok("Pydantic JsonOutputParser")


def test_runnable_parallel() -> None:
    chain = build_parallel_chain()
    result = chain.invoke("abc")
    assert result["question"] == "abc"
    assert result["length"] == 3
    assert result["upper"] == "ABC"
    ok("RunnableParallel + Passthrough")


def test_translation_chain() -> None:
    en = translate("星火智服智能客服平台", "英文")
    assert "SparkTech" in en or "mock" in en.lower()

    jp = translate("星火智服智能客服平台", "日文")
    assert jp

    chain = build_translation_chain()
    raw = chain.invoke(
        {"source_text": "测试", "target_language": "英文", "source_lang": "中文"}
    )
    assert isinstance(raw, str)
    ok("translation_chain LCEL")


def main() -> None:
    print("=== Day 26 verify ===\n")
    test_simple_lcel()
    test_json_parser()
    test_pydantic_parser()
    test_runnable_parallel()
    test_translation_chain()
    print("\n=== All checks passed ===")


if __name__ == "__main__":
    main()
