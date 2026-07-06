# -*- coding: utf-8 -*-
"""字符串清洗包：Day 2 脚本重构后的可复用函数。"""

from .cleaners import (
    apply_pipeline,
    collapse_spaces,
    load_sensitive_words,
    mask_sensitive,
    normalize_case,
    remove_all_spaces,
    strip_edges,
)
from .constants import CaseMode

__all__ = [
    "CaseMode",
    "apply_pipeline",
    "collapse_spaces",
    "load_sensitive_words",
    "mask_sensitive",
    "normalize_case",
    "remove_all_spaces",
    "strip_edges",
]
