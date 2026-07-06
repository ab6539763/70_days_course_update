# -*- coding: utf-8 -*-
"""Day 14 · JSON 会话持久化（集成 Day 10 sparktech 异常与 IO 模式）。"""

from __future__ import annotations

import json
from pathlib import Path

from sparktech.exceptions import DataLoadError, SparkTechError

from project1.session import ConversationSession

DEFAULT_SESSIONS_DIR = Path(__file__).resolve().parent.parent / "data" / "sessions"


class SessionStorageError(SparkTechError):
    """会话存储相关错误。"""

    def __init__(self, message: str, *, path: str = "") -> None:
        super().__init__(message, code="SESSION_STORAGE_ERROR")
        self.path = path


def ensure_sessions_dir(base_dir: Path | None = None) -> Path:
    target = base_dir or DEFAULT_SESSIONS_DIR
    target.mkdir(parents=True, exist_ok=True)
    return target


def build_session_path(session: ConversationSession, base_dir: Path | None = None) -> Path:
    directory = ensure_sessions_dir(base_dir)
    safe_id = session.session_id.replace("/", "_")
    return directory / f"{safe_id}.json"


def save_session(
    session: ConversationSession,
    *,
    base_dir: Path | None = None,
    path: Path | None = None,
) -> Path:
    """将会话序列化为 JSON 文件，返回写入路径。"""
    file_path = path or build_session_path(session, base_dir)
    payload = session.to_dict()
    try:
        file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError as exc:
        raise SessionStorageError(f"无法写入会话文件: {exc}", path=str(file_path)) from exc
    return file_path


def load_session(path: Path | str) -> ConversationSession:
    """从 JSON 文件恢复会话。"""
    file_path = Path(path)
    if not file_path.is_file():
        raise SessionStorageError(f"会话文件不存在: {file_path}", path=str(file_path))

    try:
        text = file_path.read_text(encoding="utf-8")
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise DataLoadError(
            f"JSON 解析失败（行 {exc.lineno} 列 {exc.colno}）: {exc.msg}",
            path=str(file_path),
        ) from exc
    except OSError as exc:
        raise DataLoadError(f"无法读取文件: {exc}", path=str(file_path)) from exc

    if not isinstance(data, dict) or "messages" not in data:
        raise SessionStorageError("会话 JSON 格式非法：缺少 messages 字段", path=str(file_path))

    return ConversationSession.from_dict(data)


def list_session_files(base_dir: Path | None = None) -> list[Path]:
    directory = ensure_sessions_dir(base_dir)
    return sorted(directory.glob("*.json"))
