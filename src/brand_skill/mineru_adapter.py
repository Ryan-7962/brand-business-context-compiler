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
