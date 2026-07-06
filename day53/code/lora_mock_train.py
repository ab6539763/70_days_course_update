# -*- coding: utf-8 -*-
"""Day 53 · 模拟 LoRA 训练（无 GPU）。"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TrainLog:
    epoch: int
    step: int
    loss: float


def mock_train(*, epochs: int = 3, steps_per_epoch: int = 5) -> list[TrainLog]:
    logs: list[TrainLog] = []
    loss = 2.5
    for ep in range(1, epochs + 1):
        for step in range(1, steps_per_epoch + 1):
            loss = max(0.3, loss * 0.85 + 0.05 * math.sin(step))
            logs.append(TrainLog(ep, step, round(loss, 4)))
    return logs


def main() -> None:
    mock = os.environ.get("SPARKTECH_MOCK", "1") == "1"
    logs = mock_train()
    out = Path(__file__).parent / "output" / "mock_train_log.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps([asdict(x) for x in logs], indent=2), encoding="utf-8")
    print(f"mock={mock} final_loss={logs[-1].loss} saved={out}")


if __name__ == "__main__":
    main()
