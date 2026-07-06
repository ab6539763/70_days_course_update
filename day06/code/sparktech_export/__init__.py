# -*- coding: utf-8 -*-
"""员工 JSON 导出包：Day 5 脚本重构后的可复用函数。"""

from .api import (
    assert_api_success,
    extract_employees,
    get_pagination,
    load_mock_response,
    parse_employees_from_file,
)
from .employee import (
    EXPORT_FIELDS,
    OUTPUT_PATH,
    build_export_report,
    clean_all_employees,
    clean_employee,
    export_employees_from_mock,
    write_employees_json,
)

__all__ = [
    "EXPORT_FIELDS",
    "OUTPUT_PATH",
    "assert_api_success",
    "build_export_report",
    "clean_all_employees",
    "clean_employee",
    "export_employees_from_mock",
    "extract_employees",
    "get_pagination",
    "load_mock_response",
    "parse_employees_from_file",
    "write_employees_json",
]
