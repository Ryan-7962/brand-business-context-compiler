"""Prepare source evidence for an AI agent to compile into a Wiki."""

from pathlib import Path

from .source_converter import convert_source
from .source_facts import build_source_facts
from .source_quality import build_source_quality_report
from .source_versions import build_source_version_report


def prepare_wiki_sources(project_dir: Path, engine: str = "pymupdf4llm") -> Path:
    convert_source(project_dir, engine=engine)
    build_source_facts(project_dir)
    build_source_quality_report(project_dir)
    build_source_version_report(project_dir)
    converted_dir = project_dir / "converted_markdown"
    print(f"Source evidence prepared: {converted_dir}")
    print("Next: the active AI agent must compile wiki/ from the prepared evidence.")
    return converted_dir
