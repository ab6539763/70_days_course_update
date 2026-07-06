# -*- coding: utf-8 -*-
"""
Day 16 · 同 prompt 多参数配置对比报告

业务场景：市场部需要数据支撑客户演示默认参数选型。

功能：
- 从 demo_prompts.json 读取 prompt
- 从 param_presets.json 读取多组 preset
- 同一 messages 分别调用，输出 JSON 对比报告
- --write-defaults 写入 output/demo_defaults.json

运行：
    cd day16/code
    python3 compare_params.py --prompt-id customer_demo
    python3 compare_params.py --prompt-id refund_policy --write-defaults
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from llm_compat import get_llm_client, load_demo_defaults

CODE_DIR = Path(__file__).resolve().parent
DATA_DIR = CODE_DIR / "data"
OUTPUT_DIR = CODE_DIR / "output"
PROMPTS_PATH = DATA_DIR / "demo_prompts.json"
PRESETS_PATH = DATA_DIR / "param_presets.json"


def load_prompts() -> dict[str, Any]:
    if not PROMPTS_PATH.is_file():
        raise FileNotFoundError(f"缺少 {PROMPTS_PATH}")
    return json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))["prompts"]


def load_presets() -> dict[str, Any]:
    if not PRESETS_PATH.is_file():
        raise FileNotFoundError(f"缺少 {PRESETS_PATH}")
    data = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))
    return data.get("presets", {}), data.get("demo_defaults", {})


def build_messages(prompt_entry: dict[str, str]) -> list[dict[str, str]]:
    """由 prompt 配置构造 messages。"""
    messages: list[dict[str, str]] = []
    if prompt_entry.get("system"):
        messages.append({"role": "system", "content": prompt_entry["system"]})
    messages.append({"role": "user", "content": prompt_entry["user"]})
    return messages


def compare_presets(
    prompt_id: str,
    preset_names: list[str] | None = None,
    *,
    use_stream: bool = False,
) -> dict[str, Any]:
    """
    对同一 prompt 运行多组 preset，收集对比数据。
    """
    prompts = load_prompts()
    if prompt_id not in prompts:
        raise KeyError(f"未知 prompt_id: {prompt_id}，可选: {list(prompts)}")

    presets, file_defaults = load_presets()
    names = preset_names or list(presets.keys())
    prompt_entry = prompts[prompt_id]
    messages = build_messages(prompt_entry)
    client = get_llm_client()

    runs: list[dict[str, Any]] = []
    for name in names:
        if name not in presets:
            continue
        preset = presets[name]
        params = {
            k: preset[k]
            for k in ("temperature", "top_p", "max_tokens", "frequency_penalty")
            if k in preset
        }

        if use_stream:
            stream_result = client.collect_stream(messages, **params)
            runs.append(
                {
                    "preset_name": name,
                    "preset_label": preset.get("label", name),
                    "params": params,
                    "response_text": stream_result.full_text,
                    "completion_tokens": stream_result.completion_tokens,
                    "latency_ms": stream_result.latency_ms,
                    "mode": stream_result.mode,
                    "stream": True,
                }
            )
        else:
            resp = client.chat(messages, **params)
            runs.append(
                {
                    "preset_name": name,
                    "preset_label": preset.get("label", name),
                    "params": params,
                    "response_text": resp.text,
                    "completion_tokens": resp.completion_tokens,
                    "latency_ms": resp.latency_ms,
                    "mode": resp.mode,
                    "stream": False,
                }
            )

    # 推荐 preset：标记 recommended 或 demo_balanced
    recommended = next(
        (n for n, p in presets.items() if p.get("recommended")),
        "demo_balanced",
    )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "prompt_id": prompt_id,
        "prompt_title": prompt_entry.get("title", prompt_id),
        "prompt_text": prompt_entry.get("user", ""),
        "client_source": client.client_source,
        "runs": runs,
        "recommended_preset": recommended,
        "demo_defaults": file_defaults,
    }


def print_summary(report: dict[str, Any]) -> None:
    print(f"\nprompt: {report['prompt_id']} — {report['prompt_title']}")
    print(f"客户端: {report['client_source']}")
    print(f"{'preset':<18} {'temp':>5} {'max_t':>6} {'freq':>5} {'len':>6} {'ms':>8}")
    print("-" * 55)
    for r in report["runs"]:
        p = r["params"]
        print(
            f"{r['preset_name']:<18} "
            f"{p.get('temperature', '-'):>5} "
            f"{p.get('max_tokens', '-'):>6} "
            f"{p.get('frequency_penalty', '-'):>5} "
            f"{len(r['response_text']):>6} "
            f"{r['latency_ms']:>8.1f}"
        )
    print(f"\n推荐 preset: {report['recommended_preset']}")


def save_report(report: dict[str, Any]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = OUTPUT_DIR / f"compare_report_{report['prompt_id']}_{ts}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_defaults(report: dict[str, Any]) -> Path:
    """将推荐默认参数写入 output/demo_defaults.json。"""
    defaults = dict(report.get("demo_defaults") or load_demo_defaults())
    defaults["recommended_preset"] = report["recommended_preset"]
    defaults["prompt_id"] = report["prompt_id"]
    defaults["generated_at"] = report["generated_at"]
    defaults["linked_clients"] = {
        "day12": str(CODE_DIR.parents[1] / "day12" / "code" / "llm_client.py"),
        "day13": str(CODE_DIR.parents[1] / "day13" / "code" / "resilient_llm_client.py"),
        "day14": str(CODE_DIR.parents[1] / "day14" / "project1" / "llm_client.py"),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / "demo_defaults.json"
    path.write_text(json.dumps(defaults, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 16 参数对比报告")
    parser.add_argument("--prompt-id", default="customer_demo", help="demo_prompts.json 中的 id")
    parser.add_argument(
        "--presets",
        type=str,
        default="",
        help="逗号分隔 preset 名，默认全部",
    )
    parser.add_argument("--stream", action="store_true", help="使用流式收集回复")
    parser.add_argument("--write-defaults", action="store_true", help="写入 demo_defaults.json")
    args = parser.parse_args()

    preset_names = [p.strip() for p in args.presets.split(",") if p.strip()] or None

    print("=" * 60)
    print("Day 16 · compare_params.py · 参数对比报告")
    print("=" * 60)

    report = compare_presets(
        args.prompt_id,
        preset_names,
        use_stream=args.stream,
    )
    print_summary(report)

    out = save_report(report)
    print(f"\n报告已保存: {out}")

    if args.write_defaults:
        dpath = write_defaults(report)
        print(f"默认参数已写入: {dpath}")

    print("\n✅ compare_params.py 完成")


if __name__ == "__main__":
    main()
