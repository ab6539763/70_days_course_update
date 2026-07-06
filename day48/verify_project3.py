#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Day 48 验收入口 — 委托 project3/verify_project3.py"""
import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).parent / "code" / "project3" / "verify_project3.py"),
    run_name="__main__",
)
