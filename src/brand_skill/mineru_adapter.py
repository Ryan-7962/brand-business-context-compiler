"""Optional MinerU readiness checks."""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Protocol


class Runner(Protocol):
    def __call__(self, command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        ...


def check_mineru_readiness(
    project_dir: Path,
    *,
    which: Callable[[str], str | None] = shutil.which,
    runner: Runner = subprocess.run,
) -> Path:
    """Write a local report describing whether MinerU can be evaluated."""
    converted_dir = project_dir / "converted_markdown"
    converted_dir.mkdir(parents=True, exist_ok=True)
    report_path = converted_dir / "mineru_readiness_report.md"

    cli_path = which("mineru")
    version_output = ""
    version_status = "未执行"
    command_text = "mineru --version"

    if cli_path:
        try:
            result = runner(
                [cli_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            version_output = "\n".join(part.strip() for part in [result.stdout, result.stderr] if part and part.strip())
            version_status = f"退出码 {result.returncode}"
        except (OSError, subprocess.TimeoutExpired) as exc:
            version_output = str(exc)
            version_status = "版本探测失败"

    report = _render_report(
        cli_path=cli_path,
        command_text=command_text,
        version_status=version_status,
        version_output=version_output,
    )
    report_path.write_text(report, encoding="utf-8")
    print(f"MinerU readiness report created: {report_path}")
    return report_path


def plan_mineru_evaluation(project_dir: Path, *, max_pages: int = 5) -> Path:
    """Select high-value pages for a local MinerU comparison plan."""
    converted_dir = project_dir / "converted_markdown"
    quality_report = converted_dir / "source_quality_report.md"
    if not quality_report.exists():
        print("Missing source quality report: converted_markdown/source_quality_report.md")
        raise SystemExit(1)

    rows = _parse_quality_rows(quality_report.read_text(encoding="utf-8"))
    candidates = [row for row in rows if _is_mineru_eval_candidate(row)]
    selected = candidates[:max_pages]
    report_path = converted_dir / "mineru_eval_plan.md"
    report_path.write_text(_render_eval_plan(selected, max_pages), encoding="utf-8")
    print(f"MinerU evaluation plan created: {report_path}")
    return report_path


def _render_report(*, cli_path: str | None, command_text: str, version_status: str, version_output: str) -> str:
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if cli_path:
        status = "已检测到 MinerU CLI"
        recommendation = "后续可在私有测试目录做 5 页以内小样对比，再决定是否接入 `convert-source --engine mineru`。"
        cli_line = cli_path
    else:
        status = "未检测到 MinerU CLI"
        recommendation = "不影响第一阶段闭环；当前仍使用默认轻量路径跑通 source conversion、source facts、outputs、入库和报告页。"
        cli_line = "未找到"

    output_block = version_output.strip() or "无"
    return "\n".join(
        [
            "# MinerU Readiness Report",
            "",
            "## 检查结论",
            "",
            f"- 检查时间：{checked_at}",
            f"- 状态：{status}",
            f"- CLI 路径：{cli_line}",
            f"- 版本命令：`{command_text}`",
            f"- 版本命令状态：{version_status}",
            "",
            "## 版本输出",
            "",
            "```text",
            output_block,
            "```",
            "",
            "## 建议动作",
            "",
            f"- {recommendation}",
            "- MinerU 只作为高保真资料转写增强，不作为品牌知识编译器本体。",
            "- 真实品牌资料只能放在 `_private_test_runs/` 私有测试区，不得写入正式 examples / docs / prompts / schemas。",
            "- 评估时优先对比复杂版式、图片文字、表格、小字、扫描页和阅读顺序，而不是只看摘要是否顺口。",
            "",
        ]
    )


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


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(cell and set(cell.replace(" ", "")) <= {"-", ":"} for cell in cells)


def _is_mineru_eval_candidate(row: dict[str, str]) -> bool:
    action = row.get("建议动作", "")
    confidence = row.get("低置信度说明", "")
    return "MinerU" in action or "OCR" in action or "表格" in confidence or "图片" in confidence or "视觉" in confidence


def _render_eval_plan(rows: list[dict[str, str]], max_pages: int) -> str:
    lines = [
        "# MinerU Evaluation Plan",
        "",
        "## 评估边界",
        "",
        "- Baseline：pymupdf4llm",
        "- MinerU：仅作为高保真 source conversion 候选，不是品牌知识编译器本体。",
        "- 真实品牌资料只能放在 `_private_test_runs/` 私有测试区，不得写入正式 examples / docs / prompts / schemas。",
        f"- 本计划最多选择 {max_pages} 个页面 / slide 做小样对比。",
        "",
        "## 建议对比页面",
        "",
        "| Source Anchor | 原始文件 | 低置信度说明 | 建议动作 |",
        "|---|---|---|---|",
    ]
    if rows:
        for row in rows:
            lines.append(
                "| "
                + " | ".join(
                    [
                        _cell(row.get("Source Anchor", "")),
                        _cell(row.get("原始文件", "")),
                        _cell(row.get("低置信度说明", "")),
                        _cell(row.get("建议动作", "")),
                    ]
                )
                + " |"
            )
    else:
        lines.append("| 待补充 | 待补充 | 当前质量报告没有明显 MinerU 候选页 | 继续默认轻量路径 |")
    lines.extend(
        [
            "",
            "## 评估维度",
            "",
            "| 维度 | pymupdf4llm baseline | MinerU 小样结果 | 是否值得接入 |",
            "|---|---|---|---|",
            "| OCR 完整度 | 待记录 | 待记录 | 待判断 |",
            "| 表格还原 | 待记录 | 待记录 | 待判断 |",
            "| 图片/图表保留 | 待记录 | 待记录 | 待判断 |",
            "| 阅读顺序 | 待记录 | 待记录 | 待判断 |",
            "| 输出 Markdown 可读性 | 待记录 | 待记录 | 待判断 |",
            "| 部署复杂度 | 待记录 | 待记录 | 待判断 |",
            "",
        ]
    )
    return "\n".join(lines)


def _cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ").strip()
