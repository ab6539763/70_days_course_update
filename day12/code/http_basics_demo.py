#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Day 12 · HTTP 基础演示

通过 requests 访问 httpbin.org，理解：
- GET / POST 方法
- 状态码 status_code
- 请求头 headers、响应头
- 请求体 body（JSON）
"""

from __future__ import annotations

import json
from typing import Any

import requests

HTTPBIN_BASE = "https://httpbin.org"
TIMEOUT = 15


def print_section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print("=" * 60)


def demo_get() -> None:
    """GET：从 URL 获取资源，参数通常放在 query string。"""
    print_section("1. GET 请求")
    url = f"{HTTPBIN_BASE}/get"
    params = {"course": "sparktech", "day": 12}

    print(f"请求: GET {url}")
    print(f"查询参数 params: {params}")

    response = requests.get(url, params=params, timeout=TIMEOUT)

    print(f"状态码: {response.status_code} {response.reason}")
    print(f"响应 Content-Type: {response.headers.get('Content-Type')}")

    data: dict[str, Any] = response.json()
    print("响应体（节选）:")
    print(json.dumps({"args": data.get("args"), "url": data.get("url")}, ensure_ascii=False, indent=2))


def demo_post_json() -> None:
    """POST + JSON body：LLM API 同款写法。"""
    print_section("2. POST 请求（JSON body）")
    url = f"{HTTPBIN_BASE}/post"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SparkTech-Day12/1.0",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "你好，星火智服！"}],
    }

    print(f"请求: POST {url}")
    print(f"请求头 headers: {json.dumps(headers, ensure_ascii=False)}")
    print(f"请求体 body: {json.dumps(payload, ensure_ascii=False, indent=2)}")

    response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)

    print(f"状态码: {response.status_code} {response.reason}")

    data = response.json()
    echoed = data.get("json", {})
    print("服务端回显的 json 字段:")
    print(json.dumps(echoed, ensure_ascii=False, indent=2))


def demo_status_codes() -> None:
    """演示常见 HTTP 状态码。"""
    print_section("3. 状态码速览")

    cases = [
        ("200 OK", f"{HTTPBIN_BASE}/status/200"),
        ("404 Not Found", f"{HTTPBIN_BASE}/status/404"),
        ("500 Server Error", f"{HTTPBIN_BASE}/status/500"),
    ]

    for label, url in cases:
        response = requests.get(url, timeout=TIMEOUT)
        ok = response.ok  # 2xx 为 True
        print(f"  {label:20s} → status_code={response.status_code}, response.ok={ok}")


def demo_headers() -> None:
    """演示自定义请求头如何被服务端接收。"""
    print_section("4. 请求头与响应头")

    url = f"{HTTPBIN_BASE}/headers"
    headers = {
        "Authorization": "Bearer sk-****（课堂示例，非真实 Key）",
        "X-SparkTech-Project": "星火智服",
    }

    response = requests.get(url, headers=headers, timeout=TIMEOUT)
    print(f"状态码: {response.status_code}")

    received = response.json().get("headers", {})
    for key in ("Authorization", "X-SparkTech-Project", "Host"):
        print(f"  服务端看到的 {key}: {received.get(key, '(无)')}")

    print(f"  响应 Server 头: {response.headers.get('Server', '(无)')}")


def main() -> None:
    print("Day 12 · HTTP 基础演示（httpbin.org）")
    print("讲师提示：下午 LLM API 调用与 POST JSON 结构完全一致，只是 URL 和鉴权不同。")

    demo_get()
    demo_post_json()
    demo_status_codes()
    demo_headers()

    print_section("小结")
    print("  GET    → 取资源，参数在 URL")
    print("  POST   → 提交数据，LLM API 用 JSON body")
    print("  状态码 → 2xx 成功，4xx 客户端错，5xx 服务端错")
    print("  headers → Authorization 携带 API Key")
    print("  body   → messages 列表是星火智服对话的核心结构")


if __name__ == "__main__":
    main()
