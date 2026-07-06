# -*- coding: utf-8 -*-
"""Day 7 主程序：命令行通讯录（Week 1 综合实战）。

运行：python3 address_book.py

功能：add / delete / update / search / list / save / load
数据：contacts 为 list[dict]，持久化到 contacts.json（Day 5 JSON）

Week 1 技能串联：
  Day 1  变量与 f-string 展示
  Day 2  字符串 strip、手机号去空格
  Day 3  while 主循环与菜单路由
  Day 4  list CRUD 与线性查找
  Day 5  dict 记录 + json.load/dump
  Day 6  函数拆分（明日 Day 8 将进入 OOP 重构）

业务背景：HR 刘姐需要培训生交付内部通讯录原型，供入职季联系人维护。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量与路径（Day 1 常量思维 + pathlib）
# ---------------------------------------------------------------------------

DEFAULT_DATA_FILE = Path(__file__).resolve().parent / "contacts.json"
JSON_VERSION = "1.0"
VALID_DEPARTMENTS: tuple[str, ...] = (
    "大模型应用开发部",
    "信息技术部",
    "人力资源部",
    "产品部",
    "未分配",
)


# ---------------------------------------------------------------------------
# 字符串清洗（Day 2 思想内联，避免跨日 import 增加环境依赖）
# ---------------------------------------------------------------------------


def strip_field(text: str) -> str:
    """去除首尾空白；空串返回空字符串。"""
    return text.strip() if text else ""


def normalize_phone(raw: str) -> str:
    """手机号：去全部空白，保留数字与常见分隔符清洗后的纯数字串。"""
    cleaned = "".join(raw.split())
    digits = "".join(ch for ch in cleaned if ch.isdigit())
    return digits


def normalize_email(raw: str) -> str:
    """邮箱：strip 并转小写，便于搜索比对。"""
    return strip_field(raw).lower()


# ---------------------------------------------------------------------------
# 持久化：JSON 读写（Day 5）
# ---------------------------------------------------------------------------


def load_contacts(path: Path | str = DEFAULT_DATA_FILE) -> tuple[list[dict], int]:
    """从 JSON 文件加载通讯录。

    返回 (contacts 列表, next_id)。
    文件不存在或为空时返回 ([], 1)。
  """
    file_path = Path(path)
    if not file_path.is_file():
        return [], 1

    try:
        with file_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"错误：JSON 解析失败 — {exc}")
        print("请检查文件格式或删除损坏文件后重试。")
        return [], 1
    except OSError as exc:
        print(f"错误：无法读取 {file_path} — {exc}")
        return [], 1

    contacts = payload.get("contacts") or []
    next_id = int(payload.get("next_id") or 1)
    if not isinstance(contacts, list):
        print("警告：contacts 字段不是列表，已重置为空。")
        return [], 1
    return contacts, next_id


def save_contacts(
    contacts: list[dict],
    next_id: int,
    path: Path | str = DEFAULT_DATA_FILE,
) -> bool:
    """将通讯录写入 JSON 文件。成功返回 True。"""
    file_path = Path(path)
    payload = {
        "version": JSON_VERSION,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "next_id": next_id,
        "contacts": contacts,
    }
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return True
    except OSError as exc:
        print(f"错误：保存失败 — {exc}")
        return False


# ---------------------------------------------------------------------------
# 查找与校验（Day 4 list 遍历）
# ---------------------------------------------------------------------------


def find_index_by_id(contacts: list[dict], contact_id: int) -> int | None:
    """按 id 线性查找，返回索引；找不到返回 None。"""
    for i, item in enumerate(contacts):
        if item.get("id") == contact_id:
            return i
    return None


def validate_name(name: str) -> str:
    """姓名非空校验。"""
    name = strip_field(name)
    if not name:
        raise ValueError("姓名不能为空。")
    return name


def validate_phone(phone: str) -> str:
    """手机号：至少 7 位数字（简化学员环境，不强制 11 位）。"""
    phone = normalize_phone(phone)
    if len(phone) < 7:
        raise ValueError("手机号至少需要 7 位数字。")
    return phone


def resolve_department(raw: str) -> str:
    """部门：空则默认「未分配」；非法值回退未分配。"""
    dept = strip_field(raw) or "未分配"
    if dept not in VALID_DEPARTMENTS:
        print(f"提示：未知部门「{dept}」，已记为「未分配」。")
        return "未分配"
    return dept


# ---------------------------------------------------------------------------
# CRUD 核心（Day 4 + Day 5 dict 记录）
# ---------------------------------------------------------------------------


def add_contact(
    contacts: list[dict],
    next_id: int,
    name: str,
    phone: str,
    email: str = "",
    department: str = "未分配",
    notes: str = "",
) -> int:
    """添加联系人，append 到列表，返回更新后的 next_id。"""
    name = validate_name(name)
    phone = validate_phone(phone)
    email = normalize_email(email)
    department = resolve_department(department)
    notes = strip_field(notes)

    # 简单去重：同手机号视为重复
    for c in contacts:
        if c.get("phone") == phone:
            raise ValueError(f"手机号 {phone} 已存在（#{c.get('id')} {c.get('name')}）。")

    now = datetime.now(timezone.utc).isoformat()
    record = {
        "id": next_id,
        "name": name,
        "phone": phone,
        "email": email,
        "department": department,
        "notes": notes,
        "created_at": now,
        "updated_at": now,
    }
    contacts.append(record)
    return next_id + 1


def update_contact(
    contacts: list[dict],
    contact_id: int,
    *,
    name: str | None = None,
    phone: str | None = None,
    email: str | None = None,
    department: str | None = None,
    notes: str | None = None,
) -> bool:
    """按 id 更新字段；仅传入的非 None 字段会被修改。"""
    idx = find_index_by_id(contacts, contact_id)
    if idx is None:
        return False

    item = contacts[idx]
    if name is not None:
        item["name"] = validate_name(name)
    if phone is not None:
        new_phone = validate_phone(phone)
        for j, other in enumerate(contacts):
            if j != idx and other.get("phone") == new_phone:
                raise ValueError(f"手机号 {new_phone} 已被 #{other.get('id')} 使用。")
        item["phone"] = new_phone
    if email is not None:
        item["email"] = normalize_email(email)
    if department is not None:
        item["department"] = resolve_department(department)
    if notes is not None:
        item["notes"] = strip_field(notes)
    item["updated_at"] = datetime.now(timezone.utc).isoformat()
    return True


def delete_contact(contacts: list[dict], contact_id: int) -> bool:
    """按 id 删除联系人。"""
    idx = find_index_by_id(contacts, contact_id)
    if idx is None:
        return False
    removed = contacts.pop(idx)
    print(f"已删除 #{removed['id']}: {removed['name']} ({removed['phone']})")
    return True


def search_contacts(
    contacts: list[dict],
    keyword: str,
    field: str = "all",
) -> list[dict]:
    """按关键词搜索；field 可为 all / name / phone / department / email。"""
    keyword = strip_field(keyword).lower()
    if not keyword:
        return list(contacts)

    results: list[dict] = []
    for c in contacts:
        if field == "name" and keyword in c.get("name", "").lower():
            results.append(c)
        elif field == "phone" and keyword in c.get("phone", ""):
            results.append(c)
        elif field == "department" and keyword in c.get("department", "").lower():
            results.append(c)
        elif field == "email" and keyword in c.get("email", "").lower():
            results.append(c)
        elif field == "all":
            haystack = " ".join(
                [
                    str(c.get("name", "")),
                    str(c.get("phone", "")),
                    str(c.get("email", "")),
                    str(c.get("department", "")),
                    str(c.get("notes", "")),
                ]
            ).lower()
            if keyword in haystack:
                results.append(c)
    return sorted(results, key=lambda x: x.get("id", 0))


def list_all_contacts(contacts: list[dict], sort_by: str = "id") -> list[dict]:
    """列出全部联系人，支持按 id / name / department 排序。"""
    if sort_by == "name":
        return sorted(contacts, key=lambda x: x.get("name", ""))
    if sort_by == "department":
        return sorted(contacts, key=lambda x: (x.get("department", ""), x.get("name", "")))
    return sorted(contacts, key=lambda x: x.get("id", 0))


# ---------------------------------------------------------------------------
# 展示层（Day 1 f-string）
# ---------------------------------------------------------------------------


def format_contact(item: dict) -> str:
    """格式化单条联系人记录。"""
    email = item.get("email") or "-"
    notes = item.get("notes") or "-"
    return (
        f"[#{item['id']}] {item['name']} | {item['phone']} | "
        f"{item.get('department', '-')} | {email} | 备注: {notes}"
    )


def print_contact_table(items: list[dict]) -> None:
    """打印联系人列表。"""
    if not items:
        print("（无匹配记录）")
        return
    print("-" * 72)
    for item in items:
        print(format_contact(item))
    print("-" * 72)
    print(f"共 {len(items)} 条")


def print_stats(contacts: list[dict]) -> None:
    """按部门统计人数。"""
    counts: dict[str, int] = {}
    for c in contacts:
        dept = c.get("department") or "未分配"
        counts[dept] = counts.get(dept, 0) + 1
    print("\n部门统计：")
    for dept in sorted(counts):
        print(f"  {dept}: {counts[dept]} 人")
    print(f"总计: {len(contacts)} 人")


def print_banner() -> None:
    print("\n" + "=" * 56)
    print("  星火科技 · 内部通讯录 v1.0  |  Week 1 综合实战")
    print("  HR 联系人维护 | JSON 持久化 contacts.json")
    print("=" * 56)


def print_menu() -> None:
    print("\n1. add      添加联系人")
    print("2. list     查看全部")
    print("3. search   搜索联系人")
    print("4. update   更新联系人")
    print("5. delete   删除联系人")
    print("6. save     保存到 JSON 文件")
    print("7. reload   从文件重新加载")
    print("8. stats    部门统计")
    print("0. quit     退出（自动保存）")


# ---------------------------------------------------------------------------
# CLI 交互处理（Day 3 菜单路由）
# ---------------------------------------------------------------------------


def prompt_nonempty(prompt: str) -> str:
    """循环读取直到非空（用于必填项）。"""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("该项不能为空，请重新输入。")


def handle_add(contacts: list[dict], next_id: int) -> int:
    print("\n--- 添加联系人 ---")
    try:
        name = prompt_nonempty("姓名: ")
        phone = prompt_nonempty("手机号: ")
        email = input("邮箱（可留空）: ").strip()
        print(f"可选部门: {', '.join(VALID_DEPARTMENTS)}")
        department = input("部门 [未分配]: ").strip() or "未分配"
        notes = input("备注（可留空）: ").strip()
        next_id = add_contact(contacts, next_id, name, phone, email, department, notes)
        print(f"已添加 #{next_id - 1}: {name}")
    except ValueError as exc:
        print(f"添加失败: {exc}")
    return next_id


def handle_list(contacts: list[dict]) -> None:
    print("\n--- 联系人列表 ---")
    sort_by = input("排序 id/name/department [id]: ").strip().lower() or "id"
    if sort_by not in ("id", "name", "department"):
        sort_by = "id"
    items = list_all_contacts(contacts, sort_by=sort_by)
    print_contact_table(items)


def handle_search(contacts: list[dict]) -> None:
    print("\n--- 搜索 ---")
    keyword = input("关键词: ").strip()
    print("搜索范围: 1=全部  2=姓名  3=手机  4=部门  5=邮箱")
    mode = input("选择 [1]: ").strip() or "1"
    field_map = {"1": "all", "2": "name", "3": "phone", "4": "department", "5": "email"}
    field = field_map.get(mode, "all")
    results = search_contacts(contacts, keyword, field=field)
    print_contact_table(results)


def handle_update(contacts: list[dict]) -> None:
    print("\n--- 更新联系人 ---")
    raw = input("要更新的联系人 id: ").strip()
    if not raw.isdigit():
        print("请输入有效数字 id。")
        return
    contact_id = int(raw)
    if find_index_by_id(contacts, contact_id) is None:
        print(f"错误：找不到 id=#{contact_id}。")
        return
    print("留空表示不修改该字段。")
    try:
        name = input("新姓名: ").strip()
        phone = input("新手机号: ").strip()
        email = input("新邮箱: ").strip()
        department = input("新部门: ").strip()
        notes = input("新备注: ").strip()
        update_contact(
            contacts,
            contact_id,
            name=name if name else None,
            phone=phone if phone else None,
            email=email if email else None,
            department=department if department else None,
            notes=notes if notes else None,
        )
        print(f"已更新 #{contact_id}。")
    except ValueError as exc:
        print(f"更新失败: {exc}")


def handle_delete(contacts: list[dict]) -> None:
    raw = input("要删除的联系人 id: ").strip()
    if not raw.isdigit():
        print("请输入有效数字 id。")
        return
    contact_id = int(raw)
    if not delete_contact(contacts, contact_id):
        print(f"错误：找不到 id=#{contact_id}。")


def handle_save(contacts: list[dict], next_id: int, data_path: Path) -> None:
    if save_contacts(contacts, next_id, data_path):
        print(f"已保存 {len(contacts)} 条记录到 {data_path}")


def handle_reload(data_path: Path) -> tuple[list[dict], int]:
    contacts, next_id = load_contacts(data_path)
    print(f"已从 {data_path} 加载 {len(contacts)} 条记录。")
    return contacts, next_id


# ---------------------------------------------------------------------------
# 主程序入口
# ---------------------------------------------------------------------------


def main() -> None:
    """主循环：启动时自动 load，退出时自动 save。"""
    data_path = DEFAULT_DATA_FILE
    contacts, next_id = load_contacts(data_path)
    dirty = False  # 内存是否有未保存修改（教学：显式 save 与 quit 自动 save）

    print_banner()
    print("刘姐：「入职季联系人别散落在 Excel 里了，统一录进系统。」")
    print("张工：「Week 1 最后一天，把 Day 1～6 的技能串成一条交付链。」")
    if contacts:
        print(f"已加载 {len(contacts)} 条历史记录（{data_path.name}）。")

    while True:
        print_menu()
        choice = input("\n请选择: ").strip().lower()

        if choice in ("0", "quit", "q", "exit"):
            if dirty or contacts:
                if save_contacts(contacts, next_id, data_path):
                    print("退出前已自动保存。")
            print("\nWeek 1 收官愉快！明天 Day 8 进入面向对象编程。")
            break
        if choice in ("1", "add"):
            next_id = handle_add(contacts, next_id)
            dirty = True
        elif choice in ("2", "list"):
            handle_list(contacts)
        elif choice in ("3", "search"):
            handle_search(contacts)
        elif choice in ("4", "update"):
            handle_update(contacts)
            dirty = True
        elif choice in ("5", "delete"):
            handle_delete(contacts)
            dirty = True
        elif choice in ("6", "save"):
            handle_save(contacts, next_id, data_path)
            dirty = False
        elif choice in ("7", "reload"):
            confirm = input("重新加载将丢弃未保存修改，确认？(y/n): ").strip().lower()
            if confirm in ("y", "yes", "是"):
                contacts, next_id = handle_reload(data_path)
                dirty = False
        elif choice in ("8", "stats"):
            print_stats(contacts)
        else:
            print("无效选项，请输入 0-8 或命令名。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已中断。若需保留数据请重新运行并执行 save。")
        sys.exit(130)
