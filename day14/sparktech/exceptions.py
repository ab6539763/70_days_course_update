# -*- coding: utf-8 -*-
"""星火智服培训库 · 自定义异常层次。"""

from __future__ import annotations


class SparkTechError(Exception):
    """所有 sparktech 业务异常的基类。"""

    def __init__(self, message: str, *, code: str = "SPARKTECH_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class ValidationError(SparkTechError):
    """输入校验失败。"""

    def __init__(self, message: str, *, field: str = "") -> None:
        super().__init__(message, code="VALIDATION_ERROR")
        self.field = field


class ConfigError(SparkTechError):
    """环境变量或配置文件缺失/非法。"""

    def __init__(self, message: str, *, key: str = "") -> None:
        super().__init__(message, code="CONFIG_ERROR")
        self.key = key


class DataLoadError(SparkTechError):
    """JSON / 文本文件读取或解析失败。"""

    def __init__(self, message: str, *, path: str = "") -> None:
        super().__init__(message, code="DATA_LOAD_ERROR")
        self.path = path
