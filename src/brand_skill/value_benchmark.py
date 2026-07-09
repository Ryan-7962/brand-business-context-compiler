"""Build a local scorecard for comparing direct AI reading with the Skill workflow."""

from __future__ import annotations

from pathlib import Path


def build_value_benchmark(project_dir: Path, library_dir: Path | None = None) -> Path:
    """Create a benchmark template that tests whether the Skill adds real value."""
    evaluation_dir = project_dir / "evaluation"
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    report_path = evaluation_dir / "direct_vs_skill_benchmark.md"
    report_path.write_text(_render_report(project_dir, library_dir), encoding="utf-8")
    record_path = evaluation_dir / "ab_answer_record.md"
    if not record_path.exists():
        record_path.write_text(_render_answer_record(), encoding="utf-8")
    sampling_path = evaluation_dir / "quality_sampling_log.md"
    if not sampling_path.exists():
        sampling_path.write_text(_render_quality_sampling_log(project_dir), encoding="utf-8")
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
            "| A/B 答案记录文件 | evaluation/ab_answer_record.md |",
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


def _render_answer_record() -> str:
    questions = [
        "这个资料大概讲什么？",
        "哪些内容被完整转写了？",
        "哪些页面/图片/表格/小字识别不可靠？",
        "哪些事实来自原文，来源在哪里？",
        "哪些内容可以长期进入品牌知识库？",
        "哪些内容只是临时政策、阶段判断或敏感信息，不能入库？",
        "如果未来写 GEO / PDP / 种草 / 销售 / 复盘 brief，应该调用哪些知识资产？",
    ]
    rows = [
        f"| {question} | 待粘贴 | 待粘贴 | 待评分 | 待补充 |"
        for question in questions
    ]
    return "\n".join(
        [
            "# A/B Answer Record｜Direct Source vs Structured Wiki",
            "",
            "本文件用于记录同一批资料、同一组问题下的两组真实 Agent 回答。不要在这里编造评估结果；没有实际跑过就保持 `待粘贴` / `待评分`。",
            "",
            "## 运行信息",
            "",
            "| 项目 | 记录 |",
            "|---|---|",
            "| 资料包 | 待填写 |",
            "| 直接读原始资料的 Agent / 模型 | 待填写 |",
            "| 读取 Structured Wiki 的 Agent / 模型 | 待填写 |",
            "| 评分人 | 待填写 |",
            "| 最终判断 | 待判断：直接读更好 / Skill 更好 / 差异不明显 |",
            "",
            "## 同题答案记录",
            "",
            "| 问题 | 直接读原始资料答案摘要 | Structured Wiki 答案摘要 | 胜出方 | 证据 |",
            "|---|---|---|---|---|",
            *rows,
            "",
            "## 评分维度",
            "",
            "| 维度 | 直接读原始资料 | Structured Wiki | 胜出方 | 证据 |",
            "|---|---|---|---|---|",
            "| 覆盖率 | 待评分 | 待评分 | 待判断 | 待补充 |",
            "| 准确率 | 待评分 | 待评分 | 待判断 | 待补充 |",
            "| 来源追溯 | 待评分 | 待评分 | 待判断 | 待补充 |",
            "| 低置信度暴露 | 待评分 | 待评分 | 待判断 | 待补充 |",
            "| 多文件版本冲突 | 待评分 | 待评分 | 待判断 | 待补充 |",
            "| 长期知识沉淀 | 待评分 | 待评分 | 待判断 | 待补充 |",
            "| 后续 brief 复用 | 待评分 | 待评分 | 待判断 | 待补充 |",
            "| 人工修正成本 | 待评分 | 待评分 | 待判断 | 待补充 |",
            "",
        ]
    )


def _render_quality_sampling_log(project_dir: Path) -> str:
    quality_text = _read_optional(project_dir / "converted_markdown" / "source_quality_report.md")
    facts_count = _count_fact_rows(project_dir / "converted_markdown" / "source_facts")
    total_pages = _metric_value(quality_text, "总页数")
    review_pages = _metric_value(quality_text, "需要复核页数")
    sample_rows = _quality_sampling_rows(quality_text)
    minimum_sample = _minimum_sample_size(total_pages)
    return "\n".join(
        [
            "# Quality Sampling Log",
            "",
            "本文件用于记录页面级 / 事实级抽样结果。生成时不会假装已经人工核对；未回看原页前，默认只作为抽样计划和风险记录。",
            "",
            "## Summary",
            "",
            "| 项目 | 记录 |",
            "|---|---|",
            f"| 总页数 | {total_pages} |",
            f"| 需要复核页数 | {review_pages} |",
            f"| source facts 数 | {facts_count} |",
            f"| 建议最小抽样页数 | {minimum_sample} |",
            "| 当前结论 | 未形成 90% 页面级 / 事实级准确率证据 |",
            "",
            "## Page Sampling Plan",
            "",
            "| sample_id | source_anchor | sampled_reason | source_state | accuracy_result | correction_needed |",
            "|---|---|---|---|---|---|",
            *sample_rows,
            "",
            "## Pass Rate",
            "",
            "| 指标 | 数值 |",
            "|---|---:|",
            "| 页面级通过数 | 0 |",
            f"| 页面级待抽样数 | {len(sample_rows)} |",
            "| 页面级通过率 | 未形成证据 |",
            "| 事实级抽样数 | 0 |",
            "| 事实级通过率 | 未形成证据 |",
            "| P0 | 0 |",
            "| P1 | 待人工核对后填写 |",
            "",
            "## Next Action",
            "",
            f"- 至少人工核对 {minimum_sample} 页抽样页面；优先选择低置信度、表格、图片、小字和关键数字页面。",
            "- 至少抽样 5 条 source facts，回到 transcript / 原页确认。",
            "- 未完成原页核对前，不得声明 90% 准确率。",
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


def _quality_sampling_rows(quality_text: str, limit: int = 16) -> list[str]:
    rows = []
    for index, row in enumerate(_quality_rows(quality_text)[:limit], start=1):
        risk = row.get("低置信度说明", "").strip() or row.get("读取状态", "").strip() or "待抽样"
        anchor = row.get("Source Anchor", "待补充")
        rows.append(
            f"| QS{index:03d} | {anchor} | {risk} | 待回看原页 | 待抽样 | 人工抽样 / 换引擎小样 |"
        )
    return rows or ["| QS001 | 待补充 | 尚未生成质量报告 | 待回看原页 | 待抽样 | 先生成 source_quality_report.md |"]


def _quality_rows(quality_text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    headers: list[str] = []
    for line in quality_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if "Source Anchor" in cells:
            headers = cells
            continue
        if headers:
            row = {header: cells[index] if index < len(cells) else "" for index, header in enumerate(headers)}
            if row.get("Source Anchor", "").strip() in {"", "-"}:
                continue
            rows.append(row)
    return rows


def _minimum_sample_size(total_pages: str) -> str:
    try:
        pages = int(total_pages)
    except ValueError:
        return "待计算"
    if pages <= 20:
        return str(max(6, (pages * 30 + 99) // 100))
    if pages <= 80:
        return str(max(12, (pages * 20 + 99) // 100))
    if pages <= 200:
        return str(max(20, (pages * 12 + 99) // 100))
    return str(max(30, (pages * 8 + 99) // 100))


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
