# -*- coding: utf-8 -*-
"""Day 52 · Alpaca 格式校验。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED = ("instruction", "output")


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]


def validate_record(rec: dict[str, Any]) -> ValidationResult:
    errors: list[str] = []
    for k in REQUIRED:
        if k not in rec or not str(rec[k]).strip():
            errors.append(f"missing_{k}")
    if "input" not in rec:
        errors.append("missing_input_key")
    return ValidationResult(len(errors) == 0, errors)


def validate_jsonl(path: Path) -> ValidationResult:
    errors: list[str] = []
    if not path.is_file():
        return ValidationResult(False, ["file_not_found"])
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        rec = json.loads(line)
        vr = validate_record(rec)
        if not vr.ok:
            errors.append(f"line{i}:{','.join(vr.errors)}")
    return ValidationResult(len(errors) == 0, errors)
