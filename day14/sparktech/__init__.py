# -*- coding: utf-8 -*-
"""
星火智服培训统一包 sparktech（Day 10 模式，Day 14 复用）。
"""

from .exceptions import (
    ConfigError,
    DataLoadError,
    SparkTechError,
    ValidationError,
)
from .utils import (
    get_env,
    load_json_file,
    normalize_phone,
    strip_field,
    validate_name,
    validate_phone,
)

__version__ = "0.1.0"

__all__ = [
    "ConfigError",
    "DataLoadError",
    "SparkTechError",
    "ValidationError",
    "__version__",
    "get_env",
    "load_json_file",
    "normalize_phone",
    "strip_field",
    "validate_name",
    "validate_phone",
]
