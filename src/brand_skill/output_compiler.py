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
    review_items = _merge_review_items(
        _quality_review_items(review_rows),
        [
            {
                "Source Anchor": row.get("Source Anchor", "待补充"),
                "低置信度说明": _review_reason(row),
                "建议动作": "人工复核 / 补充业务信息",
            }
            for row in fact_rows
            if _row_needs_review(row)
        ],
    )
    first_fact = fact_rows[0]
    title = project_name
    profile = _infer_document_profile(fact_rows)
    outline = _build_marketing_outline(fact_rows)
    facts_table = "\n".join(
        f"| {row.get('Fact ID', '')} | {_cell(row.get('Evidence Text', ''))} | {row.get('Source Anchor', '')} | {row.get('信息状态', '已从来源资料提取')} | {'是' if _row_needs_review(row) else '否'} |"
        for row in fact_rows
    )
    source_table = "\n".join(
        f"| {row.get('来源编号', '')} | {_cell(row.get('原始文件', ''))} | {_source_summary(row, fact_rows)} | {row.get('原始文件创建时间', '待补充')} | {row.get('原始文件修改时间', '待补充')} | {row.get('转写 Markdown', '待补充')} | {_source_facts_path(row)} | {row.get('页码/Slide 范围', '待补充')} |"
        for row in source_rows
    )
    retrieval_table = _retrieval_table(source_rows, profile["reuse_scene"])
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
        f"| CA{index:03d} | {_asset_type_for_fact(row, profile['asset_type'])} | {_cell(row.get('Evidence Text', ''))} | {profile['reuse_scene']} | {row.get('Source Anchor', '')} | {row.get('信息状态', '已从来源资料提取')} | {'高' if _row_needs_review(row) else '中'} |"
        for index, row in enumerate(fact_rows[:10], start=1)
    )
    library_rows = "\n".join(
        f"| LCE{index:03d} | {_library_location_for_fact(row, profile['library_location'])} | {_short_title(row.get('Evidence Text', ''), index)} | {_cell(row.get('Evidence Text', ''))} | CA{index:03d} | 待验证 | 暂存 |"
        for index, row in enumerate(fact_rows[:5], start=1)
    )
    missing_lines = "\n".join(
        f"- {row.get('Source Anchor', '待补充')}：{row.get('低置信度说明', '待复核')}"
        for row in review_items
    ) or "- 暂未发现明显低置信度事项。"

    return {
        "00_source_index.md": f"# Source Index｜{title}\n\n| Source ID | 文件名 | 内容概述 | 创建时间 | 修改时间 | 转写 Markdown | Source Facts | 页/Slide 范围 |\n|---|---|---|---|---|---|---|---|\n{source_table}\n",
        "01_source_conversion_report.md": f"# Source Conversion Report｜{title}\n\n## 转换证据\n\n请参见 `converted_markdown/conversion_report.md`、`source_quality_report.md` 和 `source_version_report.md`。\n\n## 版本线索\n\n{_version_excerpt(version_summary)}\n",
        "02_document_profile.md": f"# Document Profile｜{title}\n\n## 0. 基础信息\n\n| 字段 | 内容 | 信息状态 | 来源/依据 | 待确认 |\n|---|---|---|---|---|\n| 文件类型 | {profile['document_type']} | AI 结构化转述，待确认 | {first_fact.get('Source Anchor', '待补充')} | 是 |\n| 文件目的 | {profile['document_purpose']} | AI 结构化转述，待确认 | {first_fact.get('Source Anchor', '待补充')} | 是 |\n| 目标读者 | {profile['audience']} | AI 结构化转述，待确认 | {first_fact.get('Source Anchor', '待补充')} | 是 |\n| 业务阶段 | {profile['business_stage']} | AI 结构化转述，待确认 | {first_fact.get('Source Anchor', '待补充')} | 是 |\n| 核心内容 | {_cell(first_fact.get('Evidence Text', '待补充'))} | 已从来源资料提取 | {first_fact.get('Source Anchor', '待补充')} | 否 |\n\n## 1. 类型识别依据\n\n{profile['rationale']}\n\n## 待人工确认问题\n\n{missing_lines}\n",
        "03_marketing_semantic_transcript.md": f"# Marketing Semantic Transcript｜{title}\n\n{page_sections}\n",
        "04_key_facts_and_claims.md": f"# Key Facts and Claims｜{title}\n\n## Key Facts\n\n| Fact ID | 事实 | 来源锚点 | 信息状态 | 待确认 |\n|---|---|---|---|---|\n{facts_table}\n",
        "05_strategy_and_execution_map.md": f"# Strategy and Execution Map｜{title}\n\n## {profile['document_type']} 结构化转述重点\n\n{profile['focus_points']}\n\n## 自动识别的大纲\n\n{_render_outline(outline)}\n\n## 来源事实驱动结构\n\n{_bullet_facts(fact_rows)}\n\n## 待补充\n\n{missing_lines}\n",
        "06_risk_and_review_items.md": f"# Risk and Review Items｜{title}\n\n| Review ID | 审核项 | 风险等级 | 来源锚点 | 建议 |\n|---|---|---|---|---|\n{review_table or '| R000 | 暂无明显风险 | 低 | 待补充 | 继续后续编译 |'}\n",
        "07_ai_ready_marketing_brief_base.md": f"# AI Ready Marketing Brief Base｜{title}\n\n## Source-backed Context\n\n{_bullet_facts(fact_rows[:8])}\n\n## 自动识别的大纲\n\n{_render_outline(outline)}\n\n## 使用限制\n\n- 不把待确认内容写成品牌方已经确认的口径。\n- 不补写来源资料中没有的信息。\n",
        "08_review_pack.md": f"# Review Pack｜{title}\n\n## 需要人工处理\n\n{missing_lines}\n",
        "09_quality_check_report.md": f"# Quality Check Report｜{title}\n\n## 自动检查\n\n- Source facts：{len(facts)} 条。\n- Source pages：{len(pages)} 页/段。\n- 待复核事项：{len(review_items)} 项。\n- 大纲分类：{_outline_category_count(outline)} 类。\n\n## 结论\n\n这是确定性初稿，可进入人工复核或模型精修。\n",
        "10_context_asset_index.md": f"# Context Asset Index｜{title}\n\n| Asset ID | 上下文类型 | 可复用资产 | 适用场景 | 来源锚点 | 信息状态 | Review Priority |\n|---|---|---|---|---|---|---|\n{asset_rows}\n",
        "11_context_library_update_plan.md": f"# Context Library Update Plan｜{title}\n\n## 1. Library Update Summary\n\n| Source Package | Update Type | Recommended Action | Reason |\n|---|---|---|---|\n| {title} | 新增 | 暂存待复核 | 由 source facts 确定性生成，需人工确认后长期沉淀 |\n\n## 2. New Context Entries\n\n| Entry ID | 建议归档位置 | 标题 | 内容摘要 | 来源资产 | 稳定性 | 写入建议 |\n|---|---|---|---|---|---|---|\n{library_rows}\n\n## 3. Existing Context Updates\n\n| 可能影响的已有条目 | 更新方式 | 新信息 | 冲突或风险 | 版本判断依据 |\n|---|---|---|---|---|\n| 待检索 | 补充 | 来源事实可补充长期库 | 需人工判断是否与旧知识冲突 | source_version_report.md |\n\n## 4. Do Not Promote\n\n- 不把待确认、低置信度或临时执行信息直接提升为长期知识。\n\n## 6. Retrieval Notes\n\n后续 brief 可调用本资料中已保留原文定位的事实，但必须回到 source facts 和 transcript 校验。\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n{retrieval_table}\n",
    }


def _source_facts_path(row: dict[str, str]) -> str:
    transcript_path = row.get("转写 Markdown", "").strip()
    if not transcript_path.endswith(".md"):
        return "converted_markdown/source_facts/"
    transcript = Path(transcript_path)
    return f"converted_markdown/source_facts/{transcript.stem}_source_facts.md"


def _source_summary(source_row: dict[str, str], fact_rows: list[dict[str, str]]) -> str:
    source_id = source_row.get("来源编号", "")
    evidence = [
        row.get("Evidence Text", "").strip()
        for row in fact_rows
        if row.get("Source Anchor", "").startswith(f"{source_id}#") and row.get("Evidence Text", "").strip()
    ]
    if not evidence:
        return "待补充"
    return _cell("；".join(evidence[:2]))


def _retrieval_table(source_rows: list[dict[str, str]], reuse_scene: str) -> str:
    return "\n".join(
        f"| {reuse_scene} | outputs/10_context_asset_index.md | {_source_facts_path(row)} | {row.get('转写 Markdown', 'converted_markdown/source_transcripts/')} |"
        for row in source_rows
    )


def _needs_review(text: str) -> bool:
    normalized = text.strip().rstrip("。.!！")
    if not normalized or normalized.startswith("无明显低置信度"):
        return False
    return True


def _row_needs_review(row: dict[str, str]) -> bool:
    return _needs_review(row.get("低置信度说明", "")) or _evidence_mentions_missing_context(row.get("Evidence Text", ""))


def _review_reason(row: dict[str, str]) -> str:
    low_confidence = row.get("低置信度说明", "").strip()
    if _needs_review(low_confidence):
        return low_confidence
    evidence = row.get("Evidence Text", "").strip()
    if _evidence_mentions_missing_context(evidence):
        return f"来源文本提示信息缺口：{evidence}"
    return low_confidence or "待复核"


def _evidence_mentions_missing_context(text: str) -> bool:
    markers = [
        "未提供",
        "暂未提供",
        "没有提供",
        "缺少",
        "缺失",
        "待补充",
        "需要补充",
        "需补充",
        "待确认",
    ]
    return any(marker in text for marker in markers)


def _merge_review_items(*item_groups: list[dict[str, str]]) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for items in item_groups:
        for item in items:
            anchor = item.get("Source Anchor", "待补充")
            reason = item.get("低置信度说明", "待复核")
            key = (anchor, reason)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
    return merged


def _quality_review_items(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for row in rows:
        reason = row.get("低置信度说明", "")
        action = row.get("建议动作", "")
        if _needs_review(reason) or any(marker in action for marker in ["OCR", "MinerU", "人工复核", "复核", "补充"]):
            items.append(row)
    return items


def _infer_document_profile(facts: list[dict[str, str]]) -> dict[str, str]:
    text = " ".join(row.get("Evidence Text", "") for row in facts).lower()
    rules = [
        (
            ["竞品", "竞对", "竞争", "对标", "battlecard", "benchmark"],
            {
                "document_type": "竞品 / 市场对标资料",
                "document_purpose": "沉淀竞品动态、对标维度和市场参考",
                "audience": "品牌团队、市场团队、销售团队、内容团队",
                "business_stage": "市场观察 / 竞品研究",
                "library_location": "network",
                "asset_type": "market_signal",
                "reuse_scene": "竞品分析 / 销售话术 / 内容策略 / 市场观察",
                "focus_points": "- 抽取可证实的竞品事实、渠道表现、价格带和传播打法。\n- 区分公开事实、内部判断和待确认推断。\n- 不把竞品攻击表达直接变成可外发口径。",
                "rationale": "- 命中“竞品 / 竞对 / 竞争 / 对标 / battlecard / benchmark”等来源词，因此暂判为竞品 / 市场对标资料。",
            },
        ),
        (
            ["复盘", "总结", "表现", "转化", "经验教训", "投放"],
            {
                "document_type": "投放复盘",
                "document_purpose": "总结表现、提炼经验和指导后续优化",
                "audience": "品牌团队、投放团队、内容团队、管理层",
                "business_stage": "复盘 / 优化",
                "library_location": "case",
                "asset_type": "case",
                "reuse_scene": "复盘 / 投放优化 / 案例复用",
                "focus_points": "- 先提炼表现结论和有效做法。\n- 标出失败点、风险和后续优化动作。\n- 不把阶段性表现直接升级为长期品牌口径。",
                "rationale": "- 命中“复盘 / 表现 / 转化 / 经验教训 / 投放”等来源词，因此暂判为投放复盘。",
            },
        ),
        (
            ["新品", "上市", "首发", "上新", "launch", "gtm", "go-to-market"],
            {
                "document_type": "新品上市 / GTM 方案",
                "document_purpose": "组织新品上市节奏、核心信息、渠道动作和内容承接",
                "audience": "品牌团队、销售团队、渠道团队、内容团队、代理商",
                "business_stage": "上市准备 / GTM 执行",
                "library_location": "project",
                "asset_type": "project",
                "reuse_scene": "上市 brief / PDP / GEO / 种草 / 销售沟通",
                "focus_points": "- 抽取上市目标、核心信息、渠道节奏、内容资产和销售承接。\n- 标出未确认的卖点证据、排期、渠道资源和审核边界。\n- 不把未确认新品 claim 写成已品牌确认。",
                "rationale": "- 命中“新品 / 上市 / 首发 / 上新 / launch / GTM”等来源词，因此暂判为新品上市 / GTM 方案。",
            },
        ),
        (
            ["活动", "活动目标", "campaign", "提案", "big idea", "传播", "社媒", "触点"],
            {
                "document_type": "活动方案 / 广告提案",
                "document_purpose": "组织传播策略、创意主线、触点和内容资产",
                "audience": "品牌团队、代理商、内容团队、渠道团队",
                "business_stage": "提案 / 立项 / 执行准备",
                "library_location": "project",
                "asset_type": "project",
                "reuse_scene": "GEO / 种草 / 拍摄 / 活动执行",
                "focus_points": "- 抽取目标、洞察、创意主线、渠道触点和内容资产。\n- 标出预算、排期、资源和审核边界缺口。",
                "rationale": "- 命中“活动 / campaign / 提案 / 传播 / 社媒 / 触点”等来源词，因此暂判为活动方案 / 广告提案。",
            },
        ),
        (
            ["会议", "纪要", "决策", "负责人", "下周动作", "对齐"],
            {
                "document_type": "会议纪要",
                "document_purpose": "记录决策、待办、责任人和后续动作",
                "audience": "品牌团队、项目负责人、协作团队、管理层",
                "business_stage": "会议对齐 / 决策同步",
                "library_location": "decision",
                "asset_type": "decision",
                "reuse_scene": "决策追踪 / 项目推进 / 会议复盘",
                "focus_points": "- 优先抽取决策、被否方向、责任人和下一步动作。\n- 区分已决定事项、待确认事项和讨论信息。\n- 不把会议讨论直接写成已品牌确认。",
                "rationale": "- 命中“会议 / 纪要 / 决策 / 负责人 / 下周动作”等来源词，因此暂判为会议纪要。",
            },
        ),
        (
            ["销售", "经销商", "渠道", "门店", "终端", "ka"],
            {
                "document_type": "销售 / 渠道策略",
                "document_purpose": "推进渠道执行、销售协同或终端落地",
                "audience": "销售团队、渠道团队、经销商、品牌团队",
                "business_stage": "渠道推进 / 销售执行",
                "library_location": "project",
                "asset_type": "project",
                "reuse_scene": "销售 brief / 渠道沟通 / 终端执行",
                "focus_points": "- 抽取渠道动作、销售话术、资源配置和执行约束。\n- 临时政策、激励和敏感执行信息不得直接入长期库。",
                "rationale": "- 命中“销售 / 经销商 / 渠道 / 门店 / 终端”等来源词，因此暂判为销售 / 渠道策略。",
            },
        ),
        (
            ["产品", "培训", "sku", "卖点", "功效", "包装"],
            {
                "document_type": "产品培训 / 产品资料",
                "document_purpose": "解释产品信息、卖点、证据和使用边界",
                "audience": "品牌团队、销售团队、客服团队、内容团队",
                "business_stage": "培训 / 产品知识沉淀",
                "library_location": "product",
                "asset_type": "product",
                "reuse_scene": "PDP / 销售 / 客服 / 种草",
                "focus_points": "- 抽取产品事实、卖点、证据和适用边界。\n- 没有证据的功效表达必须进入待确认。",
                "rationale": "- 命中“产品 / 培训 / SKU / 卖点 / 功效 / 包装”等来源词，因此暂判为产品培训 / 产品资料。",
            },
        ),
    ]
    for keywords, profile in rules:
        minimum_hits = 2 if profile["document_type"] == "竞品 / 市场对标资料" else 1
        if _keyword_hit_count(text, keywords) >= minimum_hits:
            return profile
    return {
        "document_type": "综合营销资料",
        "document_purpose": "沉淀可复用品牌和业务上下文",
        "audience": "品牌团队、营销团队、相关业务团队",
        "business_stage": "资料沉淀 / 上下文编译",
        "library_location": "project",
        "asset_type": "project",
        "reuse_scene": "后续 brief / 知识库检索",
        "focus_points": "- 先保留来源事实和页面锚点。\n- 再由人工或模型进一步判断资料类型、业务阶段和长期复用价值。",
        "rationale": "- 未命中明确资料类型关键词，因此暂判为综合营销资料。",
    }


def _keyword_hit_count(text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword in text)


def _build_marketing_outline(facts: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    outline = {
        "目标 / 要解决的问题": [],
        "表格结构信息": [],
        "渠道 / 触点 / 场景": [],
        "下一步动作 / 执行要求": [],
        "缺口 / 待补充": [],
        "其他来源事实": [],
    }
    rules = [
        ("缺口 / 待补充", ["缺少", "缺失", "暂未提供", "待补充", "未提供", "没有"]),
        ("下一步动作 / 执行要求", ["下一步", "动作", "负责人", "排期", "执行", "补充", "优化"]),
        ("渠道 / 触点 / 场景", ["渠道", "触点", "线下", "社媒", "电商", "门店", "场景", "达人"]),
        ("目标 / 要解决的问题", ["目标", "希望", "建立", "提升", "解决", "心智", "目的"]),
    ]
    for row in facts:
        evidence = row.get("Evidence Text", "")
        target = "表格结构信息" if _is_table_fact(row) else "其他来源事实"
        if target == "其他来源事实":
            for category, keywords in rules:
                if any(keyword in evidence for keyword in keywords):
                    target = category
                    break
        outline[target].append(row)
    return outline


def _render_outline(outline: dict[str, list[dict[str, str]]]) -> str:
    sections = []
    for category, rows in outline.items():
        if not rows:
            continue
        sections.append(f"### {category}")
        sections.append("")
        sections.append(_bullet_facts(rows))
        sections.append("")
    return "\n".join(sections).strip() or "### 其他来源事实\n\n- 待补充。"


def _outline_category_count(outline: dict[str, list[dict[str, str]]]) -> int:
    return sum(1 for rows in outline.values() if rows)


def _cell(text: str) -> str:
    return _clean_inline(text).replace("|", "/")


def _clean_inline(text: str) -> str:
    return " ".join(str(text).split()).strip()


def _short_title(text: str, index: int) -> str:
    cleaned = _clean_inline(text)
    return cleaned[:24] or f"Context Entry {index:03d}"


def _bullet_facts(facts: list[dict[str, str]]) -> str:
    return "\n".join(f"- {row.get('Evidence Text', '待补充')}（来源：{row.get('Source Anchor', '待补充')}）" for row in facts) or "- 待补充。"


def _asset_type_for_fact(row: dict[str, str], default: str) -> str:
    return "structured_table" if _is_table_fact(row) else default


def _library_location_for_fact(row: dict[str, str], default: str) -> str:
    return "structured_table" if _is_table_fact(row) else default


def _is_table_fact(row: dict[str, str]) -> bool:
    return row.get("Evidence Text", "").strip().startswith("表格行：")


def _version_excerpt(markdown: str) -> str:
    if not markdown.strip():
        return "- 暂无版本报告。"
    lines = [line for line in markdown.splitlines() if "疑似多版本组数" in line or "最新修改时间线索" in line or "不自动覆盖" in line]
    return "\n".join(lines) or "- 已生成版本报告。"
