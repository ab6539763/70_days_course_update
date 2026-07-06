# -*- coding: utf-8 -*-
"""Runtime configuration for Project 3 office assistant."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
SAMPLE_DOCS_DIR = DATA_DIR / "sample_docs"
CHECKPOINT_DIR = Path(os.getenv("CHECKPOINT_DIR", str(DATA_DIR / "checkpoints")))


def is_mock_mode() -> bool:
    return os.getenv("SPARKTECH_MOCK", "1").strip().lower() in {"1", "true", "yes", "on"}


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
