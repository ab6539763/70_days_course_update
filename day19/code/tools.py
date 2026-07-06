# -*- coding: utf-8 -*-
"""
Day 19 · 工具实现层

提供三类工具的真实（mock）实现：
- get_weather：天气查询
- calculate：安全数学计算
- query_products：本地 JSON 产品库检索
"""

from __future__ import annotations

import ast
import json
import operator
import re
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent / "data"
PRODUCTS_FILE = DATA_DIR / "mock_products.json"

# 确定性 mock 天气库（无外部 API）
MOCK_WEATHER: dict[str, dict[str, Any]] = {
    "北京": {"temp_c": 28, "humidity": 45, "condition": "晴"},
    "上海": {"temp_c": 32, "humidity": 72, "condition": "多云"},
    "深圳": {"temp_c": 30, "humidity": 80, "condition": "阵雨"},
    "杭州": {"temp_c": 29, "humidity": 65, "condition": "阴"},
    "成都": {"temp_c": 26, "humidity": 78, "condition": "小雨"},
}

# 安全数学运算：仅允许字面量与四则运算
_SAFE_OPS: dict[type, Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


class ToolError(ValueError):
    """工具执行业务错误。"""


def _celsius_to_fahrenheit(c: float) -> float:
    return round(c * 9 / 5 + 32, 1)


def get_weather(city: str, unit: str = "celsius") -> dict[str, Any]:
    """查询城市天气（mock 数据源）。"""
    city = city.strip()
    if not city:
        raise ToolError("city 不能为空")

    # 模糊匹配：去掉「市」后缀
    key = city.rstrip("市")
    record = MOCK_WEATHER.get(key) or MOCK_WEATHER.get(city)
    if record is None:
        # 未知城市：用哈希生成确定性伪数据
        seed = sum(ord(c) for c in city) % 20
        record = {
            "temp_c": 20 + seed,
            "humidity": 40 + seed,
            "condition": "晴",
        }

    temp_c = record["temp_c"]
    if unit == "fahrenheit":
        temp = _celsius_to_fahrenheit(temp_c)
        temp_unit = "°F"
    else:
        temp = temp_c
        temp_unit = "°C"

    return {
        "city": city,
        "temperature": temp,
        "unit": temp_unit,
        "humidity_percent": record["humidity"],
        "condition": record["condition"],
        "source": "mock_weather_db",
    }


def _safe_eval(node: ast.AST) -> float:
    """仅评估安全数学 AST 节点。"""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Num):  # Python 3.8 兼容
        return float(node.n)  # type: ignore[attr-defined]
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        left = _safe_eval(node.left)
        right = _safe_eval(node.right)
        if isinstance(node.op, (ast.Div, ast.FloorDiv)) and right == 0:
            raise ToolError("除数不能为零")
        return _SAFE_OPS[type(node.op)](left, right)
    raise ToolError(f"不支持的表达式节点: {type(node).__name__}")


def calculate(expression: str) -> dict[str, Any]:
    """安全计算数学表达式。"""
    expression = expression.strip()
    if not expression:
        raise ToolError("expression 不能为空")

    # 拒绝字母与危险符号
    if re.search(r"[a-zA-Z_]", expression):
        raise ToolError("表达式仅允许数字与运算符")

    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
    except SyntaxError as exc:
        raise ToolError(f"表达式语法错误: {exc}") from exc

    # 整数结果去掉 .0
    if result == int(result):
        display = str(int(result))
    else:
        display = str(round(result, 6))

    return {
        "expression": expression,
        "result": display,
        "numeric": result,
    }


def _load_products() -> list[dict[str, Any]]:
    with PRODUCTS_FILE.open(encoding="utf-8") as fh:
        return json.load(fh)


def query_products(
    keyword: str,
    category: str = "all",
    limit: int = 5,
) -> dict[str, Any]:
    """从本地 JSON 产品库检索。"""
    keyword = keyword.strip().lower()
    if not keyword:
        raise ToolError("keyword 不能为空")

    limit = max(1, min(int(limit), 10))
    products = _load_products()
    matched: list[dict[str, Any]] = []

    for item in products:
        if category != "all" and item.get("category") != category:
            continue
        haystack = f"{item['name']} {item['description']}".lower()
        if keyword in haystack or any(k in haystack for k in keyword.split()):
            matched.append(item)
        if len(matched) >= limit:
            break

    return {
        "keyword": keyword,
        "category": category,
        "count": len(matched),
        "products": matched,
        "source": str(PRODUCTS_FILE.name),
    }


# 工具名 → Python 可调用对象
TOOL_REGISTRY: dict[str, Any] = {
    "get_weather": get_weather,
    "calculate": calculate,
    "query_products": query_products,
}


def list_tool_names() -> list[str]:
    return list(TOOL_REGISTRY.keys())


def main() -> None:
    print("=" * 60)
    print("Day 19 · tools.py 演示")
    print("=" * 60)

    print("\n[1] get_weather('北京')")
    print(json.dumps(get_weather("北京"), ensure_ascii=False, indent=2))

    print("\n[2] calculate('(12 + 8) * 3')")
    print(json.dumps(calculate("(12 + 8) * 3"), ensure_ascii=False, indent=2))

    print("\n[3] query_products('工单')")
    print(json.dumps(query_products("工单"), ensure_ascii=False, indent=2))

    print("\n✅ tools.py 完成")


if __name__ == "__main__":
    main()
