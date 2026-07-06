# -*- coding: utf-8 -*-
"""Day 54 验收脚本 —— SPARKTECH_MOCK=1 无需 GPU / API Key。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))
os.environ.setdefault("SPARKTECH_MOCK", "1")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def main() -> None:
    print("=== Day 54 verify ===")

    from pathlib import Path
    from mock_llamafactory_train import run_mock_train
    import json

    yaml = Path(__file__).parent / "llamafactory_configs" / "sparktech_qwen_lora.yaml"
    if "lora_rank" not in yaml.read_text(encoding="utf-8"):
        fail("yaml missing lora_rank")
    ok("llamafactory yaml")

    out = run_mock_train()
    cfg = out / "adapter_config.json"
    if not cfg.is_file():
        fail("adapter_config missing")
    data = json.loads(cfg.read_text(encoding="utf-8"))
    if data.get("peft_type") != "LORA":
        fail("not LORA")
    ok("mock adapter output")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
