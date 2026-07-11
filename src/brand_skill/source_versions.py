"""Report likely source file versions and update-review clues."""

from __future__ import annotations

import re
from pathlib import Path


def build_source_version_report(project_dir: Path) -> Path:
    converted_dir = project_dir / "converted_markdown"
    conversion_report = converted_dir / "conversion_report.md"
    if not conversion_report.exists():
        print("Missing source conversion report: converted_markdown/conversion_report.md")
        raise SystemExit(1)

    rows = _parse_conversion_report(conversion_report.read_text(encoding="utf-8"))
    if not rows:
        print("No source rows found in converted_markdown/conversion_report.md.")
        raise SystemExit(1)

    groups = _likely_version_groups(rows)
    report_path = converted_dir / "source_version_report.md"
    report_path.write_text(_render_report(rows, groups), encoding="utf-8")
    print(f"Source version report created: {report_path}")
    return report_path


def _parse_conversion_report(markdown: str) -> list[dict[str, str]]:
    table_lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 3:
        return []

    rows: list[dict[str, str]] = []
    seen_sources: set[tuple[str, str, str]] = set()
    index = 0
    while index < len(table_lines) - 2:
        headers = _split_row(table_lines[index])
        separator = _split_row(table_lines[index + 1])
        if "来源编号" in headers and "原始文件" in headers and _is_separator(separator):
            for row_line in table_lines[index + 2 :]:
                cells = _split_row(row_line)
                if len(cells) != len(headers):
                    break
                row = dict(zip(headers, cells))
                parsed_row = {
                    "source_id": row.get("来源编号", "").strip(),
                    "file_name": row.get("原始文件", "").strip(),
                    "created_at": row.get("原始文件创建时间", "").strip() or "待补充",
                    "modified_at": row.get("原始文件修改时间", "").strip() or "待补充",
                    "transcript": row.get("转写 Markdown", "").strip() or "待补充",
                    "external_source": row.get("外部来源", "").strip() or "-",
                }
                source_key = (
                    parsed_row["source_id"],
                    parsed_row["file_name"],
                    parsed_row["transcript"],
                )
                if source_key not in seen_sources:
                    seen_sources.add(source_key)
                    rows.append(parsed_row)
            break
        index += 1
    return [row for row in rows if row["source_id"] and row["file_name"]]


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(set(cell.replace(" ", "")) <= {"-", ":"} for cell in cells)


def _likely_version_groups(rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        key = _normalize_version_key(row["file_name"])
        grouped.setdefault(key, []).append(row)
    return {key: value for key, value in grouped.items() if len(value) > 1}


def _normalize_version_key(file_name: str) -> str:
    stem = Path(file_name).stem.lower()
    stem = re.sub(r"[\s\-]+", "_", stem)
    stem = re.sub(r"(?i)(?:^|_)(?:final|draft|revised|修订版|终版|定稿)\d{0,8}(?=_|$)", "_", stem)
    stem = re.sub(r"(?i)(?:^|_)(?:v|ver|version)[_ ]?\d+(?:\.\d+)?(?=_|$)", "_", stem)
    stem = re.sub(r"(?:^|_)(?:20\d{2}|19\d{2})(?:[._-]?\d{1,2}){0,2}(?=_|$)", "_", stem)
    stem = re.sub(r"(?:^|_)(?:\d{4}|\d{6}|\d{8})(?=_|$)", "_", stem)
    stem = re.sub(r"(?i)(?:^|_)(?:copy|副本|备份|最新版|更新版)(?:_\d+)?(?=_|$)", "_", stem)
    stem = re.sub(r"(?i)(?:^|_)[a-f0-9]{8,}(?=_|$)", "_", stem)
    stem = stem.replace("生意进度会", "生意会")
    stem = re.sub(r"(?:品牌|整合版|汇总版)", "", stem)
    stem = re.sub(r"_{2,}", "_", stem).strip("_")
    return stem or Path(file_name).stem.lower()


def _render_report(rows: list[dict[str, str]], groups: dict[str, list[dict[str, str]]]) -> str:
    lines = [
        "# Source Version Report",
        "",
        "## 版本线索总览",
        "",
        f"- 来源文件数：{len(rows)}",
        f"- 疑似多版本组数：{len(groups)}",
        "- 最新修改时间线索：优先作为版本判断依据，但不自动覆盖已有品牌知识。",
        "- 处理原则：同主题多版本资料进入更新/冲突复核队列，由使用者确认后再沉淀为长期知识。",
        "",
        "## 疑似多版本资料",
        "",
    ]
    if not groups:
        lines.append("- 暂未发现基于文件名的疑似多版本资料。")
        lines.append("")
        return "\n".join(lines)

    for key, group_rows in sorted(groups.items()):
        sorted_rows = sorted(group_rows, key=lambda row: row["modified_at"])
        latest = sorted_rows[-1]
        lines.extend(
            [
                f"### {key}",
                "",
                f"- 最新修改时间线索：{latest['source_id']} / {latest['file_name']} / {latest['modified_at']}",
                "- 建议动作：进入更新/冲突复核队列；不自动覆盖旧知识。",
                "",
                "| 来源编号 | 原始文件 | 创建时间 | 修改时间 | 转写稿 | 外部来源 |",
                "|---|---|---|---|---|---|",
            ]
        )
        for row in sorted_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(row["source_id"]),
                        _cell(row["file_name"]),
                        _cell(row["created_at"]),
                        _cell(row["modified_at"]),
                        _cell(row["transcript"]),
                        _cell(row["external_source"]),
                    ]
                )
                + " |"
            )
        lines.append("")
    return "\n".join(lines)


def _cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ").strip()
