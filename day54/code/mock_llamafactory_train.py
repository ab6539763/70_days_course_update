# -*- coding: utf-8 -*-
"""Day 54 · 模拟 LLaMA-Factory 训练输出目录结构。"""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT = Path(__file__).parent / "output" / "sparktech_lora"


def run_mock_train() -> Path:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    adapter = {
        "peft_type": "LORA",
        "r": 8,
        "lora_alpha": 16,
        "target_modules": ["q_proj", "v_proj"],
        "base_model": "Qwen/Qwen2.5-7B-Instruct",
    }
    (OUTPUT / "adapter_config.json").write_text(json.dumps(adapter, indent=2), encoding="utf-8")
    (OUTPUT / "adapter_model.bin").write_bytes(b"MOCK_LORA_WEIGHTS_SPARKTECH")
    (OUTPUT / "trainer_log.jsonl").write_text(
        '{"loss": 1.2, "step": 10}\n{"loss": 0.8, "step": 20}\n',
        encoding="utf-8",
    )
    readme = OUTPUT / "README.txt"
    readme.write_text(
        "Mock adapter for teaching. Replace with real LLaMA-Factory output on GPU.\n",
        encoding="utf-8",
    )
    return OUTPUT


if __name__ == "__main__":
    p = run_mock_train()
    print(f"mock adapter at {p}")
