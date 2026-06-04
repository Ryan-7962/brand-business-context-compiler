"""Markdown writer helpers. Placeholder for Codex implementation."""

from __future__ import annotations

from pathlib import Path


def write_markdown(path: Path, title: str, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
