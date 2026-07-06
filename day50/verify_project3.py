#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 50 验收入口 — 委托 day48 project3/verify_project3.py"""
import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).parent.parent / "day48" / "code" / "project3" / "verify_project3.py"),
    run_name="__main__",
)
