# -*- coding: utf-8 -*-
"""
Day 13 综合实操 · 弹性 LLM 客户端端到端演示

整合：
- dotenv 加载 OPENAI_API_KEY
- ResilientLLMClient（retry + timeout）
- mock 模式无 Key 可跑

运行：cd day13/code && python3 run_resilient_demo.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE_DIR))

from llm_client import load_dotenv_file
from resilient_llm_client import ResilientLLMClient, SimulatedFlakyClient


def main() -> None:
    load_dotenv_file()

    print("=" * 60)
    print("星火智服 · Day 13 弹性 LLM 客户端综合演示")
    print("=" * 60)

    client = ResilientLLMClient(max_retries=3, retry_delay=0.2, timeout=15.0)
    print(f"\n客户端模式: {client.mode} | 模型: {client.model}")

    messages = [
        {"role": "system", "content": "你是星火智服技术支持助手，回答简洁。"},
        {"role": "user", "content": "生产环境 API 调用失败，retry 和 timeout 分别解决什么问题？"},
    ]

    print("\n--- 正常调用 ---")
    result = client.chat(messages)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))

    print("\n--- 模拟故障恢复（教学）---")
    flaky = SimulatedFlakyClient(fail_times=2, max_retries=4, retry_delay=0.1)
    recovered = flaky.chat([{"role": "user", "content": "故障恢复测试"}])
    print(json.dumps(recovered.to_dict(), ensure_ascii=False, indent=2))

    print("\n✅ run_resilient_demo.py 完成")
    print("提示: 配置 .env 中 OPENAI_API_KEY 可切换 live 模式")


if __name__ == "__main__":
    main()
