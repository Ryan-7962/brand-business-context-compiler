"""Local source conversion engine evaluation planning."""

from __future__ import annotations

import shutil
import subprocess
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol

from .mineru_adapter import _cell, _is_separator, _split_table_row


class Runner(Protocol):
    def __call__(self, command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        ...


ENGINE_COMMANDS = {
    "pymupdf4llm": None,
    "markitdown": ["markitdown", "--version"],
    "mineru": ["mineru", "--version"],
}


def check_source_engines(
    project_dir: Path,
    *,
    which: Callable[[str], str | None] = shutil.which,
    runner: Runner = subprocess.run,
) -> Path:
    """Write a local readiness report for candidate source conversion engines."""
    converted_dir = project_dir / "converted_markdown"
    converted_dir.mkdir(parents=True, exist_ok=True)
    report_path = converted_dir / "source_engine_readiness_report.md"

    rows = []
    for engine, command in ENGINE_COMMANDS.items():
        if command is None:
            rows.append(
                {
                    "engine": engine,
                    "status": "内置默认",
                    "path": "Python dependency",
                    "version": "随项目环境",
                    "recommendation": "继续作为 baseline。",
                }
            )
            continue

        executable = command[0]
        cli_path = which(executable)
        version = "未执行"
        status = "未检测到 CLI"
        recommendation = "不影响第一阶段闭环；仅在本机可用后进入小样评估。"
        if cli_path:
            status = "已检测到 CLI"
            recommendation = "可在私有测试目录做小样对比；通过证据后再考虑接入。"
            try:
                result = runner(
                    [cli_path, *command[1:]],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                )
                version = "\n".join(part.strip() for part in [result.stdout, result.stderr] if part and part.strip())
                version = version or f"退出码 {result.returncode}，无版本输出"
            except (OSError, subprocess.TimeoutExpired) as exc:
                version = str(exc)
                status = "CLI 检测失败"

        rows.append(
            {
                "engine": engine,
                "status": status,
                "path": cli_path or "未找到",
                "version": version,
                "recommendation": recommendation,
            }
        )

    report_text = _render_readiness_report(rows)
    if report_path.exists():
        current_text = report_path.read_text(encoding="utf-8")
        if _strip_checked_at(current_text) == _strip_checked_at(report_text):
            print(f"Source engine readiness report unchanged: {report_path}")
            return report_path
    report_path.write_text(report_text, encoding="utf-8")
    print(f"Source engine readiness report created: {report_path}")
    return report_path


def plan_source_engine_evaluation(project_dir: Path, *, max_pages: int = 5) -> Path:
    """Create a template for comparing pymupdf4llm, MarkItDown, and MinerU."""
    converted_dir = project_dir / "converted_markdown"
    quality_report = converted_dir / "source_quality_report.md"
    if not quality_report.exists():
        print("Missing source quality report: converted_markdown/source_quality_report.md")
        raise SystemExit(1)

    rows = _parse_quality_rows(quality_report.read_text(encoding="utf-8"))
    candidates = [row for row in rows if _is_engine_eval_candidate(row)]
    selected = candidates[:max_pages]
    report_path = converted_dir / "source_engine_eval_plan.md"
    report_path.write_text(_render_eval_plan(selected, max_pages), encoding="utf-8")
    print(f"Source engine evaluation plan created: {report_path}")
    return report_path


def scaffold_source_engine_evaluation_results(project_dir: Path) -> Path:
    """Write a local template for recording multi-engine comparison evidence."""
    converted_dir = project_dir / "converted_markdown"
    plan_path = converted_dir / "source_engine_eval_plan.md"
    if not plan_path.exists():
        print("Missing source engine evaluation plan: converted_markdown/source_engine_eval_plan.md")
        raise SystemExit(1)

    rows = _parse_eval_plan_rows(plan_path.read_text(encoding="utf-8"))
    report_path = converted_dir / "source_engine_eval_results.md"
    report_path.write_text(_render_eval_results(rows), encoding="utf-8")
    print(f"Source engine evaluation results template created: {report_path}")
    return report_path


def _render_readiness_report(rows: list[dict[str, str]]) -> str:
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Source Engine Readiness Report",
        "",
        "## 检查边界",
        "",
        f"- 检查时间：{checked_at}",
        "- 本报告只检查本机是否具备评估条件，不上传真实品牌资料。",
        "- Microsoft MarkItDown / MinerU 都只是 Source-to-Markdown 候选引擎，不是品牌知识编译器本体。",
        "- 未经小样证据证明前，不把任何候选引擎设为默认。",
        "",
        "| Engine | 状态 | CLI / 路径 | 版本输出 | 建议动作 |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    _cell(row["engine"]),
                    _cell(row["status"]),
                    _cell(row["path"]),
                    _cell(row["version"]),
                    _cell(row["recommendation"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## 当前建议",
            "",
            "- `pymupdf4llm` 保持 baseline。",
            "- `markitdown` 优先作为 Microsoft MarkItDown 多格式 Markdown 转换候选评估，重点看 PPTX / DOCX / XLSX / HTML / ZIP 和普通 PDF。",
            "- `mineru` 继续作为复杂版式、扫描件、图片文字、表格和阅读顺序的高保真候选评估。",
            "- DuanYan007/markitdown4j 暂不进入默认检查；若后续需要 Java / PaddleOCR / 本地批量部署，再单独评估。",
            "",
        ]
    )
    return "\n".join(lines)


def _strip_checked_at(text: str) -> str:
    return re.sub(r"^- 检查时间：.+$", "- 检查时间：<checked-at>", text, flags=re.MULTILINE)


def _parse_quality_rows(markdown: str) -> list[dict[str, str]]:
    table_lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    rows: list[dict[str, str]] = []
    index = 0
    while index < len(table_lines) - 1:
        header = _split_table_row(table_lines[index])
        separator = _split_table_row(table_lines[index + 1])
        if "Source Anchor" in header and "建议动作" in header and _is_separator(separator):
            for row_line in table_lines[index + 2 :]:
                cells = _split_table_row(row_line)
                if len(cells) != len(header):
                    break
                rows.append(dict(zip(header, cells)))
            break
        index += 1
    return rows


def _parse_eval_plan_rows(markdown: str) -> list[dict[str, str]]:
    table_lines = _section_table_lines(markdown, "## 建议小样")
    if not table_lines:
        table_lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    rows: list[dict[str, str]] = []
    index = 0
    while index < len(table_lines) - 1:
        header = _split_table_row(table_lines[index])
        separator = _split_table_row(table_lines[index + 1])
        if "Source Anchor" in header and "原始文件" in header and "推荐对比引擎" in header and _is_separator(separator):
            for row_line in table_lines[index + 2 :]:
                cells = _split_table_row(row_line)
                if len(cells) != len(header):
                    break
                row = dict(zip(header, cells))
                if row.get("Source Anchor") and row.get("Source Anchor") != "待补充":
                    rows.append(row)
            break
        index += 1
    return rows


def _section_table_lines(markdown: str, heading: str) -> list[str]:
    lines: list[str] = []
    in_section = False
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line == heading:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section and line.startswith("|"):
            lines.append(line)
    return lines


def _is_engine_eval_candidate(row: dict[str, str]) -> bool:
    action = row.get("建议动作", "")
    confidence = row.get("低置信度说明", "")
    source_file = row.get("原始文件", "").lower()
    return (
        "OCR" in action
        or "MinerU" in action
        or "人工复核" in action
        or "表格" in confidence
        or "图片" in confidence
        or "视觉" in confidence
        or source_file.endswith((".pptx", ".docx", ".xlsx", ".html", ".zip"))
    )


def _render_eval_results(rows: list[dict[str, str]]) -> str:
    lines = [
        "# Source Engine Evaluation Results",
        "",
        "## 评估边界",
        "",
        "- Baseline：pymupdf4llm。",
        "- 候选：Microsoft MarkItDown、MinerU。",
        "- 本文件只记录 source conversion 工具链的小样证据，不是品牌确认，也不是内容总结。",
        "- 真实品牌资料只能在 `_private_test_runs/` 中评估；公开 examples / docs / prompts / schemas 不得写入真实品牌名、预算、销量、价格、平台数据或内部会议内容。",
        "- 未经结果证据证明前，不把候选引擎设为默认链路。",
        "",
        "## 小样级对比记录",
        "",
        "| Source Anchor | 原始文件 | 推荐对比引擎 | pymupdf4llm baseline 观测 | MarkItDown 观察 | MinerU 观察 | 结论 | 是否调整默认链路 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    if rows:
        for row in rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(row.get("Source Anchor", "")),
                        _cell(row.get("原始文件", "")),
                        _cell(row.get("推荐对比引擎", "")),
                        _baseline_observation(row),
                        "待填写",
                        "待填写",
                        "待判断",
                        "否，待证据",
                    ]
                )
                + " |"
            )
    else:
        lines.append("| 待补充 | 待补充 | pymupdf4llm baseline | 暂无候选小样，需先生成 source_quality_report 候选页 | 待填写 | 待填写 | 待判断 | 否，待证据 |")

    lines.extend(
        [
            "",
            "## 接入判断表",
            "",
            "| 维度 | 当前判断 | 证据 | 后续动作 |",
            "|---|---|---|---|",
            "| 文字覆盖率 | 待判断 | 待填写 | 对比抽样页全文覆盖情况 |",
            "| 页码 / slide 锚点 | 待判断 | 待填写 | 检查是否能稳定回溯原文件位置 |",
            "| 表格结构 | 待判断 | 待填写 | 检查复杂表格和跨页表格 |",
            "| 图片 / 图表 / 小字 | 待判断 | 待填写 | 检查视觉页和小字区域 |",
            "| 阅读顺序 | 待判断 | 待填写 | 检查多栏、图文混排和长页 |",
            "| Markdown 可读性 | 待判断 | 待填写 | 检查后续 facts / semantic transcript 是否更稳定 |",
            "| 本地部署复杂度 | 待判断 | 待填写 | 评估依赖、速度和失败模式 |",
            "| 隐私和外部服务风险 | 待判断 | 待填写 | 确认不上传真实品牌资料 |",
            "",
            "## 当前建议",
            "",
            "- MarkItDown 已可作为 optional adapter 使用，但只有当它在多格式输入上明显减少漏读，才扩大使用范围。",
            "- MinerU 仍保持高保真候选；只有当 OCR / 表格 / 图片 / 阅读顺序显著优于 baseline，才考虑接入 `convert-source --engine mineru`。",
            "- 如果候选引擎只是让摘要更顺口，但不能改善 source anchor、覆盖率和复核成本，不应改变默认链路。",
            "",
        ]
    )
    return "\n".join(lines)


def _render_eval_plan(rows: list[dict[str, str]], max_pages: int) -> str:
    lines = [
        "# Source Engine Evaluation Plan",
        "",
        "## 评估目标",
        "",
        "- 目标不是证明某个开源工具更有名，而是判断它是否能让品牌资料转写更完整、更少漏读、更适合后续上下文编译。",
        "- Baseline：当前 `pymupdf4llm` 轻量路径。",
        "- 候选：Microsoft MarkItDown、MinerU；DuanYan007/markitdown4j 暂作为后续 Java / PaddleOCR 方向候选。",
        "- 真实品牌资料只能在 `_private_test_runs/` 中评估，评估结论不得包含真实品牌名、价格、预算、销量或平台数据。",
        f"- 本计划最多选择 {max_pages} 个页面 / slide / 文件片段做小样对比。",
        "",
        "## 建议小样",
        "",
        "| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 | 推荐对比引擎 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    if rows:
        for row in rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(row.get("Source Anchor", "")),
                        _cell(row.get("原始文件", "")),
                        _cell(row.get("可抽取文字数", "待补充")),
                        _cell(row.get("图片数", "待补充")),
                        _cell(row.get("图形数", "待补充")),
                        _cell(row.get("表格数", "待补充")),
                        _cell(row.get("低置信度说明", "")),
                        _cell(row.get("建议动作", "")),
                        _engine_recommendation(row),
                    ]
                )
                + " |"
            )
    else:
        lines.append("| 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 当前质量报告没有明显候选页 | 继续默认轻量路径 | pymupdf4llm baseline |")

    lines.extend(
        [
            "",
            "## 对比记录模板",
            "",
            "| 维度 | pymupdf4llm baseline | MarkItDown | MinerU | 是否改善后续知识编译 |",
            "|---|---|---|---|---|",
            "| 文字覆盖率 | 待记录 | 待记录 | 待记录 | 待判断 |",
            "| 页码 / slide 锚点 | 待记录 | 待记录 | 待记录 | 待判断 |",
            "| 表格结构 | 待记录 | 待记录 | 待记录 | 待判断 |",
            "| 图片 / 图表 / 小字 | 待记录 | 待记录 | 待记录 | 待判断 |",
            "| 阅读顺序 | 待记录 | 待记录 | 待记录 | 待判断 |",
            "| Markdown 可读性 | 待记录 | 待记录 | 待记录 | 待判断 |",
            "| 本地部署复杂度 | 待记录 | 待记录 | 待记录 | 待判断 |",
            "| 隐私和外部服务风险 | 待记录 | 待记录 | 待记录 | 待判断 |",
            "",
            "## 接入判断",
            "",
            "- 如果 MarkItDown 只让 Markdown 更顺眼，但没有提升页码锚点、表格、视觉页或多格式覆盖，不应替换默认引擎。",
            "- 如果 MinerU 只提升少数复杂页，但部署成本高，应保持 optional，不进入默认链路。",
            "- 只有当候选引擎明显降低人工复核成本，并能保留 source anchor，才进入 `convert-source --engine <engine>` 实现。",
            "",
        ]
    )
    return "\n".join(lines)


def _engine_recommendation(row: dict[str, str]) -> str:
    source_file = row.get("原始文件", "").lower()
    confidence = row.get("低置信度说明", "")
    if source_file.endswith((".pptx", ".docx", ".xlsx", ".html", ".zip")):
        return "MarkItDown / pymupdf4llm baseline"
    if any(term in confidence for term in ["表格", "图片", "视觉", "小字", "扫描"]):
        return "MinerU / MarkItDown / pymupdf4llm baseline"
    return "MarkItDown / MinerU / pymupdf4llm baseline"


def _baseline_observation(row: dict[str, str]) -> str:
    parts = []
    for key, label in [
        ("可抽取文字数", "文字数"),
        ("图片数", "图片"),
        ("图形数", "图形"),
        ("表格数", "表格"),
    ]:
        value = row.get(key, "").strip()
        if value:
            parts.append(f"{label} {value}")
    confidence = row.get("低置信度说明", "").strip()
    if confidence:
        parts.append(f"低置信度：{confidence}")
    action = row.get("建议动作", "").strip()
    if action:
        parts.append(f"建议：{action}")
    return _cell("；".join(parts) if parts else "待填写")
