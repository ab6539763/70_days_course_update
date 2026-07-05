# -*- coding: utf-8 -*-
"""待办管理包：Day 4 脚本重构后的可复用函数与 CLI。"""

from .cli import run_cli
from .core import (
    VALID_PRIORITIES,
    add_todo,
    complete_todo,
    compute_stats,
    delete_todo,
    find_index_by_id,
    format_todo,
    list_todos,
    parse_tags,
)

__all__ = [
    "VALID_PRIORITIES",
    "add_todo",
    "complete_todo",
    "compute_stats",
    "delete_todo",
    "find_index_by_id",
    "format_todo",
    "list_todos",
    "parse_tags",
    "run_cli",
]
