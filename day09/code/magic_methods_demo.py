#!/usr/bin/env python3
"""
Day 9 上午配套 · 继承、多态、super() 演示

运行：python3 magic_methods_demo.py
（文件名历史原因保留 magic_methods；本文件侧重继承多态，魔术方法见 property_demo 与 base_model）
"""

from __future__ import annotations

from base_model import BaseModel
from openai_model import OpenAIModel
from qwen_model import QwenModel


# ---------------------------------------------------------------------------
# 1. 最小继承示例（课堂白板）
# ---------------------------------------------------------------------------

class Animal:
  vendor = "nature"

  def speak(self) -> str:
    return "..."


class Dog(Animal):
  def speak(self) -> str:
    return "汪汪"


class Cat(Animal):
  def speak(self) -> str:
    return "喵喵"


def demo_animal_polymorphism() -> None:
  print("=" * 60)
  print("【1】多态：同一接口 speak()，不同子类不同行为")
  print("=" * 60)
  animals: list[Animal] = [Dog(), Cat(), Dog()]
  for a in animals:
    print(f"  {type(a).__name__:8} → {a.speak()}")


# ---------------------------------------------------------------------------
# 2. super() 与方法重写
# ---------------------------------------------------------------------------

class LoggingMixin:
  """演示 Mixin：非 LLM 业务，仅说明 super() 链。"""

  def log(self, msg: str) -> None:
    print(f"  [LOG] {msg}")


class VerboseOpenAI(OpenAIModel, LoggingMixin):
  def generate(self, prompt: str, **kwargs):
    self.log(f"OpenAI 开始生成，prompt 长度={len(prompt)}")
    result = super().generate(prompt, **kwargs)
    self.log(f"完成，completion_tokens≈{result.completion_tokens}")
    return result


def demo_super_and_override() -> None:
  print("\n" + "=" * 60)
  print("【2】方法重写 + super()：VerboseOpenAI 扩展 generate")
  print("=" * 60)
  model = VerboseOpenAI(model_name="gpt-4o-mini", api_key="sk-mock")
  print(f"  实例类型: {type(model).__mro__}")
  result = model.generate("星火智服工单摘要怎么写？")
  print(f"  回复: {result.text[:80]}…")


# ---------------------------------------------------------------------------
# 3. 多态：统一列表调度不同厂商
# ---------------------------------------------------------------------------

def route_prompt(models: list[BaseModel], prompt: str) -> None:
  """
  业务层只依赖 BaseModel 类型 —— 不必知道背后是 OpenAI 还是 Qwen。

  这就是张工要求的「统一接口」。
  """
  print(f"\n  用户问题: {prompt}")
  for m in models:
    # 多态：运行时根据实际类型调用对应 generate
    out = m.generate(prompt)
    print(f"  → {m.vendor:6} | {out.text[:70]}…")


def demo_llm_polymorphism() -> None:
  print("\n" + "=" * 60)
  print("【3】LLM 多态：list[BaseModel] 统一路由")
  print("=" * 60)
  registry: list[BaseModel] = [
    OpenAIModel("gpt-4o", api_key="sk-openai-mock"),
    QwenModel("qwen-plus", api_key="sk-qwen-mock"),
    OpenAIModel("gpt-4o-mini"),
  ]
  route_prompt(registry, "客户投诉回复模板")


# ---------------------------------------------------------------------------
# 4. isinstance 与类型检查
# ---------------------------------------------------------------------------

def demo_isinstance() -> None:
  print("\n" + "=" * 60)
  print("【4】isinstance：按能力分支")
  print("=" * 60)
  models: list[BaseModel] = [OpenAIModel(), QwenModel()]
  for m in models:
    label = type(m).__name__
    if isinstance(m, QwenModel):
      print(f"  {label}: 可走 generate_with_search 扩展")
      print(f"    {m.generate_with_search('最新资费')}")
    elif isinstance(m, OpenAIModel):
      print(f"  {label}: 标准 generate")
      print(f"    {m('Hello')}")


# ---------------------------------------------------------------------------
# 5. __str__ / __repr__ / __call__ 速览
# ---------------------------------------------------------------------------

def demo_magic_methods_preview() -> None:
  print("\n" + "=" * 60)
  print("【5】魔术方法速览（详细见 property_demo.py）")
  print("=" * 60)
  m = QwenModel("qwen-turbo", temperature=0.5)
  print(f"  str(m)  = {m}")       # __str__
  print(f"  repr(m) = {repr(m)}")  # __repr__
  print(f"  m('你好') = {m('你好')}")  # __call__ → generate


def main() -> None:
  print("Day 9 · 继承与多态演示\n")
  demo_animal_polymorphism()
  demo_super_and_override()
  demo_llm_polymorphism()
  demo_isinstance()
  demo_magic_methods_preview()
  print("\n✅ magic_methods_demo.py 运行完成")


if __name__ == "__main__":
  main()
