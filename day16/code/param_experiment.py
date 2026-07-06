# -*- coding: utf-8 -*-
"""
Day 16 · 单参数扫描实验

固定 prompt，扫描某一采样参数的不同取值，观察输出差异。

运行：
    cd day16/code
    python3 param_experiment.py --param temperature
    python3 param_experiment.py --param max_tokens
    python3 param_experiment.py --param frequency_penalty
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from llm_compat import get_llm_client, merge_params

CODE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = CODE_DIR / "output"

# 各参数扫描取值
SCAN_VALUES: dict[str, list[Any]] = {
    "temperature": [0.0, 0.3, 0.7, 1.0, 1.5],
    "top_p": [0.5, 0.8, 0.9, 0.95, 1.0],
    "max_tokens": [50, 100, 256, 512, 1024],
    "frequency_penalty": [0.0, 0.3, 0.6, 1.0, 1.5],
}

DEFAULT_MESSAGES = [
    {
        "role": "system",
        "content": "你是星火智服客服。回答简洁。",
    },
    {
        "role": "user",
        "content": "请介绍一下星火智服能帮我做什么，并说明退款政策要点。",
    },
]


def run_experiment(param_name: str, values: list[Any] | None = None) -> dict[str, Any]:
    """
    扫描单个参数，其余保持 demo 默认值。

    Returns:
        含 runs 列表的实验报告 dict
    """
    if param_name not in SCAN_VALUES:
        raise ValueError(f"不支持的参数: {param_name}")

    scan = values or SCAN_VALUES[param_name]
    client = get_llm_client()
    base = merge_params({})

    runs: list[dict[str, Any]] = []
    for val in scan:
        params = dict(base)
        params[param_name] = val
        resp = client.chat(DEFAULT_MESSAGES, **params)
        runs.append(
            {
                "param": param_name,
                "value": val,
                "response_preview": resp.text[:120] + ("…" if len(resp.text) > 120 else ""),
                "response_length": len(resp.text),
                "completion_tokens": resp.completion_tokens,
                "latency_ms": resp.latency_ms,
                "mode": resp.mode,
            }
        )

    return {
        "experiment": param_name,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "client_source": client.client_source,
        "mode": client.mode,
        "base_params": base,
        "runs": runs,
    }


def print_table(report: dict[str, Any]) -> None:
    """终端打印实验表格。"""
    param = report["experiment"]
    print(f"\n扫描参数: {param} | mode={report['mode']}")
    print(f"{'value':>10} {'len':>6} {'tok':>6} {'ms':>8}  preview")
    print("-" * 70)
    for r in report["runs"]:
        print(
            f"{r['value']!s:>10} {r['response_length']:>6} "
            f"{r['completion_tokens']:>6} {r['latency_ms']:>8.1f}  "
            f"{r['response_preview'][:40]}"
        )


def save_report(report: dict[str, Any]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"experiment_{report['experiment']}_{ts}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 16 单参数扫描")
    parser.add_argument(
        "--param",
        required=True,
        choices=list(SCAN_VALUES.keys()),
        help="要扫描的参数名",
    )
    args = parser.parse_args()

    print("=" * 60)
    print(f"Day 16 · param_experiment.py · 扫描 {args.param}")
    print("=" * 60)

    report = run_experiment(args.param)
    print_table(report)
    out = save_report(report)
    print(f"\n报告: {out}")

    print("\n观察要点:")
    if args.param == "temperature":
        print("  · 低温更稳定，高温 preview 中语气词可能更多")
    elif args.param == "max_tokens":
        print("  · 低 max_tokens 时 response_length 明显变短（可能被截断）")
    elif args.param == "frequency_penalty":
        print("  · 高 frequency_penalty 时 mock 会减少重复「您好」")
    print("\n✅ param_experiment.py 完成")


if __name__ == "__main__":
    main()
