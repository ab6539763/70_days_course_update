# -*- coding: utf-8 -*-
"""SQLAlchemy 数据库连接与会话管理。"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DB = DATA_DIR / "kb_qa.db"
SQLITE_PATH = Path(os.getenv("SQLITE_PATH", str(DEFAULT_DB)))

DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=os.getenv("SQL_ECHO", "0") == "1",
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """创建所有表。"""
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
