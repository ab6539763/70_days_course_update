# -*- coding: utf-8 -*-
"""Day 53 · LoRA 配置解释器。"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass
class LoRAConfig:
    r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: tuple[str, ...] = ("q_proj", "v_proj")
    bias: str = "none"

    def explain(self) -> str:
        return (
            f"rank={self.r}, alpha={self.lora_alpha} (scale={self.lora_alpha/self.r}), "
            f"targets={list(self.target_modules)}"
        )


def save_config(path: Path) -> LoRAConfig:
    cfg = LoRAConfig()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")
    return cfg


if __name__ == "__main__":
    cfg = save_config(Path(__file__).parent / "configs" / "lora_sparktech.json")
    print(cfg.explain())
