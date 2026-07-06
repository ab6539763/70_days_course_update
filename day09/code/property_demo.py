#!/usr/bin/env python3
"""
Day 9 下午配套 · @property 与魔术方法深入演示

运行：python3 property_demo.py
"""

from __future__ import annotations

from dataclasses import dataclass

from base_model import BaseModel, GenerationResult
from openai_model import OpenAIModel
from qwen_model import QwenModel


# ---------------------------------------------------------------------------
# 1. @property 基础：计算属性 vs 存储属性
# ---------------------------------------------------------------------------

@dataclass
class Rectangle:
  width: float
  height: float

  @property
  def area(self) -> float:
    """面积由宽高推导，不应允许外部直接赋值 area。"""
    return self.width * self.height

  @property
  def perimeter(self) -> float:
    return 2 * (self.width + self.height)


def demo_property_basics() -> None:
  print("=" * 60)
  print("【1】@property：只读计算属性")
  print("=" * 60)
  rect = Rectangle(3, 4)
  print(f"  宽={rect.width}, 高={rect.height}")
  print(f"  area={rect.area}, perimeter={rect.perimeter}")
  # rect.area = 100  # AttributeError: property 'area' has no setter


# ---------------------------------------------------------------------------
# 2. getter / setter：带校验的可写属性
# ---------------------------------------------------------------------------

class TemperatureModel(BaseModel):
  """演示 temperature 的 setter 校验（逻辑在 BaseModel 中）。"""

  vendor = "demo"

  def generate(self, prompt: str, **kwargs) -> GenerationResult:
    prompt = super()._before_generate(prompt)
    return GenerationResult(
      text=f"[temp={self.temperature}] {prompt}",
      model=self.model_name,
      vendor=self.vendor,
    )


def demo_property_setter() -> None:
  print("\n" + "=" * 60)
  print("【2】@property setter：赋值时校验")
  print("=" * 60)
  m = TemperatureModel("demo-1", temperature=0.7)
  print(f"  初始 temperature = {m.temperature}")
  m.temperature = 1.2
  print(f"  修改为 1.2 → OK: {m.temperature}")
  try:
    m.temperature = 3.0
  except ValueError as e:
    print(f"  修改为 3.0 → ValueError: {e}")


# ---------------------------------------------------------------------------
# 3. __str__ vs __repr__
# ---------------------------------------------------------------------------

def demo_str_vs_repr() -> None:
  print("\n" + "=" * 60)
  print("【3】__str__ vs __repr__")
  print("=" * 60)
  models = [
    OpenAIModel("gpt-4o", api_key="sk-xxx"),
    QwenModel("qwen-max", api_key=""),
  ]
  print("  规则：str 给人看，repr 给调试器看（最好能 eval 重建对象）")
  for m in models:
    print(f"\n  type: {type(m).__name__}")
    print(f"    print(m) → {m}")
    print(f"    repr(m)  → {repr(m)}")
  print("\n  list 打印时默认用 repr:")
  print(f"    {models!r}")


# ---------------------------------------------------------------------------
# 4. __call__：实例当函数用
# ---------------------------------------------------------------------------

def demo_call() -> None:
  print("\n" + "=" * 60)
  print("【4】__call__：model('prompt') 等价 generate")
  print("=" * 60)
  model = OpenAIModel("gpt-4o-mini")
  print(f"  callable(model) = {callable(model)}")
  r1 = model.generate("什么是 RAG？")
  r2 = model("什么是 RAG？")
  print(f"  generate 与 __call__ 文本一致: {r1.text == r2.text}")
  print(f"  call_count = {model.call_count}")


# ---------------------------------------------------------------------------
# 5. 只读 @property：统计与派生状态
# ---------------------------------------------------------------------------

def demo_readonly_stats() -> None:
  print("\n" + "=" * 60)
  print("【5】只读 property：call_count / is_configured")
  print("=" * 60)
  m = QwenModel("qwen-plus")
  print(f"  is_configured: {m.is_configured}")
  m("第一次")
  m("第二次")
  print(f"  call_count: {m.call_count}")
  # m.call_count = 0  # AttributeError


# ---------------------------------------------------------------------------
# 6. @property 与私有化约定 _field
# ---------------------------------------------------------------------------

class ConfigHolder:
  def __init__(self) -> None:
    self._api_key = ""

  @property
  def api_key_masked(self) -> str:
    if not self._api_key:
      return "(未设置)"
    return self._api_key[:4] + "****" + self._api_key[-4:]

  @api_key_masked.setter
  def api_key_masked(self, value: str) -> None:
    cleaned = value.strip()
    if cleaned and len(cleaned) < 8:
      raise ValueError("API Key 过短")
    self._api_key = cleaned


def demo_masked_secret() -> None:
  print("\n" + "=" * 60)
  print("【6】业务场景：API Key 脱敏展示")
  print("=" * 60)
  cfg = ConfigHolder()
  print(f"  空 Key: {cfg.api_key_masked}")
  cfg.api_key_masked = "sk-proj-abcdefghijklmnop"
  print(f"  设置后: {cfg.api_key_masked}")


def main() -> None:
  print("Day 9 · @property 与魔术方法演示\n")
  demo_property_basics()
  demo_property_setter()
  demo_str_vs_repr()
  demo_call()
  demo_readonly_stats()
  demo_masked_secret()
  print("\n✅ property_demo.py 运行完成")


if __name__ == "__main__":
  main()
