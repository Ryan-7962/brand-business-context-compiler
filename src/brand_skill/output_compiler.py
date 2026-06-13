"""Deterministically compile first-pass structured outputs from source evidence."""

from __future__ import annotations

import re
from pathlib import Path

from .workflow import OUTPUT_FILES


def compile_structured_outputs(project_dir: Path, keep_existing: bool = False) -> None:
    converted_dir = project_dir / "converted_markdown"
    facts = _load_facts(converted_dir / "source_facts")
    pages = _load_pages(converted_dir / "source_transcripts")
    sources = _load_sources(converted_dir / "conversion_report.md")
    review_rows = _load_quality_rows(converted_dir / "source_quality_report.md")
    version_summary = _read_optional(converted_dir / "source_version_report.md")

    outputs = project_dir / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    documents = _build_documents(project_dir.name or "Compiled Source Package", facts, pages, sources, review_rows, version_summary)
    for filename in OUTPUT_FILES:
        path = outputs / filename
        if keep_existing and path.exists() and path.read_text(encoding="utf-8").strip():
            continue
        path.write_text(documents.get(filename, f"# {filename}\n\n待补充。\n"), encoding="utf-8")
    print(f"Structured outputs compiled: {outputs}")


def _load_facts(facts_dir: Path) -> list[dict[str, str]]:
    if not facts_dir.exists():
        return []
    rows: list[dict[str, str]] = []
    for path in sorted(facts_dir.glob("*.md")):
        rows.extend(_parse_table_rows(path.read_text(encoding="utf-8")))
    return [
        row
        for row in rows
        if row.get("Fact ID") and row.get("Source Anchor") and row.get("Evidence Text")
    ]


def _load_pages(transcripts_dir: Path) -> list[dict[str, str]]:
    if not transcripts_dir.exists():
        return []
    pages = []
    for path in sorted(transcripts_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for block in _page_blocks(text):
            pages.append(
                {
                    "anchor": _metadata_value(block, "Source Anchor") or "待补充",
                    "text": _section_after_heading(block, "Text"),
                    "low_confidence": _section_after_heading(block, "Low Confidence / Need Review") or "无明显低置信度。",
                }
            )
    return pages


def _load_sources(report_path: Path) -> list[dict[str, str]]:
    if not report_path.exists():
        return []
    return [
        row
        for row in _parse_table_rows(report_path.read_text(encoding="utf-8"))
        if row.get("来源编号") and row.get("原始文件")
    ]


def _load_quality_rows(report_path: Path) -> list[dict[str, str]]:
    if not report_path.exists():
        return []
    return [
        row
        for row in _parse_table_rows(report_path.read_text(encoding="utf-8"))
        if row.get("Source Anchor") and row.get("低置信度说明")
    ]


def _parse_table_rows(markdown: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    rows: list[dict[str, str]] = []
    index = 0
    while index < len(lines) - 1:
        header = _split_row(lines[index])
        separator = _split_row(lines[index + 1])
        if not _is_separator(separator):
            index += 1
            continue
        for row_line in lines[index + 2 :]:
            cells = _split_row(row_line)
            if len(cells) != len(header):
                break
            rows.append(dict(zip(header, cells)))
        index += 1
    return rows


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(set(cell.replace(" ", "")) <= {"-", ":"} for cell in cells)


def _page_blocks(markdown: str) -> list[str]:
    matches = list(re.finditer(r"^## Page\s+.+$", markdown, flags=re.MULTILINE))
    blocks = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        blocks.append(markdown[match.end() : end])
    return blocks


def _metadata_value(markdown: str, label: str) -> str:
    match = re.search(rf"^-\s*{re.escape(label)}：(.+)$", markdown, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def _section_after_heading(markdown: str, heading: str) -> str:
    match = re.search(rf"^###\s+{re.escape(heading)}\s*$", markdown, flags=re.MULTILINE)
    if not match:
        return ""
    next_heading = re.search(r"^###\s+", markdown[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(markdown)
    return markdown[match.end() : end].strip()


def _read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _build_documents(
    project_name: str,
    facts: list[dict[str, str]],
    pages: list[dict[str, str]],
    sources: list[dict[str, str]],
    review_rows: list[dict[str, str]],
    version_summary: str,
) -> dict[str, str]:
    fact_rows = facts or [{"Fact ID": "SF000-001", "Source Anchor": "待补充", "Evidence Text": "待补充", "信息状态": "待补充", "低置信度说明": "待补充"}]
    page_rows = pages or [{"anchor": row.get("Source Anchor", "待补充"), "text": row.get("Evidence Text", ""), "low_confidence": row.get("低置信度说明", "")} for row in fact_rows]
    source_rows = sources or [{"来源编号": "S001", "原始文件": "待补充", "原始文件创建时间": "待补充", "原始文件修改时间": "待补充", "页码/Slide 范围": "待补充"}]
    review_items = review_rows or [
        {"Source Anchor": row.get("Source Anchor", "待补充"), "低置信度说明": row.get("低置信度说明", "待复核"), "建议动作": "人工复核"}
        for row in fact_rows
        if _needs_review(row.get("低置信度说明", ""))
    ]
    first_fact = fact_rows[0]
    title = project_name
    facts_table = "\n".join(
        f"| {row.get('Fact ID', '')} | {_cell(row.get('Evidence Text', ''))} | {row.get('Source Anchor', '')} | {row.get('信息状态', '已从来源资料提取')} | {'是' if _needs_review(row.get('低置信度说明', '')) else '否'} |"
        for row in fact_rows
    )
    source_table = "\n".join(
        f"| {row.get('来源编号', '')} | {_cell(row.get('原始文件', ''))} | {row.get('原始文件创建时间', '待补充')} | {row.get('原始文件修改时间', '待补充')} | {row.get('页码/Slide 范围', '待补充')} |"
        for row in source_rows
    )
    page_sections = "\n\n".join(
        "\n".join(
            [
                f"## Page / Slide {index}",
                "",
                f"- Source Anchor：{page.get('anchor', '待补充')}",
                f"- 低置信度说明：{_clean_inline(page.get('low_confidence', '') or '无明显低置信度。')}",
                "",
                "### 原页核心内容转述",
                "",
                page.get("text", "").strip() or "待补充。",
            ]
        )
        for index, page in enumerate(page_rows, start=1)
    )
    review_table = "\n".join(
        f"| R{index:03d} | {_cell(row.get('低置信度说明', '待复核'))} | 中 | {row.get('Source Anchor', '待补充')} | {row.get('建议动作', '人工复核')} |"
        for index, row in enumerate(review_items, start=1)
    )
    asset_rows = "\n".join(
        f"| CA{index:03d} | project | {_cell(row.get('Evidence Text', ''))} | 后续 brief / 知识库检索 | {row.get('Source Anchor', '')} | {row.get('信息状态', '已从来源资料提取')} | {'高' if _needs_review(row.get('低置信度说明', '')) else '中'} |"
        for index, row in enumerate(fact_rows[:10], start=1)
    )
    library_rows = "\n".join(
        f"| LCE{index:03d} | project | {_short_title(row.get('Evidence Text', ''), index)} | {_cell(row.get('Evidence Text', ''))} | CA{index:03d} | 待验证 | 暂存 |"
        for index, row in enumerate(fact_rows[:5], start=1)
    )
    missing_lines = "\n".join(
        f"- {row.get('Source Anchor', '待补充')}：{row.get('低置信度说明', '待复核')}"
        for row in review_items
    ) or "- 暂未发现明显低置信度事项。"

    return {
        "00_source_index.md": f"# Source Index｜{title}\n\n| Source ID | 文件名 | 创建时间 | 修改时间 | 页/Slide 范围 |\n|---|---|---|---|---|\n{source_table}\n",
        "01_source_conversion_report.md": f"# Source Conversion Report｜{title}\n\n## 转换证据\n\n请参见 `converted_markdown/conversion_report.md`、`source_quality_report.md` 和 `source_version_report.md`。\n\n## 版本线索\n\n{_version_excerpt(version_summary)}\n",
        "02_document_profile.md": f"# Document Profile｜{title}\n\n## 0. 基础信息\n\n| 字段 | 内容 | 信息状态 | 来源/依据 | 待确认 |\n|---|---|---|---|---|\n| 文件类型 | 待分类营销资料 | AI 结构化转述，待确认 | {first_fact.get('Source Anchor', '待补充')} | 是 |\n| 核心内容 | {_cell(first_fact.get('Evidence Text', '待补充'))} | 已从来源资料提取 | {first_fact.get('Source Anchor', '待补充')} | 否 |\n\n## 待人工确认问题\n\n{missing_lines}\n",
        "03_marketing_semantic_transcript.md": f"# Marketing Semantic Transcript｜{title}\n\n{page_sections}\n",
        "04_key_facts_and_claims.md": f"# Key Facts and Claims｜{title}\n\n## Key Facts\n\n| Fact ID | 事实 | 来源锚点 | 信息状态 | 待确认 |\n|---|---|---|---|---|\n{facts_table}\n",
        "05_strategy_and_execution_map.md": f"# Strategy and Execution Map｜{title}\n\n## 来源事实驱动结构\n\n{_bullet_facts(fact_rows)}\n\n## 待补充\n\n{missing_lines}\n",
        "06_risk_and_review_items.md": f"# Risk and Review Items｜{title}\n\n| Review ID | 审核项 | 风险等级 | 来源锚点 | 建议 |\n|---|---|---|---|---|\n{review_table or '| R000 | 暂无明显风险 | 低 | 待补充 | 继续后续编译 |'}\n",
        "07_ai_ready_marketing_brief_base.md": f"# AI Ready Marketing Brief Base｜{title}\n\n## Source-backed Context\n\n{_bullet_facts(fact_rows[:8])}\n\n## 使用限制\n\n- 不把待确认内容写成已品牌确认。\n- 不补写来源资料中没有的信息。\n",
        "08_review_pack.md": f"# Review Pack｜{title}\n\n## 需要人工处理\n\n{missing_lines}\n",
        "09_quality_check_report.md": f"# Quality Check Report｜{title}\n\n## 自动检查\n\n- Source facts：{len(facts)} 条。\n- Source pages：{len(pages)} 页/段。\n- 待复核事项：{len(review_items)} 项。\n\n## 结论\n\n这是确定性初稿，可进入人工复核或模型精修。\n",
        "10_context_asset_index.md": f"# Context Asset Index｜{title}\n\n| Asset ID | 上下文类型 | 可复用资产 | 适用场景 | 来源锚点 | 信息状态 | Review Priority |\n|---|---|---|---|---|---|---|\n{asset_rows}\n",
        "11_context_library_update_plan.md": f"# Context Library Update Plan｜{title}\n\n## 1. Library Update Summary\n\n| Source Package | Update Type | Recommended Action | Reason |\n|---|---|---|---|\n| {title} | 新增 | 暂存待复核 | 由 source facts 确定性生成，需人工确认后长期沉淀 |\n\n## 2. New Context Entries\n\n| Entry ID | 建议归档位置 | 标题 | 内容摘要 | 来源资产 | 稳定性 | 写入建议 |\n|---|---|---|---|---|---|---|\n{library_rows}\n\n## 3. Existing Context Updates\n\n| 可能影响的已有条目 | 更新方式 | 新信息 | 冲突或风险 | 版本判断依据 |\n|---|---|---|---|---|\n| 待检索 | 补充 | 来源事实可补充长期库 | 需人工判断是否与旧知识冲突 | source_version_report.md |\n\n## 4. Do Not Promote\n\n- 不把待确认、低置信度或临时执行信息直接提升为长期知识。\n\n## 6. Retrieval Notes\n\n后续 brief 可调用本资料中已保留来源锚点的事实，但必须回到 source facts 和 transcript 校验。\n",
    }


def _needs_review(text: str) -> bool:
    normalized = text.strip().rstrip("。.!！")
    return bool(normalized and normalized != "无明显低置信度")


def _cell(text: str) -> str:
    return _clean_inline(text).replace("|", "/")


def _clean_inline(text: str) -> str:
    return " ".join(str(text).split()).strip()


def _short_title(text: str, index: int) -> str:
    cleaned = _clean_inline(text)
    return cleaned[:24] or f"Context Entry {index:03d}"


def _bullet_facts(facts: list[dict[str, str]]) -> str:
    return "\n".join(f"- {row.get('Evidence Text', '待补充')}（来源：{row.get('Source Anchor', '待补充')}）" for row in facts) or "- 待补充。"


def _version_excerpt(markdown: str) -> str:
    if not markdown.strip():
        return "- 暂无版本报告。"
    lines = [line for line in markdown.splitlines() if "疑似多版本组数" in line or "最新修改时间线索" in line or "不自动覆盖" in line]
    return "\n".join(lines) or "- 已生成版本报告。"
