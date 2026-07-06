# -*- coding: utf-8 -*-
"""多格式文档摄取：txt / md / pdf。"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from .database import DATA_DIR
from .models import DocumentRecord, KnowledgeChunk
from .rag_common import chunk_text, embedding_to_json, mock_embed_text

UPLOAD_DIR = DATA_DIR / "uploads"
SAMPLE_DIR = DATA_DIR / "sample_docs"
ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf"}


@dataclass
class IngestResult:
    document: DocumentRecord
    chunks: list[KnowledgeChunk]


def ensure_dirs() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)


def _extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PDF 解析需要 pypdf，请 pip install pypdf") from exc

    reader = PdfReader(str(path))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text.strip())
    return "\n\n".join(parts)


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="replace")
    if suffix == ".pdf":
        return _extract_pdf_text(path)
    raise ValueError(f"不支持的文件类型: {suffix}")


def normalize_filename(name: str) -> str:
    base = Path(name).name
    base = re.sub(r"[^\w.\-一-龥]", "_", base)
    return base[:200] or f"doc_{uuid.uuid4().hex[:8]}"


def ingest_file(db: Session, file_path: Path, original_name: str | None = None) -> IngestResult:
    """解析单文件、切块、写入数据库。"""
    ensure_dirs()
    suffix = file_path.suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError(f"仅支持 {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    filename = original_name or file_path.name
    text = extract_text(file_path)
    if not text.strip():
        raise ValueError(f"文件内容为空: {filename}")

    doc = DocumentRecord(
        filename=normalize_filename(filename),
        file_type=suffix.lstrip("."),
        file_path=str(file_path.resolve()),
        char_count=len(text),
        status="processing",
    )
    db.add(doc)
    db.flush()

    pieces = chunk_text(text, chunk_size=380, overlap=70)
    chunks: list[KnowledgeChunk] = []
    for idx, piece in enumerate(pieces):
        chunk_id = f"{doc.id}-{uuid.uuid4().hex[:8]}"
        emb = mock_embed_text(piece, model="mock-kb-ingest")
        chunk = KnowledgeChunk(
            chunk_id=chunk_id,
            document_id=doc.id,
            source=doc.filename,
            content=piece,
            chunk_index=idx,
            embedding_json=embedding_to_json(emb),
        )
        db.add(chunk)
        chunks.append(chunk)

    doc.chunk_count = len(chunks)
    doc.status = "indexed"
    db.commit()
    db.refresh(doc)
    for c in chunks:
        db.refresh(c)
    return IngestResult(document=doc, chunks=chunks)


def ingest_bytes(
    db: Session,
    filename: str,
    content: bytes,
) -> IngestResult:
    """保存上传字节并摄取。"""
    ensure_dirs()
    safe_name = normalize_filename(filename)
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex[:8]}_{safe_name}"
    dest.write_bytes(content)
    return ingest_file(db, dest, original_name=safe_name)


def ingest_directory(db: Session, directory: Path | None = None) -> list[IngestResult]:
    """批量摄取目录下文档（用于初始化样本库）。"""
    ensure_dirs()
    target = directory or SAMPLE_DIR
    results: list[IngestResult] = []
    if not target.is_dir():
        return results

    for path in sorted(target.iterdir()):
        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        existing = (
            db.query(DocumentRecord)
            .filter(DocumentRecord.file_path == str(path.resolve()))
            .first()
        )
        if existing:
            continue
        try:
            results.append(ingest_file(db, path, original_name=path.name))
        except (ValueError, RuntimeError) as exc:
            print(f"[ingest] skip {path.name}: {exc}")
    return results


def rebuild_index(db: Session) -> tuple[int, int]:
    """删除所有 chunk 后按文档重新切块（教学用简化版）。"""
    docs = db.query(DocumentRecord).order_by(DocumentRecord.id.asc()).all()
    db.query(KnowledgeChunk).delete(synchronize_session=False)
    db.commit()

    total_chunks = 0
    for doc in docs:
        path = Path(doc.file_path)
        if not path.is_file():
            doc.status = "missing"
            continue
        try:
            text = extract_text(path)
            pieces = chunk_text(text, chunk_size=380, overlap=70)
            for idx, piece in enumerate(pieces):
                chunk_id = f"{doc.id}-{uuid.uuid4().hex[:8]}"
                emb = mock_embed_text(piece, model="mock-kb-ingest")
                db.add(
                    KnowledgeChunk(
                        chunk_id=chunk_id,
                        document_id=doc.id,
                        source=doc.filename,
                        content=piece,
                        chunk_index=idx,
                        embedding_json=embedding_to_json(emb),
                    )
                )
            doc.char_count = len(text)
            doc.chunk_count = len(pieces)
            doc.status = "indexed"
            total_chunks += len(pieces)
        except (ValueError, RuntimeError) as exc:
            doc.status = f"error: {exc}"[:32]
    db.commit()
    return len(docs), total_chunks
