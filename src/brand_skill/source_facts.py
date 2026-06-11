"""Build traceable source fact candidates from source transcripts."""

from __future__ import annotations

import re
from pathlib import Path


def build_source_facts(project_dir: Path) -> None:
    transcripts_dir = project_dir / "converted_markdown" / "source_transcripts"
    if not transcripts_dir.exists():
        print("Missing source transcripts directory: converted_markdown/source_transcripts/")
        raise SystemExit(1)

    transcripts = sorted(transcripts_dir.glob("*.md"))
    if not transcripts:
        print("No source transcript Markdown found under converted_markdown/source_transcripts/.")
        raise SystemExit(1)

    facts_dir = project_dir / "converted_markdown" / "source_facts"
    facts_dir.mkdir(parents=True, exist_ok=True)
    for transcript in transcripts:
        facts_path = facts_dir / f"{transcript.stem}_source_facts.md"
        facts_path.write_text(_render_source_facts(transcript), encoding="utf-8")
    print(f"Source facts created: {facts_dir}")


def _render_source_facts(transcript_path: Path) -> str:
    text = transcript_path.read_text(encoding="utf-8")
    source_title = _first_heading(text) or transcript_path.stem
    source_name = source_title.split("｜", 1)[1].strip() if "｜" in source_title else source_title
    source_id = _first_metadata_value(text, "Source ID") or transcript_path.stem.split("_", 1)[0]
    source_number = re.sub(r"\D+", "", source_id) or "000"
    page_blocks = _page_blocks(text)

    lines = [
        f"# Source Facts｜{source_name}",
        "",
        "## 生成规则",
        "",
        "- 只从 `converted_markdown/source_transcripts/` 抽取来源资料中已经出现的文字。",
        "- 不做品牌确认判断，不做外发安全判断，不补写资料中没有的信息。",
        "- 每条候选事实必须保留 Source Anchor，后续语义编译和人工复核都应回到原始 transcript / 页面截图。",
        "",
        "## Source Metadata",
        "",
        f"- Source ID：{source_id}",
        f"- 原始文件：{source_name}",
        f"- Source Transcript：{transcript_path.name}",
        "",
        "## Fact Candidates",
        "",
        "| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |",
        "|---|---|---|---|---|",
    ]

    fact_index = 1
    for block in page_blocks:
        candidates = _fact_candidates(block["text"])
        if not candidates:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"SF{source_number}-{fact_index:03d}",
                        block["anchor"],
                        "待补充：本页未抽取到可用文字",
                        "待补充",
                        block["low_confidence"],
                    ]
                )
                + " |"
            )
            fact_index += 1
            continue
        for candidate in candidates:
            lines.append(
                "| "
                + " | ".join(
                    [
                        f"SF{source_number}-{fact_index:03d}",
                        block["anchor"],
                        _escape_table_cell(candidate),
                        "已从来源资料提取",
                        _escape_table_cell(block["low_confidence"]),
                    ]
                )
                + " |"
            )
            fact_index += 1

    lines.append("")
    return "\n".join(lines)


def _first_heading(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _first_metadata_value(text: str, label: str) -> str:
    pattern = re.compile(rf"^-\s*{re.escape(label)}：(.+)$", re.MULTILINE)
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def _page_blocks(text: str) -> list[dict[str, str]]:
    blocks: list[dict[str, str]] = []
    page_matches = list(re.finditer(r"^## Page\s+(.+)$", text, flags=re.MULTILINE))
    for index, match in enumerate(page_matches):
        start = match.end()
        end = page_matches[index + 1].start() if index + 1 < len(page_matches) else len(text)
        block_text = text[start:end]
        blocks.append(
            {
                "anchor": _first_metadata_value(block_text, "Source Anchor") or "待补充",
                "text": _extract_subsection(block_text, "Text"),
                "low_confidence": _low_confidence(block_text),
            }
        )
    return blocks


def _extract_subsection(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^###\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    next_heading = re.search(r"^###\s+", markdown[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(markdown)
    return markdown[match.end() : end].strip()


def _low_confidence(markdown: str) -> str:
    section = _extract_subsection(markdown, "Low Confidence / Need Review")
    for line in section.splitlines():
        stripped = line.strip().lstrip("-").strip()
        if stripped:
            return stripped
    return "待复核"


def _fact_candidates(text: str) -> list[str]:
    candidates: list[str] = []
    for line in text.splitlines():
        cleaned = _clean_evidence_line(line)
        if not cleaned:
            continue
        candidates.extend(_split_sentences(cleaned))
    return [candidate for candidate in candidates if candidate]


def _clean_evidence_line(line: str) -> str:
    cleaned = line.strip()
    if cleaned.startswith("#"):
        return ""
    cleaned = re.sub(r"^>\s*", "", cleaned)
    cleaned = re.sub(r"^[-*]\s+", "", cleaned)
    cleaned = re.sub(r"^\d+[.)、]\s*", "", cleaned)
    cleaned = cleaned.strip()
    if not cleaned or cleaned.startswith("|") or set(cleaned) <= {"-", ":"}:
        return ""
    return cleaned


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[。！？!?；;])\s+", text)
    return [part.strip() for part in parts if part.strip()]


def _escape_table_cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ").strip()
