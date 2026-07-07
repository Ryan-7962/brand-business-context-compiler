"""Build a local scorecard for comparing direct AI reading with the Skill workflow."""

from __future__ import annotations

from pathlib import Path


def build_value_benchmark(project_dir: Path, library_dir: Path | None = None) -> Path:
    """Create a benchmark template that tests whether the Skill adds real value."""
    evaluation_dir = project_dir / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    report_path = evaluation_dir / "direct_vs_skill_benchmark.md"
    report_path.write_text(_render_report(project_dir, library_dir), encoding="utf-8")
    print(f"Direct PDF/PPT vs Skill benchmark created: {report_path}")
    return report_path


def _render_report(project_dir: Path, library_dir: Path | None) -> str:
    converted = project_dir / "converted_markdown"
    outputs = project_dir / "outputs"
    review_page = project_dir / "review" / "brand_review.html"
    resolved_library = library_dir or (project_dir / "brand_context_library")
    library_report = resolved_library / "library_report.html"
    retrieval_map = resolved_library / "retrieval_maps" / "source_packages.md"

    facts_count = _count_fact_rows(converted / "source_facts")
    output_count = len(list(outputs.glob("*.md"))) if outputs.exists() else 0
    quality_text = _read_optional(converted / "source_quality_report.md")
    total_pages = _metric_value(quality_text, "总页数")
    review_pages = _metric_value(quality_text, "需要复核页数")
    library_entries = _count_library_entries(resolved_library)
    retrieval_notes = _count_retrieval_rows(retrieval_map)
    quality_samples = _quality_sample_rows(quality_text)
    quality_status = "存在" if (converted / "source_quality_report.md").exists() else "缺失"
    version_status = "存在" if (converted / "source_version_report.md").exists() else "缺失"
    review_status = "存在" if review_page.exists() else "缺失"
    library_status = "存在" if library_report.exists() else "缺失"

    return "\n".join(
        [
            "# Direct PDF/PPT vs Skill Benchmark",
            "",
            "## 评估目的",
            "",
            "这份 benchmark 用来验证本项目是否真的比“直接把原始 PDF/PPT 发给 AI”更有价值。这份 benchmark 不证明 Skill 一定更好，只提供同一批资料下的可比问题、评分维度和证据记录。",
            "",
            "## 对比对象",
            "",
            "- A：直接把原始 PDF/PPT 发给 AI，让 AI 直接总结和回答问题。",
            "- B：先经 Skill 转写、抽 facts、编译、入库后再回答同样问题。",
            "",
            "## 固定问题集",
            "",
            "1. 这个资料大概讲什么？",
            "2. 哪些内容被完整转写了？",
            "3. 哪些页面/图片/表格/小字识别不可靠？",
            "4. 哪些事实来自原文，来源在哪里？",
            "5. 哪些内容可以长期进入品牌知识库？",
            "6. 哪些内容只是临时政策、阶段判断或敏感信息，不能入库？",
            "7. 如果未来写 GEO / PDP / 种草 / 销售 / 复盘 brief，应该调用哪些知识资产？",
            "",
            "## 当前 Skill 证据清单",
            "",
            f"- 来源转写质量报告：{quality_status}",
            f"- 来源版本报告：{version_status}",
            f"- 事实候选数：{facts_count}",
            f"- 结构化输出文件数：{output_count}",
            f"- 异常确认页：{review_status}",
            f"- 知识库报告页：{library_status}",
            "",
            "## 当前可自动验证的 Skill 价值",
            "",
            f"- 页面覆盖证据：source_quality_report.md 记录总页数 {total_pages}，需要复核页数 {review_pages}。",
            f"- 来源追溯证据：source_facts 中有 {facts_count} 条事实候选，可回到 source transcript / page anchor 核对。",
            f"- 结构化证据：outputs 中有 {output_count} 个 Markdown 输出，用于索引、事实、风险和后续调用。",
            f"- 长期沉淀证据：brand_context_library 中有 {library_entries} 个 Markdown 知识条目。",
            f"- 后续复用证据：retrieval map 中有 {retrieval_notes} 条读取建议，说明后续 brief 应优先读哪些 Wiki 文件。",
            "",
            "## Skill 链路证据路径",
            "",
            f"- Source Index：{_path_status(outputs / '00_source_index.md', project_dir, resolved_library)}",
            f"- Context Asset Index：{_path_status(outputs / '10_context_asset_index.md', project_dir, resolved_library)}",
            f"- Library Update Plan：{_path_status(outputs / '11_context_library_update_plan.md', project_dir, resolved_library)}",
            f"- Source Quality Report：{_path_status(converted / 'source_quality_report.md', project_dir, resolved_library)}",
            f"- Source Version Report：{_path_status(converted / 'source_version_report.md', project_dir, resolved_library)}",
            f"- Review Report：{_path_status(review_page, project_dir, resolved_library)}",
            f"- Library Report：{_path_status(library_report, project_dir, resolved_library)}",
            f"- Retrieval Map：{_path_status(retrieval_map, project_dir, resolved_library)}",
            "",
            "## 质量抽样候选",
            "",
            "优先抽样 source_quality_report.md 中需要复核或可代表读取质量的页面。抽样时只检查原文是否被忠实转写，不要求业务人员逐条审核全部事实。",
            "",
            "| Source Anchor | 原始文件 | 风险说明 | 建议动作 | 抽样结论 |",
            "|---|---|---|---|---|",
            *quality_samples,
            "",
            "## 最小 A/B 执行记录",
            "",
            "| 项目 | 记录 |",
            "|---|---|",
            "| 原始资料直接回答记录 | 待粘贴或链接到本地记录 |",
            "| Structured Wiki 回答记录 | 待粘贴或链接到本地记录 |",
            "| 评分人 | 待填写 |",
            "| 最终判断 | 待判断：直接读更好 / Skill 更好 / 差异不明显 |",
            "",
            "## 对比评分表",
            "",
            "| 维度 | 直接读 PDF/PPT | Skill 链路 | 胜出方 | 证据 |",
            "|---|---|---|---|---|",
            "| 覆盖率 | 待记录 | 待记录 | 待判断 | 哪些页面、表格、图片文字被漏掉 |",
            "| 准确率 | 待记录 | 待记录 | 待判断 | 是否误读、编造或混淆上下文 |",
            "| 来源追溯 | 待记录 | 待记录 | 待判断 | 是否能定位到文件、页码、Source Anchor |",
            "| 低置信度暴露 | 待记录 | 待记录 | 待判断 | 是否明确告诉用户哪些页不可靠 |",
            "| 多文件版本冲突 | 待记录 | 待记录 | 待判断 | 是否识别旧版、新版、疑似冲突 |",
            "| 长期知识沉淀 | 待记录 | 待记录 | 待判断 | 是否能形成可复用 Context Asset |",
            "| 后续 brief 复用 | 待记录 | 待记录 | 待判断 | 是否能说明 GEO / PDP / 种草 / 销售 / 复盘该调用哪些资产 |",
            "| 人工修正成本 | 待记录 | 待记录 | 待判断 | 需要使用者补充或纠错的数量与难度 |",
            "",
            "## A/B 评估提示词",
            "",
            "### A. 直接读 PDF/PPT 的提示词",
            "",
            "```text",
            "请只基于我上传的原始 PDF/PPT/文档回答，不使用外部知识，也不要根据常识补写资料中没有的信息。",
            "",
            "请依次回答以下问题，并在每个答案后说明：",
            "- 你能否指出来自哪一页或哪一部分；",
            "- 哪些内容你不确定；",
            "- 哪些图片、表格、小字或版式内容可能没有识别完整。",
            "",
            "问题：",
            "1. 这个资料大概讲什么？",
            "2. 哪些内容被完整转写了？",
            "3. 哪些页面/图片/表格/小字识别不可靠？",
            "4. 哪些事实来自原文，来源在哪里？",
            "5. 哪些内容可以长期进入品牌知识库？",
            "6. 哪些内容只是临时政策、阶段判断或敏感信息，不能入库？",
            "7. 如果未来写 GEO / PDP / 种草 / 销售 / 复盘 brief，应该调用哪些知识资产？",
            "```",
            "",
            "### B. Skill 链路回答提示词",
            "",
            "```text",
            "请优先基于 source_facts、outputs 和 brand_context_library 回答，不要把未确认内容写成品牌确认。",
            "",
            "回答时必须：",
            "- 引用 Source Anchor、文件名或知识库条目；",
            "- 明确哪些内容来自 source_facts，哪些来自结构化 outputs，哪些来自长期库；",
            "- 标出低置信度、版本冲突、待人工确认和不应入库内容；",
            "- 不补写资料中没有的信息。",
            "",
            "请回答同一组问题：",
            "1. 这个资料大概讲什么？",
            "2. 哪些内容被完整转写了？",
            "3. 哪些页面/图片/表格/小字识别不可靠？",
            "4. 哪些事实来自原文，来源在哪里？",
            "5. 哪些内容可以长期进入品牌知识库？",
            "6. 哪些内容只是临时政策、阶段判断或敏感信息，不能入库？",
            "7. 如果未来写 GEO / PDP / 种草 / 销售 / 复盘 brief，应该调用哪些知识资产？",
            "```",
            "",
            "## 答案记录模板",
            "",
            "| 问题 | 直接读 PDF/PPT 答案摘要 | Skill 链路答案摘要 | 差异 | 证据 |",
            "|---|---|---|---|---|",
            "| 这个资料大概讲什么？ | 待记录 | 待记录 | 待判断 | 待补充 |",
            "| 哪些内容被完整转写了？ | 待记录 | 待记录 | 待判断 | 待补充 |",
            "| 哪些页面/图片/表格/小字识别不可靠？ | 待记录 | 待记录 | 待判断 | 待补充 |",
            "| 哪些事实来自原文，来源在哪里？ | 待记录 | 待记录 | 待判断 | 待补充 |",
            "| 哪些内容可以长期进入品牌知识库？ | 待记录 | 待记录 | 待判断 | 待补充 |",
            "| 哪些内容只是临时政策、阶段判断或敏感信息，不能入库？ | 待记录 | 待记录 | 待判断 | 待补充 |",
            "| 如果未来写 GEO / PDP / 种草 / 销售 / 复盘 brief，应该调用哪些知识资产？ | 待记录 | 待记录 | 待判断 | 待补充 |",
            "",
            "## 判定规则",
            "",
            "- 如果只是单份资料的一次性摘要，直接读 PDF/PPT 可以胜出。",
            "- 如果 Skill 在来源追溯、多文件版本冲突、低置信度暴露、长期知识沉淀和后续 brief 复用上没有明显优势，应降低项目复杂度。",
            "- 如果 Skill 能稳定减少重复阅读和人工纠错，并能把资料沉淀为可调用知识资产，才说明继续开发值得。",
            "",
        ]
    )


def _count_fact_rows(facts_dir: Path) -> int:
    if not facts_dir.exists():
        return 0
    count = 0
    for path in facts_dir.glob("*.md"):
        for line in path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if stripped.startswith("| SF") and "Source Anchor" not in stripped:
                count += 1
    return count


def _read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _metric_value(text: str, label: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"- {label}："):
            return stripped.split("：", 1)[1].strip()
    return "缺失"


def _count_library_entries(library_dir: Path) -> int:
    if not library_dir.exists():
        return 0
    return sum(
        1
        for path in library_dir.rglob("*.md")
        if "review_queue" not in path.parts
        and "retrieval_maps" not in path.parts
        and path.name not in {"00_library_index.md", "evolution_log.md", "taxonomy.md"}
    )


def _count_retrieval_rows(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("|") and "使用场景" not in line and "---" not in line)


def _quality_sample_rows(quality_text: str, limit: int = 5) -> list[str]:
    rows: list[str] = []
    headers: list[str] = []
    for line in quality_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if "Source Anchor" in cells:
            headers = cells
            continue
        if not headers:
            continue
        row = {header: cells[index] if index < len(cells) else "" for index, header in enumerate(headers)}
        status = row.get("读取状态", "")
        risk = row.get("低置信度说明", "").strip()
        action = row.get("建议动作", "").strip()
        if "需要复核" not in status and not risk and not action:
            continue
        anchor = row.get("Source Anchor", "待补充")
        filename = row.get("原始文件", "待补充")
        risk = risk or "需要复核"
        action = action or "回看原文 / 人工抽样"
        rows.append(f"| {anchor} | {filename} | {risk} | {action} | 待抽样 |")
        if len(rows) >= limit:
            return rows
    return rows or ["| 待补充 | 待补充 | 暂无需要复核页面或尚未生成质量报告 | 先生成 source_quality_report.md | 待抽样 |"]


def _path_status(path: Path, project_dir: Path, library_dir: Path) -> str:
    if not path.exists():
        return "缺失"
    try:
        return str(path.relative_to(project_dir))
    except ValueError:
        pass
    try:
        return str(Path("brand_context_library") / path.relative_to(library_dir))
    except ValueError:
        return str(path)
