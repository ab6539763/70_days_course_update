# -*- coding: utf-8 -*-
"""
Day 20 · 多模态 API 入门（图像理解）

- live 模式：OpenAI 兼容 vision chat/completions
- mock 模式：根据图片文件名返回确定性描述
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]


DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_VISION_MODEL = "gpt-4o-mini"
ENV_API_KEY = "OPENAI_API_KEY"
ENV_BASE_URL = "OPENAI_BASE_URL"
ENV_VISION_MODEL = "OPENAI_VISION_MODEL"

# 1x1 红色 PNG（教学用最小合法图片）
TINY_RED_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


@dataclass
class VisionResult:
    description: str
    model: str
    mode: str
    image_source: str
    latency_ms: float = 0.0
    raw: dict[str, Any] = field(default_factory=dict)


def load_dotenv_file() -> None:
    if load_dotenv is None:
        return
    code_dir = Path(__file__).resolve().parent
    for candidate in (code_dir / ".env", code_dir.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate)
            return
    load_dotenv()


def image_to_data_url(path: Path) -> str:
    """本地图片 → data URL（base64）。"""
    suffix = path.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "gif": "image/gif"}.get(
        suffix, "image/png"
    )
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


class MultimodalClient:
    """图像理解轻量客户端。"""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        load_dotenv_file()
        self._api_key = (api_key or os.getenv(ENV_API_KEY) or "").strip()
        self._base_url = (base_url or os.getenv(ENV_BASE_URL) or DEFAULT_BASE_URL).rstrip("/")
        self._model = model or os.getenv(ENV_VISION_MODEL) or DEFAULT_VISION_MODEL
        self._timeout = timeout

    @property
    def is_mock_mode(self) -> bool:
        return not self._api_key

    @property
    def mode(self) -> str:
        return "mock" if self.is_mock_mode else "live"

    def describe_image(
        self,
        image_path: Path | None = None,
        *,
        prompt: str = "请用中文简要描述这张图片的内容。",
    ) -> VisionResult:
        if image_path and image_path.is_file():
            source = str(image_path.name)
            data_url = image_to_data_url(image_path)
        else:
            source = "builtin_tiny_red.png"
            data_url = f"data:image/png;base64,{TINY_RED_PNG_B64}"

        if self.is_mock_mode:
            return self._mock_describe(source, prompt)
        return self._live_describe(data_url, source, prompt)

    def _mock_describe(self, source: str, prompt: str) -> VisionResult:
        start = time.perf_counter()
        digest = hashlib.md5(f"{source}:{prompt}".encode()).hexdigest()[:8]
        description = (
            f"[mock 视觉] 图片「{source}」：检测到纯色块或示意图样；"
            f"若为用户上传的工业质检图，可能含产品边缘与缺陷标注区域。（id={digest}）"
        )
        latency_ms = (time.perf_counter() - start) * 1000
        return VisionResult(
            description=description,
            model=f"mock-vision",
            mode="mock",
            image_source=source,
            latency_ms=round(latency_ms, 2),
            raw={"mock": True},
        )

    def _live_describe(self, data_url: str, source: str, prompt: str) -> VisionResult:
        if requests is None:
            raise RuntimeError("未安装 requests")

        url = f"{self._base_url}/chat/completions"
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ]
        payload = {"model": self._model, "messages": messages, "max_tokens": 300}
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        start = time.perf_counter()
        resp = requests.post(url, headers=headers, json=payload, timeout=self._timeout)
        latency_ms = (time.perf_counter() - start) * 1000

        if resp.status_code >= 400:
            raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        return VisionResult(
            description=text,
            model=data.get("model", self._model),
            mode="live",
            image_source=source,
            latency_ms=round(latency_ms, 2),
            raw=data,
        )


def main() -> None:
    print("=" * 60)
    print("Day 20 · multimodal_demo.py（图像理解）")
    print("=" * 60)

    client = MultimodalClient()
    print(f"模式: {client.mode}")

    images_dir = Path(__file__).resolve().parent / "images"
    sample = images_dir / "sample_diagram.png"
    if not sample.is_file():
        # 写入最小 PNG 供演示
        images_dir.mkdir(parents=True, exist_ok=True)
        sample.write_bytes(base64.b64decode(TINY_RED_PNG_B64))

    result = client.describe_image(sample)
    print(f"\n图片: {result.image_source}")
    print(f"描述: {result.description}")
    print(json.dumps({"mode": result.mode, "latency_ms": result.latency_ms}, ensure_ascii=False))

    print("\n✅ multimodal_demo.py 完成")


if __name__ == "__main__":
    main()
