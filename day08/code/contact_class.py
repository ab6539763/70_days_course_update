# -*- coding: utf-8 -*-
"""Day 8 演示：Contact 类 —— 重构 Day 7 通讯录单条记录。

运行：python3 contact_class.py

将 Day 7 address_book.py 中的 dict 记录与校验逻辑封装为 Contact 类：
  - __init__ 构造并校验 name / phone
  - 实例方法 update / __str__ / to_dict
  - @classmethod from_dict 兼容 day07/contacts.json
  - @staticmethod normalize_phone 复用手机号清洗

Day 14 扩展：命令行助手可通过 /contact 子命令查询 ContactBook。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

# 与 Day 7 address_book.py 保持一致的部门白名单
VALID_DEPARTMENTS: tuple[str, ...] = (
    "大模型应用开发部",
    "信息技术部",
    "人力资源部",
    "产品部",
    "未分配",
)

# 默认尝试读取 Day 7 示例数据（路径不存在时 demo 使用内置样例）
DAY07_CONTACTS_JSON = (
    Path(__file__).resolve().parents[2] / "day07" / "code" / "contacts.json"
)


class Contact:
    """联系人 —— 对应 Day 7 单条 dict 记录的面向对象版本。"""

    def __init__(
        self,
        contact_id: int,
        name: str,
        phone: str,
        email: str = "",
        department: str = "未分配",
        notes: str = "",
        created_at: str | None = None,
        updated_at: str | None = None,
    ) -> None:
        """构造联系人；校验失败则抛出 ValueError，对象不会半初始化暴露出去。"""
        self.id = contact_id
        self.name = self._validate_name(name)
        self.phone = self._validate_phone(phone)
        self.email = self._normalize_email(email)
        self.department = self._resolve_department(department)
        self.notes = self._strip(notes)

        now = datetime.now(timezone.utc).isoformat()
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    # ----- 校验与清洗（Day 7 函数内聚到类内） -----

    @staticmethod
    def _strip(text: str) -> str:
        """去除首尾空白。"""
        return text.strip() if text else ""

    @staticmethod
    def normalize_phone(raw: str) -> str:
        """静态方法：手机号规范化 —— 提取数字，不依赖具体联系人实例。

        Day 7 同名逻辑：去空白后只保留数字字符。
        """
        cleaned = "".join(raw.split())
        return "".join(ch for ch in cleaned if ch.isdigit())

    @staticmethod
    def _normalize_email(raw: str) -> str:
        return Contact._strip(raw).lower()

    def _validate_name(self, name: str) -> str:
        name = self._strip(name)
        if not name:
            raise ValueError("姓名不能为空。")
        return name

    def _validate_phone(self, phone: str) -> str:
        phone = self.normalize_phone(phone)
        if len(phone) < 7:
            raise ValueError("手机号至少需要 7 位数字。")
        return phone

    def _resolve_department(self, raw: str) -> str:
        dept = self._strip(raw) or "未分配"
        if dept not in VALID_DEPARTMENTS:
            return "未分配"
        return dept

    # ----- 实例方法：操作「当前这条联系人」 -----

    def update(
        self,
        *,
        name: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        department: str | None = None,
        notes: str | None = None,
    ) -> None:
        """按字段更新当前联系人；仅传入非 None 的字段会被修改。"""
        if name is not None:
            self.name = self._validate_name(name)
        if phone is not None:
            self.phone = self._validate_phone(phone)
        if email is not None:
            self.email = self._normalize_email(email)
        if department is not None:
            self.department = self._resolve_department(department)
        if notes is not None:
            self.notes = self._strip(notes)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        """序列化为 Day 7 兼容的 dict，便于 json.dump 落盘。"""
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "department": self.department,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def __str__(self) -> str:
        """对齐 Day 7 format_contact 的展示风格。"""
        email = self.email or "-"
        notes = self.notes or "-"
        return (
            f"[#{self.id}] {self.name} | {self.phone} | "
            f"{self.department} | {email} | 备注: {notes}"
        )

    # ----- 类方法：工厂，从外部 dict 构造对象 -----

    @classmethod
    def from_dict(cls, data: dict) -> Contact:
        """类方法：从 Day 7 JSON 单条记录创建 Contact 实例。

        使用 cls(...) 而非 Contact(...)，便于日后子类继承时工厂返回子类实例。
        """
        return cls(
            contact_id=int(data.get("id", 0)),
            name=str(data.get("name", "")),
            phone=str(data.get("phone", "")),
            email=str(data.get("email", "")),
            department=str(data.get("department", "未分配")),
            notes=str(data.get("notes", "")),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class ContactBook:
    """通讯录容器 —— 管理 list[Contact]，对应 Day 7 的 contacts + next_id。"""

    def __init__(self, contacts: list[Contact] | None = None, next_id: int = 1) -> None:
        self._contacts: list[Contact] = list(contacts or [])
        self._next_id = next_id

    def add(
        self,
        name: str,
        phone: str,
        email: str = "",
        department: str = "未分配",
        notes: str = "",
    ) -> Contact:
        """添加联系人：内部构造 Contact 并 append。"""
        # 简单去重：同手机号不允许添加
        norm = Contact.normalize_phone(phone)
        for c in self._contacts:
            if c.phone == norm:
                raise ValueError(f"手机号 {norm} 已存在（#{c.id} {c.name}）。")

        contact = Contact(self._next_id, name, phone, email, department, notes)
        self._contacts.append(contact)
        self._next_id += 1
        return contact

    def find_by_id(self, contact_id: int) -> Contact | None:
        for c in self._contacts:
            if c.id == contact_id:
                return c
        return None

    def search(self, keyword: str) -> list[Contact]:
        """关键词子串搜索（姓名/手机/部门/邮箱/备注）。"""
        kw = self._strip_keyword(keyword)
        if not kw:
            return list(self._contacts)
        results = []
        for c in self._contacts:
            haystack = " ".join(
                [c.name, c.phone, c.email, c.department, c.notes]
            ).lower()
            if kw in haystack:
                results.append(c)
        return sorted(results, key=lambda x: x.id)

    @staticmethod
    def _strip_keyword(keyword: str) -> str:
        return keyword.strip().lower()

    def to_contacts_payload(self) -> dict:
        """生成与 Day 7 contacts.json 顶层兼容的字典。"""
        return {
            "version": "1.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "next_id": self._next_id,
            "contacts": [c.to_dict() for c in self._contacts],
        }

    @classmethod
    def from_contacts_payload(cls, payload: dict) -> ContactBook:
        """从 Day 7 JSON 顶层结构加载 ContactBook。"""
        contacts = [Contact.from_dict(item) for item in payload.get("contacts", [])]
        next_id = int(payload.get("next_id", 1))
        return cls(contacts=contacts, next_id=next_id)

    def __len__(self) -> int:
        return len(self._contacts)


def _load_day07_sample() -> ContactBook:
    """尝试加载 Day 7 示例 JSON；失败则返回内置演示数据。"""
    if DAY07_CONTACTS_JSON.is_file():
        with DAY07_CONTACTS_JSON.open(encoding="utf-8") as f:
            payload = json.load(f)
        book = ContactBook.from_contacts_payload(payload)
        print(f"已从 Day 7 加载: {DAY07_CONTACTS_JSON}")
        return book

    print(f"提示：未找到 {DAY07_CONTACTS_JSON}，使用内置样例。")
    book = ContactBook()
    book.add("陈晓", "13800138001", email="chen.xiao@sparktech.cn", department="大模型应用开发部")
    book.add("李雷", "13800138002", department="信息技术部")
    return book


def main() -> None:
    print("\n星火科技 Day 8 · Contact 类重构 contact_class.py")
    print("张工：「Day 7 的 dict 记录，今天变成有行为的对象。」\n")

    book = _load_day07_sample()
    print(f"通讯录共 {len(book)} 条联系人。\n")

    # 展示第一条（from_dict 互操作）
    if len(book) > 0:
        first = book._contacts[0]
        print("--- 第一条联系人 ---")
        print(first)
        print("\n--- to_dict 键名与 Day 7 一致 ---")
        print(list(first.to_dict().keys()))

    # 演示 update 实例方法
    c = book.find_by_id(1)
    if c:
        c.update(department="产品部")
        print("\n--- update 后 ---")
        print(c)

    # 演示 staticmethod：无需实例即可清洗手机号
    print("\n--- normalize_phone（静态方法）---")
    print(Contact.normalize_phone("138 0013 8001"))

    # 演示搜索
    print("\n--- search('陈') ---")
    for item in book.search("陈"):
        print(item)

    print("\n小结：Contact 封装字段+校验；ContactBook 封装 list 容器；Day 14 可 import 查询 HR 数据。")


if __name__ == "__main__":
    main()
