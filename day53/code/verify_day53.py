# -*- coding: utf-8 -*-
"""Day 53 验收脚本 —— SPARKTECH_MOCK=1 无需 GPU / API Key。"""

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
    print("=== Day 53 verify ===")

    from lora_math_demo import lora_delta_demo
    from lora_config_explainer import save_config
    from lora_mock_train import mock_train
    from pathlib import Path

    info = lora_delta_demo(r=8)
    if info["lora_params"] >= info["full_params"]:
        fail("lora should reduce params")
    ok("lora_math_demo")

    cfg_path = Path(__file__).parent / "configs" / "lora_sparktech.json"
    save_config(cfg_path)
    if not cfg_path.is_file():
        fail("config not saved")
    ok("lora_config")

    logs = mock_train(epochs=2, steps_per_epoch=3)
    if logs[-1].loss >= logs[0].loss:
        fail("loss should decrease in mock")
    ok("lora_mock_train")

    print("=== ALL PASSED ===")


if __name__ == "__main__":
    main()
