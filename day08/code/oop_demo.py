# -*- coding: utf-8 -*-
"""Day 8 入门演示：类、对象、属性、方法与 __init__。

运行：python3 oop_demo.py

教学目标：
  - 理解 class 是模板，object 是实例
  - 掌握 __init__ 构造与 self 含义
  - 区分属性访问与方法调用

业务旁白：张工说「先把 OOP 语法学稳，再重构通讯录」——本文件用
Employee / Dog 两个极简类打基础，与星火业务无强耦合，降低认知负荷。
"""

from __future__ import annotations


class Employee:
    """员工类 —— 模拟星火科技培训生档案（教学用）。"""

    def __init__(self, emp_id: str, name: str, department: str, years: int = 0) -> None:
        """构造方法：创建员工对象时自动调用。

        Args:
            emp_id: 工号，如 ST20260708
            name: 姓名，strip 后非空
            department: 部门名称
            years: 工龄，默认 0
        """
        # self 代表「当前正在创建的这个员工对象」
        self.emp_id = emp_id.strip()
        self.name = name.strip()
        self.department = department.strip() or "未分配"
        self.years = years

        if not self.name:
            raise ValueError("员工姓名不能为空。")

    def introduce(self) -> str:
        """实例方法：需要读取 self 上的属性，必须用实例调用。"""
        senior = "资深" if self.is_senior() else "新人"
        return f"【{senior}】{self.name}（{self.emp_id}）· {self.department} · 工龄 {self.years} 年"

    def is_senior(self) -> bool:
        """实例方法：工龄 >= 3 视为资深（业务规则可日后配置化）。"""
        return self.years >= 3

    def __str__(self) -> str:
        """定义 print(employee) 时的人类可读格式。"""
        return f"Employee({self.emp_id}, {self.name}, {self.department})"


class Dog:
    """狗类 —— 经典 OOP 教具，帮助理解「同一类，不同实例」。"""

    def __init__(self, name: str, breed: str) -> None:
        self.name = name.strip()
        self.breed = breed.strip()

    def bark(self) -> str:
        return f"{self.name}（{self.breed}）: 汪汪！"


def demo_employee() -> None:
    """演示：构造两个 Employee，证明是不同对象。"""
    print("=" * 56)
    print("  演示 1 · Employee 类")
    print("=" * 56)

    alice = Employee("ST001", "陈晓", "大模型应用开发部", years=5)
    bob = Employee("ST002", "李雷", "信息技术部", years=1)

    print(alice.introduce())
    print(bob.introduce())
    print(f"alice 与 bob 是同一对象吗？ {alice is bob}")  # False
    print(f"alice 的 id: {id(alice)}")
    print(f"bob 的 id:   {id(bob)}")


def demo_dog() -> None:
    """演示：同一 Dog 类，不同实例，行为依赖各自 name。"""
    print("\n" + "=" * 56)
    print("  演示 2 · Dog 类")
    print("=" * 56)

    wangcai = Dog("旺财", "柴犬")
    laifu = Dog("来福", "金毛")
    print(wangcai.bark())
    print(laifu.bark())


def demo_validation() -> None:
    """演示：非法数据在 __init__ 阶段被拒绝，对象不会被创建。"""
    print("\n" + "=" * 56)
    print("  演示 3 · 构造期校验")
    print("=" * 56)

    try:
        Employee("ST999", "   ", "产品部")
    except ValueError as exc:
        print(f"捕获预期错误: {exc}")


def main() -> None:
    print("\n星火科技 Day 8 · OOP 入门 oop_demo.py")
    print("张工：「类是图纸，对象是根据图纸造出来的实物。」\n")
    demo_employee()
    demo_dog()
    demo_validation()
    print("\n小结：")
    print("  1. class 定义模板；变量 = ClassName(...) 得到对象")
    print("  2. __init__(self, ...) 初始化属性；self.xxx = 值")
    print("  3. 实例方法第一个参数是 self，调用时 Python 自动传入对象")
    print("  4. 下一步 → contact_class.py 把 Day 7 联系人 dict 升级为 Contact 类")


if __name__ == "__main__":
    main()
