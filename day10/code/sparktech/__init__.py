# -*- coding: utf-8 -*-
"""
星火智服培训统一包 sparktech。

Day 10 将 Day 6 分散的 sparktech_* 脚本收敛到单一命名空间，
并补充 exceptions 与 utils 子包。
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
