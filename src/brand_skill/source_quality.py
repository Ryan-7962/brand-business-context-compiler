"""Generate a source recognition quality report from converted transcripts."""

from __future__ import annotations

import re
from pathlib import Path


def build_source_quality_report(project_dir: Path) -> Path:
    converted_dir = project_dir / "converted_markdown"
    transcripts_dir = converted_dir / "source_transcripts"
    if not transcripts_dir.exists():
        print("Missing source transcripts directory: converted_markdown/source_transcripts/")
        raise SystemExit(1)

    transcripts = sorted(transcripts_dir.glob("*.md"))
    if not transcripts:
        print("No source transcript Markdown found under converted_markdown/source_transcripts/.")
        raise SystemExit(1)

    page_rows = []
    for transcript in transcripts:
        page_rows.extend(_parse_transcript(transcript))

    review_rows = [row for row in page_rows if _needs_review(row)]
    report_path = converted_dir / "source_quality_report.md"
    report_path.write_text(_render_report(page_rows, review_rows), encoding="utf-8")
    print(f"Source quality report created: {report_path}")
    return report_path


def _parse_transcript(path: Path) -> list[dict[str, str | int]]:
    text = path.read_text(encoding="utf-8")
    source_title = _first_heading(text) or path.stem
    source_name = source_title.split("｜", 1)[1].strip() if "｜" in source_title else source_title
    rows = []
    for block in _page_blocks(text):
        rows.append(
            {
                "source_name": source_name,
                "anchor": _metadata_value(block, "Source Anchor") or "待补充",
                "text_chars": _metadata_int(block, "Extracted text chars"),
                "image_count": _metadata_int(block, "Embedded images detected"),
                "drawing_count": _metadata_int(block, "Vector drawings detected"),
                "table_count": _markdown_table_count(block),
                "low_confidence": _low_confidence(block),
            }
        )
    return rows


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _page_blocks(markdown: str) -> list[str]:
    matches = list(re.finditer(r"^## Page\s+.+$", markdown, flags=re.MULTILINE))
    blocks = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        blocks.append(markdown[start:end])
    return blocks


def _metadata_value(markdown: str, label: str) -> str:
    pattern = re.compile(rf"^-\s*{re.escape(label)}：(.+)$", re.MULTILINE)
    match = pattern.search(markdown)
    return match.group(1).strip() if match else ""


def _metadata_int(markdown: str, label: str) -> int:
    value = _metadata_value(markdown, label)
    match = re.search(r"\d+", value)
    return int(match.group(0)) if match else 0


def _markdown_table_count(markdown: str) -> int:
    lines = [line.strip() for line in markdown.splitlines()]
    count = 0
    index = 0
    while index < len(lines) - 1:
        if _looks_like_table_row(lines[index]) and _looks_like_separator(lines[index + 1]):
            count += 1
            index += 2
            while index < len(lines) and _looks_like_table_row(lines[index]):
                index += 1
            continue
        index += 1
    return count


def _looks_like_table_row(line: str) -> bool:
    return line.startswith("|") and line.endswith("|") and line.count("|") >= 2


def _looks_like_separator(line: str) -> bool:
    if not _looks_like_table_row(line):
        return False
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    return bool(cells) and all(cell and set(cell.replace(" ", "")) <= {"-", ":"} for cell in cells)


def _low_confidence(markdown: str) -> str:
    section = _extract_subsection(markdown, "Low Confidence / Need Review")
    for line in section.splitlines():
        stripped = line.strip().lstrip("-").strip()
        if stripped:
            return stripped
    return "待复核"


def _extract_subsection(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^###\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    next_heading = re.search(r"^###\s+", markdown[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(markdown)
    return markdown[match.end() : end].strip()


def _needs_review(row: dict[str, str | int]) -> bool:
    low_confidence = str(row["low_confidence"])
    return (
        _normalize_low_confidence(low_confidence) != "无明显低置信度"
        or int(row["text_chars"]) < 20
        or int(row["image_count"]) > 0
        or int(row["drawing_count"]) > 0
        or int(row["table_count"]) > 0
    )


def _normalize_low_confidence(text: str) -> str:
    return text.strip().rstrip("。.!！")


def _recommended_action(row: dict[str, str | int]) -> str:
    reasons = str(row["low_confidence"])
    if int(row["table_count"]) > 0 or "表格" in reasons:
        return "MinerU / MarkItDown / 人工复核"
    if int(row["image_count"]) > 0 or int(row["text_chars"]) < 20 or "图片" in reasons or "视觉" in reasons:
        return "OCR / MinerU / 人工复核"
    if "PowerPoint 轻量转写" in reasons:
        return "MinerU / 原 PPT 人工复核"
    return "人工复核"


def _render_report(page_rows: list[dict[str, str | int]], review_rows: list[dict[str, str | int]]) -> str:
    lines = [
        "# Source Quality Report",
        "",
        "## 识别质量总览",
        "",
        f"- 总页数：{len(page_rows)}",
        f"- 需要复核页数：{len(review_rows)}",
        "- 复核原则：优先处理含图片、低文字量、表格、小字或 OCR 不确定页面；关键品牌口径和关键数字必须回到原始页面确认。",
        "",
        "## 全部页面读取状态",
        "",
        "| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 读取状态 | 低置信度说明 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for row in page_rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(str(row["anchor"])),
                    _cell(str(row["source_name"])),
                    str(row["text_chars"]),
                    str(row["image_count"]),
                    str(row["drawing_count"]),
                    str(row["table_count"]),
                    "需要复核" if _needs_review(row) else "可进入后续编译",
                    _cell(str(row["low_confidence"])),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## 需要复核的页面",
            "",
            "| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 |",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    if not review_rows:
        lines.append("| - | - | - | - | - | - | 无明显低置信度页面 | 继续后续语义编译 |")
    else:
        for row in review_rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(str(row["anchor"])),
                        _cell(str(row["source_name"])),
                        str(row["text_chars"]),
                        str(row["image_count"]),
                        str(row["drawing_count"]),
                        str(row["table_count"]),
                        _cell(str(row["low_confidence"])),
                        _recommended_action(row),
                    ]
                )
                + " |"
            )
    lines.append("")
    return "\n".join(lines)


def _cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ").strip()
