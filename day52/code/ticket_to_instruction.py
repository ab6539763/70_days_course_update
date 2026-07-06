# -*- coding: utf-8 -*-
"""Day 52 · 工单转 Alpaca 指令数据。"""

from __future__ import annotations

import json
import re
from pathlib import Path

RAW = Path(__file__).parent / "data" / "raw_tickets.json"
PHONE_RE = re.compile(r"1[3-9]\d{9}")
EMAIL_RE = re.compile(r"[\w.-]+@[\w.-]+\.\w+")


def desensitize(text: str) -> str:
    text = PHONE_RE.sub("[PHONE]", text)
    text = EMAIL_RE.sub("[EMAIL]", text)
    return text


def ticket_to_record(ticket: dict) -> dict:
    user = desensitize(ticket.get("user", ""))
    agent = desensitize(ticket.get("agent", ""))
    return {
        "instruction": f"作为星火智服客服回复：{user}",
        "input": "",
        "output": agent,
        "meta": {"ticket_id": ticket.get("ticket_id"), "category": ticket.get("category")},
    }


def convert(raw_path: Path | None = None) -> list[dict]:
    path = raw_path or RAW
    tickets = json.loads(path.read_text(encoding="utf-8"))
    return [ticket_to_record(t) for t in tickets]


def main() -> None:
    recs = convert()
    for r in recs:
        print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    main()
