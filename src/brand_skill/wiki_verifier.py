"""Verify the structural and traceability contract for an agent-neutral Wiki."""

from __future__ import annotations

from dataclasses import dataclass
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
    "内容概述",
    "知识页",
    "转写稿",
    "版本线索",
    "何时阅读",
)
CONVERSION_COLUMNS = ("来源编号", "原始文件", "转写 Markdown", "页码/Slide 范围")
UNRESOLVED_PLACEHOLDERS = ("待补充", "待填写", "TODO", "TBD", "{{", "}}")
NO_UNCERTAINTIES_TEXT = "未发现需要人工处理的读取异常。"


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    filename: str
    transcript_path: Path
    page_range: str


def verify_wiki(project_dir: Path) -> None:
    issues = collect_wiki_issues(project_dir)
    if issues:
        print("Wiki verification failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print("Wiki verification passed.")


def collect_wiki_issues(project_dir: Path) -> list[str]:
    """Return structural and deterministic-evidence failures, not semantic judgments."""
    issues: list[str] = []
    source_records = _source_records_from_conversion_report(project_dir, issues)
    transcript_anchors = _collect_transcript_anchors(source_records, issues)
    wiki_dir = project_dir / "wiki"
    if not wiki_dir.is_dir():
        return [*issues, "Missing wiki/ directory."]

    index_source_ids = _collect_index_issues(project_dir, wiki_dir / "00_index.md", source_records, issues)
    _collect_index_coverage_issues(source_records, index_source_ids, issues)
    _collect_uncertainties_issues(wiki_dir / "uncertainties.md", project_dir, transcript_anchors, issues)
    _collect_documents_issues(project_dir, wiki_dir / "documents", source_records, transcript_anchors, issues)

    for markdown_path in _wiki_markdown_files(wiki_dir):
        _collect_placeholder_issues(markdown_path, project_dir, issues)
    return issues


def _source_records_from_conversion_report(project_dir: Path, issues: list[str]) -> dict[str, SourceRecord]:
    report_path = project_dir / "converted_markdown" / "conversion_report.md"
    if not report_path.is_file():
        issues.append("Missing converted_markdown/conversion_report.md.")
        return {}
    table = _find_table(report_path.read_text(encoding="utf-8"), set(CONVERSION_COLUMNS))
    if table is None:
        issues.append("conversion_report.md is missing required source and range columns.")
        return {}

    headers, rows = table
    records: dict[str, SourceRecord] = {}
    for row_number, row in enumerate(rows, start=1):
        if len(row) != len(headers):
            issues.append(f"conversion_report.md source row {row_number} has an invalid column count.")
            continue
        values = dict(zip(headers, row))
        source_id = values["来源编号"]
        filename = values["原始文件"]
        transcript_value = values["转写 Markdown"]
        page_range = values["页码/Slide 范围"]
        if not source_id or not filename or not transcript_value or not page_range:
            issues.append(f"conversion_report.md source row {row_number} has an empty required field.")
            continue
        if source_id in records:
            issues.append(f"conversion_report.md has duplicate source {source_id}.")
            continue
        transcript_path = _project_path(project_dir, transcript_value)
        if transcript_path is None:
            issues.append(f"conversion_report.md has an invalid transcript path for {source_id}.")
            continue
        records[source_id] = SourceRecord(source_id, filename, transcript_path, page_range)

    if not records:
        issues.append("conversion_report.md has no source entries.")
    return records


def _collect_transcript_anchors(
    source_records: dict[str, SourceRecord],
    issues: list[str],
) -> dict[str, set[str]]:
    anchors_by_source: dict[str, set[str]] = {}
    for source_id, record in source_records.items():
        if not record.transcript_path.is_file():
            issues.append(f"Missing transcript for {source_id}: {record.transcript_path}.")
            anchors_by_source[source_id] = set()
            continue

        transcript = record.transcript_path.read_text(encoding="utf-8")
        anchors = set(_transcript_anchors(transcript))
        source_anchors = {anchor for anchor in anchors if anchor.startswith(f"{source_id}#")}
        anchors_by_source[source_id] = source_anchors
        if not source_anchors:
            issues.append(f"Transcript for {source_id} has no source anchors.")
            continue
        _collect_range_coverage_issues(record, source_anchors, issues)
    return anchors_by_source


def _transcript_anchors(markdown: str) -> list[str]:
    return re.findall(r"^\s*-\s*Source Anchor[：:]\s*([^\s]+)\s*$", markdown, flags=re.MULTILINE)


def _collect_range_coverage_issues(record: SourceRecord, anchors: set[str], issues: list[str]) -> None:
    expected_numbers = _range_numbers(record.page_range)
    if not expected_numbers:
        issues.append(f"{record.source_id} has an invalid conversion range: {record.page_range}.")
        return
    kinds = {
        match.group("kind")
        for anchor in anchors
        if (match := re.fullmatch(rf"{re.escape(record.source_id)}#(?P<kind>page|slide)=(?P<number>\d+)", anchor))
    }
    if not kinds:
        issues.append(f"Transcript for {record.source_id} has no valid page or slide anchors.")
        return
    for kind in kinds:
        for number in expected_numbers:
            anchor = f"{record.source_id}#{kind}={number}"
            if anchor not in anchors:
                issues.append(f"{record.source_id} conversion range is missing transcript anchor {anchor}.")


def _range_numbers(page_range: str) -> range | None:
    match = re.fullmatch(r"\s*(\d+)(?:\s*-\s*(\d+))?\s*", page_range)
    if not match:
        return None
    start = int(match.group(1))
    end = int(match.group(2) or start)
    return range(start, end + 1) if start <= end else None


def _collect_index_issues(
    project_dir: Path,
    index_path: Path,
    source_records: dict[str, SourceRecord],
    issues: list[str],
) -> list[str]:
    if not index_path.is_file():
        issues.append("Missing wiki/00_index.md.")
        return []
    table = _index_table(index_path.read_text(encoding="utf-8"))
    if table is None:
        issues.append("wiki/00_index.md must use exactly the required seven columns.")
        return []

    headers, rows = table
    if tuple(headers) != INDEX_COLUMNS:
        issues.append("wiki/00_index.md must use exactly the required seven columns.")
        return []

    source_ids: list[str] = []
    for row_number, row in enumerate(rows, start=1):
        if len(row) != len(INDEX_COLUMNS):
            issues.append(f"wiki/00_index.md row {row_number} has an invalid column count.")
            continue
        values = dict(zip(INDEX_COLUMNS, row))
        source_id = values["Source ID"]
        label = source_id or _sole_source_id(source_records)
        for column, value in values.items():
            if not value:
                issues.append(f"index row for {label} has an invalid {column}.")
        if not source_id:
            continue
        source_ids.append(source_id)
        record = source_records.get(source_id)
        if record is None:
            continue
        if values["文件名"] != record.filename:
            issues.append(f"index row for {source_id} has an invalid 文件名.")
        expected_document = f"wiki/documents/{source_id}.md"
        if not _is_expected_project_file(project_dir, values["知识页"], expected_document):
            issues.append(f"index row for {source_id} has an invalid 知识页.")
        expected_transcript = record.transcript_path.relative_to(project_dir.resolve()).as_posix()
        if not _is_expected_project_file(project_dir, values["转写稿"], expected_transcript):
            issues.append(f"index row for {source_id} has an invalid 转写稿.")
    return source_ids


def _index_table(markdown: str) -> tuple[list[str], list[list[str]]] | None:
    for headers, rows in _markdown_tables(markdown):
        if "Source ID" in headers:
            return headers, rows
    return None


def _sole_source_id(source_records: dict[str, SourceRecord]) -> str:
    return next(iter(source_records), "<empty>") if len(source_records) == 1 else "<empty>"


def _is_expected_project_file(project_dir: Path, value: str, expected_relative_path: str) -> bool:
    path = _project_path(project_dir, value)
    return path is not None and value == expected_relative_path and path.is_file()


def _collect_index_coverage_issues(
    source_records: dict[str, SourceRecord],
    index_source_ids: list[str],
    issues: list[str],
) -> None:
    for source_id in source_records:
        occurrences = index_source_ids.count(source_id)
        if occurrences == 0:
            issues.append(f"Missing index entry for {source_id}.")
        elif occurrences > 1:
            issues.append(f"Index has duplicate entries for {source_id}.")
    for source_id in sorted(set(index_source_ids) - set(source_records)):
        issues.append(f"Index references unknown source {source_id}.")


def _collect_uncertainties_issues(
    uncertainties_path: Path,
    project_dir: Path,
    transcript_anchors: dict[str, set[str]],
    issues: list[str],
) -> None:
    if not uncertainties_path.is_file():
        issues.append("Missing wiki/uncertainties.md.")
        return
    markdown = uncertainties_path.read_text(encoding="utf-8")
    if not _has_heading(markdown, "异常与不确定项", level=1):
        issues.append("wiki/uncertainties.md is missing the '# 异常与不确定项' heading.")

    review_anchors = _review_anchors_from_quality_report(project_dir, issues)
    known_anchors = set().union(*transcript_anchors.values()) if transcript_anchors else set()
    real_review_anchors = []
    for anchor in review_anchors:
        if anchor not in known_anchors:
            issues.append(f"source_quality_report.md review anchor is not present in a transcript: {anchor}.")
        else:
            real_review_anchors.append(anchor)
    if not real_review_anchors:
        return
    if NO_UNCERTAINTIES_TEXT in markdown:
        issues.append("uncertainties.md cannot claim no reading exceptions when review anchors exist.")
    for anchor in real_review_anchors:
        if anchor not in markdown:
            issues.append(f"uncertainties.md must list review anchor {anchor}.")


def _review_anchors_from_quality_report(project_dir: Path, issues: list[str]) -> list[str]:
    quality_path = project_dir / "converted_markdown" / "source_quality_report.md"
    if not quality_path.is_file():
        issues.append("Missing converted_markdown/source_quality_report.md.")
        return []
    section = _section_after_heading(quality_path.read_text(encoding="utf-8"), "需要复核的页面", level=2)
    if section is None:
        issues.append("source_quality_report.md is missing the '需要复核的页面' section.")
        return []
    table = _find_table(section, {"Source Anchor"})
    if table is None:
        issues.append("source_quality_report.md is missing the review-anchor table.")
        return []
    headers, rows = table
    anchor_index = headers.index("Source Anchor")
    return [row[anchor_index] for row in rows if len(row) > anchor_index and row[anchor_index] != "-"]


def _section_after_heading(markdown: str, heading: str, *, level: int) -> str | None:
    match = re.search(rf"^{'#' * level}\s+{re.escape(heading)}\s*$", markdown, flags=re.MULTILINE)
    if not match:
        return None
    next_heading = re.search(rf"^#{{1,{level}}}\s+", markdown[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(markdown)
    return markdown[match.end() : end]


def _collect_documents_issues(
    project_dir: Path,
    documents_dir: Path,
    source_records: dict[str, SourceRecord],
    transcript_anchors: dict[str, set[str]],
    issues: list[str],
) -> None:
    if not documents_dir.is_dir():
        issues.append("Missing wiki/documents/ directory.")
        return
    expected_paths = {f"{source_id}.md" for source_id in source_records}
    actual_paths = {
        path.relative_to(documents_dir).as_posix()
        for path in documents_dir.rglob("*")
        if path.is_file()
    }
    for path in sorted(actual_paths - expected_paths):
        issues.append(f"Unknown knowledge page: wiki/documents/{path}.")
    for source_id in source_records:
        document_path = documents_dir / f"{source_id}.md"
        if not document_path.is_file():
            issues.append(f"Missing knowledge page for {source_id}: wiki/documents/{source_id}.md.")
            continue
        _collect_document_issues(document_path, project_dir, source_id, transcript_anchors.get(source_id, set()), issues)


def _collect_document_issues(
    document_path: Path,
    project_dir: Path,
    source_id: str,
    transcript_anchors: set[str],
    issues: list[str],
) -> None:
    markdown = document_path.read_text(encoding="utf-8")
    relative_path = document_path.relative_to(project_dir)
    for heading in REQUIRED_HEADINGS:
        if not _has_heading(markdown, heading, level=2):
            issues.append(f"{relative_path} is missing '## {heading}'.")
    labels = re.findall(r"\[来源:\s*([^\]]+)\]", markdown)
    if not labels:
        issues.append(f"{relative_path} has no source anchor for {source_id}.")
        return
    for label in labels:
        match = re.fullmatch(r"([^#\s]+)#(page|slide)=(\d+)", label.strip())
        if match is None:
            issues.append(f"{relative_path} has an invalid source anchor: {label}.")
            continue
        anchor_source, anchor_kind, anchor_number = match.groups()
        anchor = f"{anchor_source}#{anchor_kind}={anchor_number}"
        if anchor_source != source_id:
            issues.append(f"{relative_path} source anchor {anchor} does not belong to {source_id}.")
        elif anchor not in transcript_anchors:
            issues.append(f"{relative_path} source anchor {anchor} is not present in its transcript.")


def _find_table(markdown: str, required_headers: set[str]) -> tuple[list[str], list[list[str]]] | None:
    for headers, rows in _markdown_tables(markdown):
        if required_headers.issubset(headers):
            return headers, rows
    return None


def _markdown_tables(markdown: str) -> list[tuple[list[str], list[list[str]]]]:
    lines = markdown.splitlines()
    tables: list[tuple[list[str], list[list[str]]]] = []
    for index, line in enumerate(lines[:-1]):
        headers = _table_cells(line)
        if not headers or not _is_table_separator(lines[index + 1]):
            continue
        rows: list[list[str]] = []
        for row_line in lines[index + 2 :]:
            cells = _table_cells(row_line)
            if not cells:
                break
            rows.append(cells)
        tables.append((headers, rows))
    return tables


def _table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def _is_table_separator(line: str) -> bool:
    cells = _table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _project_path(project_dir: Path, relative_path: str) -> Path | None:
    candidate = Path(relative_path)
    if not relative_path or candidate.is_absolute() or ".." in candidate.parts:
        return None
    root = project_dir.resolve()
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


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
