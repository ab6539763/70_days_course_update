# -*- coding: utf-8 -*-
"""Day 53 · LoRA 低秩直觉演示（纯 numpy）。"""

from __future__ import annotations


def lora_delta_demo(d: int = 64, r: int = 4) -> dict:
    full_params = d * d
    lora_params = d * r + r * d
    return {
        "d": d,
        "r": r,
        "full_params": full_params,
        "lora_params": lora_params,
        "ratio": round(lora_params / full_params, 4),
    }


def main() -> None:
    for r in (4, 8, 16):
        info = lora_delta_demo(r=r)
        print(f"r={r} params_ratio={info['ratio']}")


if __name__ == "__main__":
    main()
