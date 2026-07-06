# -*- coding: utf-8 -*-
"""
Day 15 · 星火智服 API Token 成本估算器

业务场景：产品部需要二期立项书中的月度 API 成本区间。

功能：
- 读取方案/场景文本，tiktoken 统计输入 Token
- 按 price_table.json 计算多模型、多档位月费
- 可选 --live-sample 调用 Day 13 客户端对比 API usage

运行：
    cd day15/code
    python3 token_cost_estimator.py
    python3 token_cost_estimator.py --scenario data/xinghuo_proposal.txt --tiers low,medium,high
    python3 token_cost_estimator.py --live-sample   # 需 OPENAI_API_KEY
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from tiktoken_demo import count_messages_tokens, count_tokens
from llm_compat import get_llm_client, CLIENT_SOURCE

CODE_DIR = Path(__file__).resolve().parent
DATA_DIR = CODE_DIR / "data"
OUTPUT_DIR = CODE_DIR / "output"
DEFAULT_SCENARIO = DATA_DIR / "xinghuo_proposal.txt"
PRICE_TABLE_PATH = DATA_DIR / "price_table.json"

# 三档商务假设（日均请求次数, 假设输出 Token）
TIER_PRESETS: dict[str, dict[str, int]] = {
    "low": {"daily_requests": 200, "output_tokens": 150},
    "medium": {"daily_requests": 500, "output_tokens": 300},
    "high": {"daily_requests": 2000, "output_tokens": 500},
}

# 内置单价（price_table.json 缺失时使用）
DEFAULT_PRICE_TABLE: dict[str, dict[str, float]] = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
    "gpt-4o": {"input": 2.5, "output": 10.0},
    "deepseek-chat": {"input": 0.14, "output": 0.28},
    "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
}

FX_USD_TO_CNY = 7.25
DAYS_PER_MONTH = 30


def load_price_table(path: Path = PRICE_TABLE_PATH) -> tuple[dict[str, dict[str, float]], float]:
    """
    加载模型单价表。

    Returns:
        (models_dict, fx_usd_to_cny)
    """
    if not path.is_file():
        return DEFAULT_PRICE_TABLE, FX_USD_TO_CNY

    data = json.loads(path.read_text(encoding="utf-8"))
    models = data.get("models", DEFAULT_PRICE_TABLE)
    fx = float(data.get("fx_usd_to_cny", FX_USD_TO_CNY))
    return models, fx


def build_scenario_messages(scenario_text: str) -> list[dict[str, str]]:
    """
    将方案文本包装为一次典型 API 请求的 messages。

    结构：系统提示 + 方案节选作为知识上下文 + 示例用户问题。
    """
    return [
        {
            "role": "system",
            "content": (
                "你是星火智服成本测算助手。根据以下方案背景回答产品问询，"
                "回答简洁、可引用数据。"
            ),
        },
        {
            "role": "user",
            "content": (
                "【方案背景】\n"
                f"{scenario_text[:3000]}\n\n"
                "【问题】请评估单次客服对话的输入 Token 规模，并说明影响成本的关键因素。"
            ),
        },
    ]


def calc_single_request_cost_usd(
    input_tokens: int,
    output_tokens: int,
    input_price_per_m: float,
    output_price_per_m: float,
) -> float:
    """单次请求美元成本。"""
    return (input_tokens / 1_000_000) * input_price_per_m + (
        output_tokens / 1_000_000
    ) * output_price_per_m


def estimate_cost(
    scenario_text: str,
    *,
    daily_requests: int = 500,
    output_tokens: int = 300,
    rag_chunks: int = 0,
    chunk_tokens: int = 400,
    models: list[str] | None = None,
    price_table: dict[str, dict[str, float]] | None = None,
    fx: float = FX_USD_TO_CNY,
) -> dict[str, Any]:
    """
    核心估算逻辑。

    Args:
        scenario_text: 方案或场景全文
        daily_requests: 日均 API 请求次数
        output_tokens: 假设每次输出 Token 数
        rag_chunks: RAG 检索片段数量（0 表示不加）
        chunk_tokens: 每段检索片段 Token 数
    """
    messages = build_scenario_messages(scenario_text)
    input_tokens, count_method = count_messages_tokens(messages)
    input_tokens += rag_chunks * chunk_tokens

    table = price_table or DEFAULT_PRICE_TABLE
    model_names = models or list(table.keys())

    model_results: list[dict[str, Any]] = []
    for name in model_names:
        prices = table.get(name)
        if not prices:
            continue
        per_request = calc_single_request_cost_usd(
            input_tokens,
            output_tokens,
            float(prices["input"]),
            float(prices["output"]),
        )
        monthly_usd = per_request * daily_requests * DAYS_PER_MONTH
        model_results.append(
            {
                "model": name,
                "input_price_per_1m": prices["input"],
                "output_price_per_1m": prices["output"],
                "per_request_usd": round(per_request, 6),
                "monthly_cost_usd": round(monthly_usd, 2),
                "monthly_cost_cny": round(monthly_usd * fx, 2),
            }
        )

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_tokens": input_tokens,
        "output_tokens_assumed": output_tokens,
        "token_count_method": count_method,
        "rag_extra_tokens": rag_chunks * chunk_tokens,
        "assumptions": {
            "daily_requests": daily_requests,
            "days_per_month": DAYS_PER_MONTH,
            "output_tokens": output_tokens,
            "rag_chunks": rag_chunks,
            "chunk_tokens": chunk_tokens,
        },
        "models": model_results,
    }


def estimate_tiers(
    scenario_text: str,
    tier_names: list[str],
    **kwargs: Any,
) -> dict[str, Any]:
    """按低/中/高三档分别估算。"""
    tiers: dict[str, Any] = {}
    for name in tier_names:
        preset = TIER_PRESETS.get(name, TIER_PRESETS["medium"])
        tiers[name] = estimate_cost(
            scenario_text,
            daily_requests=preset["daily_requests"],
            output_tokens=preset["output_tokens"],
            **kwargs,
        )
    return {"tiers": tiers, "tier_names": tier_names}


def live_usage_sample(scenario_text: str) -> dict[str, Any] | None:
    """
    调用 Day 12/13 客户端发一条样例请求，对比 API 返回的 usage。

    无 Key 时仍 mock 返回，用于演示字段对齐。
    """
    client = get_llm_client()
    messages = build_scenario_messages(scenario_text)
    # 截断 user 内容避免 mock 过长
    short_messages = [
        messages[0],
        {"role": "user", "content": "请用一句话说明 Token 成本如何估算。"},
    ]
    resp = client.chat(short_messages)

    tiktoken_in, _ = count_messages_tokens(short_messages)
    api_in = getattr(resp, "prompt_tokens", 0) or 0
    api_out = getattr(resp, "completion_tokens", 0) or 0

    return {
        "client_source": CLIENT_SOURCE,
        "mode": getattr(resp, "mode", "unknown"),
        "model": getattr(resp, "model", getattr(client, "model", "")),
        "tiktoken_input_estimate": tiktoken_in,
        "api_prompt_tokens": api_in,
        "api_completion_tokens": api_out,
        "delta_input": api_in - tiktoken_in if api_in else None,
    }


def save_report(data: dict[str, Any], prefix: str = "cost_estimate") -> Path:
    """写入 output/ 目录 JSON 报告。"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = OUTPUT_DIR / f"{prefix}_{ts}.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


def print_summary(report: dict[str, Any]) -> None:
    """终端打印摘要表。"""
    if "tiers" in report:
        for tier_name, tier_data in report["tiers"].items():
            print(f"\n── 档位: {tier_name} ──")
            _print_single_tier(tier_data)
        return
    _print_single_tier(report)


def _print_single_tier(data: dict[str, Any]) -> None:
    print(f"输入 Token: {data['input_tokens']} ({data['token_count_method']})")
    assump = data["assumptions"]
    print(
        f"假设: 日均 {assump['daily_requests']} 次 × "
        f"{assump['days_per_month']} 天, 输出 {assump['output_tokens']} tokens/次"
    )
    print(f"{'模型':<22} {'月费(USD)':>12} {'月费(CNY)':>12}")
    print("-" * 48)
    for m in data["models"]:
        print(
            f"{m['model']:<22} {m['monthly_cost_usd']:>12.2f} "
            f"{m['monthly_cost_cny']:>12.2f}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="星火智服 Token 成本估算")
    parser.add_argument(
        "--scenario",
        type=Path,
        default=DEFAULT_SCENARIO,
        help="场景文本路径",
    )
    parser.add_argument("--daily-requests", type=int, default=500)
    parser.add_argument("--output-tokens", type=int, default=300)
    parser.add_argument("--rag-chunks", type=int, default=0)
    parser.add_argument("--chunk-tokens", type=int, default=400)
    parser.add_argument(
        "--tiers",
        type=str,
        default="",
        help="逗号分隔档位名: low,medium,high",
    )
    parser.add_argument(
        "--live-sample",
        action="store_true",
        help="调用 Day12/13 客户端对比 usage",
    )
    args = parser.parse_args()

    if not args.scenario.is_file():
        raise SystemExit(f"场景文件不存在: {args.scenario}")

    scenario_text = args.scenario.read_text(encoding="utf-8")
    price_table, fx = load_price_table()

    print("=" * 60)
    print("Day 15 · token_cost_estimator · 星火智服成本估算")
    print("=" * 60)
    print(f"场景文件: {args.scenario}")

    if args.tiers.strip():
        tier_names = [t.strip() for t in args.tiers.split(",") if t.strip()]
        report: dict[str, Any] = {
            "scenario_file": str(args.scenario),
            **estimate_tiers(
                scenario_text,
                tier_names,
                rag_chunks=args.rag_chunks,
                chunk_tokens=args.chunk_tokens,
                price_table=price_table,
                fx=fx,
            ),
        }
    else:
        report = {
            "scenario_file": str(args.scenario),
            **estimate_cost(
                scenario_text,
                daily_requests=args.daily_requests,
                output_tokens=args.output_tokens,
                rag_chunks=args.rag_chunks,
                chunk_tokens=args.chunk_tokens,
                price_table=price_table,
                fx=fx,
            ),
        }

    if args.live_sample:
        live = live_usage_sample(scenario_text)
        if live:
            report["live_usage_sample"] = live
            print(f"\n[live] 客户端: {live['client_source']} | mode={live['mode']}")
            print(
                f"  tiktoken 输入≈{live['tiktoken_input_estimate']} | "
                f"API prompt={live['api_prompt_tokens']}"
            )

    print_summary(report)
    out = save_report(report)
    print(f"\n报告已保存: {out}")
    print("✅ token_cost_estimator.py 完成")


if __name__ == "__main__":
    main()
