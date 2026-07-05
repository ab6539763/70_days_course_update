#!/usr/bin/env python3
"""
Day 9 综合实操 · 星火智服多厂商 LLM 路由（mock）

运行：python3 run_llm_demo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# 保证从 code/ 目录直接运行时可 import 同级模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from base_model import BaseModel, GenerationResult
from openai_model import OpenAIModel
from qwen_model import QwenModel


def build_default_registry() -> list[BaseModel]:
  """按配置组装模型列表 —— 业务层只返回 BaseModel 接口。"""
  return [
    OpenAIModel(
      model_name="gpt-4o",
      api_key="sk-openai-mock-day09",
      temperature=0.7,
    ),
    OpenAIModel(
      model_name="gpt-4o-mini",
      api_key="sk-openai-mock-day09",
      temperature=0.3,
    ),
    QwenModel(
      model_name="qwen-plus",
      api_key="sk-qwen-mock-day09",
      temperature=0.8,
      region="cn-beijing",
    ),
    QwenModel(
      model_name="qwen-turbo",
      temperature=0.5,
      region="cn-shanghai",
    ),
  ]


def generate_all(models: list[BaseModel], prompt: str) -> list[dict]:
  """对同一 prompt 调用所有模型，返回可 JSON 序列化的结果。"""
  rows: list[dict] = []
  for model in models:
    result: GenerationResult = model(prompt)  # __call__
    rows.append(
      {
        "vendor": result.vendor,
        "model": result.model,
        "text": result.text,
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "latency_ms": result.latency_ms,
      }
    )
  return rows


def pick_model(models: list[BaseModel], vendor: str) -> BaseModel | None:
  for m in models:
    if m.vendor == vendor:
      return m
  return None


def main() -> None:
  print("=" * 60)
  print("星火智服 · Day 9 LLM 统一接口实操（mock）")
  print("=" * 60)

  registry = build_default_registry()
  print("\n已注册模型：")
  for i, m in enumerate(registry, 1):
    print(f"  {i}. {m}")

  prompt = "请用三句话向客户解释星火智服工单系统的用法。"
  print(f"\n统一 Prompt:\n  {prompt}\n")

  results = generate_all(registry, prompt)
  print("多模型并行 mock 结果：")
  print(json.dumps(results, ensure_ascii=False, indent=2))

  print("\n--- 按厂商多态调用 ---")
  qwen = pick_model(registry, "qwen")
  if isinstance(qwen, QwenModel):
    search_result = qwen.generate_with_search("今日值班 FAQ")
    print(search_result)

  print("\n--- 调用统计 ---")
  for m in registry:
    print(f"  {m.model_name}: call_count={m.call_count}")

  print("\n✅ run_llm_demo.py 完成")


if __name__ == "__main__":
  main()
