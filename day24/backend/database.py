# -*- coding: utf-8 -*-
"""Day 24 · SQLite 数据库连接与 Session 工厂。"""

from __future__ import annotations

import os
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BACKEND_DIR = Path(__file__).resolve().parent
DAY24_DIR = BACKEND_DIR.parent
DEFAULT_DB_PATH = DAY24_DIR / "data" / "chat_history.db"


def _resolve_database_url() -> str:
    explicit = os.getenv("DATABASE_URL", "").strip()
    if explicit:
        return explicit
    db_path = os.getenv("SQLITE_PATH", str(DEFAULT_DB_PATH))
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}"


DATABASE_URL = _resolve_database_url()
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=os.getenv("SQLALCHEMY_ECHO", "").lower() in {"1", "true", "yes"},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    """SQLAlchemy 声明基类。"""


def init_db() -> None:
    """创建所有表（若不存在）。"""
    # 延迟导入避免循环依赖
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖：请求级 DB Session。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
