"""Verify the structural and traceability contract for an agent-neutral Wiki."""

from __future__ import annotations

import re
from pathlib import Path


REQUIRED_HEADINGS = (
    "文件概述",
    "内容大纲",
    "核心观点",
    "关键事实",
    "业务关系",
    "不确定项",
    "来源",
)
INDEX_COLUMNS = (
    "Source ID",
    "文件名",
    "事实摘要",
    "知识页",
    "转写稿",
    "版本线索",
    "何时阅读",
)
UNRESOLVED_PLACEHOLDERS = ("待补充", "待填写", "TODO", "TBD", "{{", "}}")


def verify_wiki(project_dir: Path) -> None:
    issues = collect_wiki_issues(project_dir)
    if issues:
        print("Wiki verification failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print("Wiki verification passed.")


def collect_wiki_issues(project_dir: Path) -> list[str]:
    """Return coverage and traceability failures without judging semantic quality."""
    issues: list[str] = []
    source_ids = _source_ids_from_conversion_report(project_dir, issues)
    wiki_dir = project_dir / "wiki"
    if not wiki_dir.is_dir():
        return [*issues, "Missing wiki/ directory."]

    index_path = wiki_dir / "00_index.md"
    index_source_ids = _source_ids_from_index(index_path, issues)
    for source_id in source_ids:
        occurrences = index_source_ids.count(source_id)
        if occurrences == 0:
            issues.append(f"Missing index entry for {source_id}.")
        elif occurrences > 1:
            issues.append(f"Index has duplicate entries for {source_id}.")
    for source_id in sorted(set(index_source_ids) - set(source_ids)):
        issues.append(f"Index references unknown source {source_id}.")

    uncertainties_path = wiki_dir / "uncertainties.md"
    if not uncertainties_path.is_file():
        issues.append("Missing wiki/uncertainties.md.")
    elif not _has_heading(uncertainties_path.read_text(encoding="utf-8"), "异常与不确定项", level=1):
        issues.append("wiki/uncertainties.md is missing the '# 异常与不确定项' heading.")

    documents_dir = wiki_dir / "documents"
    if not documents_dir.is_dir():
        issues.append("Missing wiki/documents/ directory.")
    else:
        for source_id in source_ids:
            document_path = documents_dir / f"{source_id}.md"
            if not document_path.is_file():
                issues.append(f"Missing knowledge page for {source_id}: wiki/documents/{source_id}.md.")
                continue
            _collect_document_issues(document_path, source_id, issues)

    for markdown_path in _wiki_markdown_files(wiki_dir):
        _collect_placeholder_issues(markdown_path, project_dir, issues)
    return issues


def _source_ids_from_conversion_report(project_dir: Path, issues: list[str]) -> list[str]:
    report_path = project_dir / "converted_markdown" / "conversion_report.md"
    if not report_path.is_file():
        issues.append("Missing converted_markdown/conversion_report.md.")
        return []
    table = _find_table(report_path.read_text(encoding="utf-8"), {"来源编号", "原始文件", "转写 Markdown"})
    if table is None:
        issues.append("conversion_report.md is missing the Source Files table headers.")
        return []
    headers, rows = table
    source_id_index = headers.index("来源编号")
    source_ids = [row[source_id_index] for row in rows if len(row) > source_id_index and row[source_id_index]]
    if not source_ids:
        issues.append("conversion_report.md has no source entries.")
    return source_ids


def _source_ids_from_index(index_path: Path, issues: list[str]) -> list[str]:
    if not index_path.is_file():
        issues.append("Missing wiki/00_index.md.")
        return []
    table = _find_table(index_path.read_text(encoding="utf-8"), set(INDEX_COLUMNS))
    if table is None:
        issues.append("wiki/00_index.md is missing required index columns.")
        return []
    headers, rows = table
    source_id_index = headers.index("Source ID")
    return [row[source_id_index] for row in rows if len(row) > source_id_index and row[source_id_index]]


def _find_table(markdown: str, required_headers: set[str]) -> tuple[list[str], list[list[str]]] | None:
    lines = markdown.splitlines()
    for index, line in enumerate(lines[:-1]):
        headers = _table_cells(line)
        if not headers or not required_headers.issubset(headers):
            continue
        if not _is_table_separator(lines[index + 1]):
            continue
        rows: list[list[str]] = []
        for row_line in lines[index + 2 :]:
            cells = _table_cells(row_line)
            if not cells:
                break
            rows.append(cells)
        return headers, rows
    return None


def _table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _is_table_separator(line: str) -> bool:
    cells = _table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _collect_document_issues(document_path: Path, source_id: str, issues: list[str]) -> None:
    markdown = document_path.read_text(encoding="utf-8")
    for heading in REQUIRED_HEADINGS:
        if not _has_heading(markdown, heading, level=2):
            issues.append(f"{document_path.relative_to(document_path.parents[2])} is missing '## {heading}'.")
    anchor_pattern = rf"\[来源:\s*{re.escape(source_id)}#(?:page|slide)=\d+(?:-\d+)?\]"
    if not re.search(anchor_pattern, markdown):
        issues.append(f"{document_path.relative_to(document_path.parents[2])} has no source anchor for {source_id}.")


def _has_heading(markdown: str, heading: str, *, level: int) -> bool:
    return bool(re.search(rf"^{'#' * level}\s+{re.escape(heading)}\s*$", markdown, flags=re.MULTILINE))


def _wiki_markdown_files(wiki_dir: Path) -> list[Path]:
    return sorted(path for path in wiki_dir.rglob("*.md") if path.is_file())


def _collect_placeholder_issues(markdown_path: Path, project_dir: Path, issues: list[str]) -> None:
    markdown = markdown_path.read_text(encoding="utf-8")
    for line_number, line in enumerate(markdown.splitlines(), start=1):
        for placeholder in UNRESOLVED_PLACEHOLDERS:
            if placeholder in line:
                relative_path = markdown_path.relative_to(project_dir)
                issues.append(f"{relative_path}:{line_number} contains unresolved placeholder '{placeholder}'.")
                break
