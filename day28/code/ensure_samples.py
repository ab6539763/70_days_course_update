# -*- coding: utf-8 -*-
"""
Day 28 · 样本文档生成工具

在缺少 PDF / Word 样本时，自动生成教学用 ebook.pdf 与 policy.docx。
"""

from __future__ import annotations

from pathlib import Path

SAMPLE_DIR = Path(__file__).resolve().parent / "data" / "sample_docs"

PDF_CONTENT = """星火智服 RAG 电子书 · 第一章

第一节 文档加载
企业知识库往往包含 PDF 手册、Word 制度、Markdown 技术文档与 CSV 报表。
LangChain Document Loader 将各类格式统一为 Document 对象，携带 page_content 与 metadata。

第二节 文本切块
长文档无法整段送入大模型上下文。Text Splitter 按 chunk_size 与 chunk_overlap 切分，
RecursiveCharacterTextSplitter 会优先在段落、句号处断开，保持语义完整。

第三节 退款与工单
客户可在工单系统提交退款申请，客服三个工作日内审核。
大模型 Token 额度消耗后不支持单独退款，详见退款 FAQ。

第四节 chunk_size 调参
chunk_size 过小：上下文碎片化，检索噪声多。
chunk_size 过大：单块超出 embedding 有效窗口，召回精度下降。
推荐起点：中文 300~500 字符，overlap 10%~20%。
"""

DOCX_PARAGRAPHS = [
    "星火智服客户服务制度（Word 版）",
    "第一条：在线客服工作日 9:00-18:00 实时响应。",
    "第二条：工单 24 小时内首次回复，紧急工单 4 小时内升级。",
    "第三条：大模型回答仅供参考，退款与合同变更须经人工确认。",
    "第四条：知识库 txt、md 文档仅限内网访问，批量导出需审批。",
    "第五条：退款类咨询请优先查阅退款 FAQ，减少重复工单。",
    "第六条：每月统计工单与大模型会话高频关键词，用于培训与知识库更新。",
]


def ensure_sample_pdf(path: Path | None = None) -> Path:
    """生成最小 PDF 样本；正文以 ebook.pdf.txt 为主（PyPDF 提取可能为空）。"""
    target = path or (SAMPLE_DIR / "ebook.pdf")
    txt_path = target.with_suffix(".pdf.txt")
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    txt_path.write_text(PDF_CONTENT, encoding="utf-8")

    if target.is_file():
        return target

    try:
        from pypdf import PdfWriter
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("需要安装 pypdf: pip install pypdf") from exc

    writer = PdfWriter()
    writer.add_blank_page(width=595, height=842)
    with target.open("wb") as fh:
        writer.write(fh)
    return target


def ensure_sample_docx(path: Path | None = None) -> Path:
    """生成 Word 样本。"""
    target = path or (SAMPLE_DIR / "policy.docx")
    if target.is_file():
        return target

    try:
        from docx import Document
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("需要安装 python-docx: pip install python-docx") from exc

    doc = Document()
    for para in DOCX_PARAGRAPHS:
        doc.add_paragraph(para)
    target.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(target))
    return target


def ensure_all_samples() -> dict[str, Path]:
    """确保 PDF 与 DOCX 样本存在。"""
    return {
        "pdf": ensure_sample_pdf(),
        "docx": ensure_sample_docx(),
    }


if __name__ == "__main__":
    paths = ensure_all_samples()
    for kind, p in paths.items():
        print(f"[OK] {kind}: {p} ({p.stat().st_size} bytes)")
