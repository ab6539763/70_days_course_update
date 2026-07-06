# -*- coding: utf-8 -*-
"""Day 8 演示：实例方法、类方法、静态方法对照实验。

运行：python3 classmethod_demo.py

通过 Temperature 与 DateRange 两个教学类，对比：
  - 实例方法：依赖 self，读写当前对象状态
  - @classmethod：依赖 cls，常用作工厂方法
  - @staticmethod：无 self/cls，纯工具函数归属类命名空间

业务联系：Contact.from_dict 是 classmethod；Contact.normalize_phone 是 staticmethod。
"""

from __future__ import annotations


class Temperature:
    """温度类 —— 演示三种方法在同一业务概念下的分工。"""

    def __init__(self, celsius: float) -> None:
        if not Temperature.is_valid_value(celsius):
            raise ValueError(f"温度值非法: {celsius}")
        self.celsius = celsius

    # ----- 实例方法 -----

    def to_fahrenheit(self) -> float:
        """实例方法：把「当前对象」的摄氏温度转为华氏。"""
        return self.celsius * 9 / 5 + 32

    def describe(self) -> str:
        return f"{self.celsius}°C = {self.to_fahrenheit():.1f}°F"

    # ----- 类方法：工厂 -----

    @classmethod
    def from_fahrenheit(cls, fahrenheit: float) -> Temperature:
        """类方法：从华氏温度「生产」一个 Temperature 对象。

        调用方还没有实例，所以用 cls(...) 而不是 self。
        """
        celsius = (fahrenheit - 32) * 5 / 9
        return cls(celsius)

    @classmethod
    def boiling_point(cls) -> Temperature:
        """类方法：返回标准大气压下水的沸点对象。"""
        return cls(100.0)

    # ----- 静态方法：与实例/类状态无关的工具 -----

    @staticmethod
    def is_valid_value(value: float) -> bool:
        """静态方法：绝对零度以上（教学简化，单位摄氏度）。"""
        return value >= -273.15

    @staticmethod
    def average(a: "Temperature", b: "Temperature") -> float:
        """静态方法：计算两个温度对象的摄氏均值（不修改原对象）。"""
        return (a.celsius + b.celsius) / 2


class DateRange:
    """日期范围字符串解析 —— 演示 classmethod 解析多种输入格式。"""

    def __init__(self, start: str, end: str) -> None:
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f"{self.start} ~ {self.end}"

    @classmethod
    def from_text(cls, text: str) -> DateRange:
        """类方法：解析 '2026-07-01/2026-07-08' 形式文本。"""
        parts = [p.strip() for p in text.split("/", 1)]
        if len(parts) != 2 or not all(parts):
            raise ValueError("日期范围格式应为 start/end")
        return cls(parts[0], parts[1])

    @staticmethod
    def is_iso_date(text: str) -> bool:
        """静态方法：极简 ISO 日期格式检查（YYYY-MM-DD）。"""
        text = text.strip()
        if len(text) != 10 or text[4] != "-" or text[7] != "-":
            return False
        y, m, d = text.split("-")
        return y.isdigit() and m.isdigit() and d.isdigit()


def demo_temperature() -> None:
    print("=" * 56)
    print("  演示 1 · Temperature：三种方法")
    print("=" * 56)

    # 实例方法：需要先有对象
    room = Temperature(25.0)
    print(room.describe())

    # 类方法：无需先有对象，从华氏工厂生产
    body = Temperature.from_fahrenheit(98.6)
    print(f"体温（由华氏工厂生产）: {body.describe()}")

    boil = Temperature.boiling_point()
    print(f"沸水（类方法常量）: {boil.describe()}")

    # 静态方法：不访问 self/cls，可当工具函数
    print(f"25°C 合法? {Temperature.is_valid_value(25)}")
    print(f"-300°C 合法? {Temperature.is_valid_value(-300)}")
    print(f"25°C 与 30°C 均值: {Temperature.average(room, Temperature(30)):.1f}°C")


def demo_date_range() -> None:
    print("\n" + "=" * 56)
    print("  演示 2 · DateRange：classmethod 解析")
    print("=" * 56)

    dr = DateRange.from_text("2026-07-01/2026-07-08")
    print(dr)
    print(f"start 是 ISO? {DateRange.is_iso_date(dr.start)}")


def demo_contact_analogy() -> None:
    """用注释对照今日业务类，帮助记忆。"""
    print("\n" + "=" * 56)
    print("  演示 3 · 与 Contact / ChatMessage 对照")
    print("=" * 56)
    print("  实例方法  →  Contact.update()      改当前联系人")
    print("  类方法    →  Contact.from_dict()   从 JSON 造对象")
    print("  静态方法  →  Contact.normalize_phone()  清洗手机号")
    print("  类方法    →  ChatMessage.from_dict()")
    print("  静态方法  →  ChatMessage.preview()")


def main() -> None:
    print("\n星火科技 Day 8 · 三种方法 classmethod_demo.py")
    print("张工：「别把所有函数都贴成 staticmethod —— 按是否访问 self 来选。」\n")
    demo_temperature()
    demo_date_range()
    demo_contact_analogy()
    print("\n小结：实例改自己；classmethod 造对象；staticmethod 当工具。")


if __name__ == "__main__":
    main()
