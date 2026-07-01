"""Verify project evidence against the local success contract."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


REQUIRED_OUTPUTS = [
    "00_source_index.md",
    "02_document_profile.md",
    "03_marketing_semantic_transcript.md",
    "04_key_facts_and_claims.md",
    "05_strategy_and_execution_map.md",
    "06_risk_and_review_items.md",
    "10_context_asset_index.md",
    "11_context_library_update_plan.md",
]

REQUIRED_PHASE1_PROMPTS = [
    "00_source_to_markdown_conversion.md",
    "01_generate_document_profile.md",
    "02_generate_marketing_semantic_transcript.md",
    "03_generate_key_facts_and_claims.md",
    "04_generate_strategy_and_execution_map.md",
    "05_generate_risk_and_review_items.md",
    "06_generate_ai_ready_marketing_brief_base.md",
    "07_generate_review_pack.md",
    "08_generate_context_asset_index.md",
    "09_generate_context_library_update_plan.md",
    "11_quality_check.md",
]

REQUIRED_CORE_SCHEMAS = [
    "source_index.schema.md",
    "source_conversion_report.schema.md",
    "document_profile.schema.md",
    "marketing_semantic_transcript.schema.md",
    "risk_and_review_items.schema.md",
    "context_asset_index.schema.md",
    "context_library_update_plan.schema.md",
    "quality_check_report.schema.md",
]


def verify_project_contract(
    project_dir: Path,
    library_dir: Path | None = None,
    repo_dir: Path | None = None,
    report_path: Path | None = None,
) -> None:
    issues: list[str] = []
    target_library = library_dir or (project_dir / "brand_context_library")
    target_repo = repo_dir or _find_repo_dir(project_dir)

    if target_repo:
        _check_skill_package(target_repo, issues)
        _check_prompt_schema_package(target_repo, issues)
        _check_repo_privacy(target_repo, issues)
    _check_outputs(project_dir, issues)
    _check_source_conversion(project_dir, issues)
    _check_review_pack(project_dir, issues)
    _check_library(target_library, issues)
    _check_value_benchmark(project_dir, issues)
    _check_unapproved_confirmed_status(project_dir, target_library, issues)

    if report_path:
        _write_verification_report(report_path, project_dir, target_library, target_repo, issues)

    if issues:
        print("Contract verification failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)

    print("Contract verification passed.")


def _write_verification_report(
    report_path: Path,
    project_dir: Path,
    library_dir: Path,
    repo_dir: Path | None,
    issues: list[str],
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    status = "failed" if issues else "passed"
    lines = [
        "# Contract Verification Report",
        "",
        f"- Status: {status}",
        f"- Project: {project_dir}",
        f"- Library: {library_dir}",
        f"- Repo: {repo_dir if repo_dir else 'not detected'}",
        "",
        "## Checked Evidence",
        "",
        "- Required structured outputs",
        "- Skill package entrypoint",
        "- Prompt and schema package",
        "- Source conversion report, quality/version summaries, and source transcripts",
        "- Source engine readiness, evaluation plan, and evaluation results",
        "- Exception review page",
        "- Context library entries and review queues",
        "- Brand Context Map report",
        "- Direct PDF/PPT vs Skill benchmark",
        "- Private test file tracking",
        "- Optional privacy term scan",
        "- Unapproved confirmed-status claims",
        "",
        "## Issues",
        "",
    ]
    if issues:
        lines.extend(f"- {issue}" for issue in issues)
    else:
        lines.append("No issues found.")
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")


def _check_skill_package(repo_dir: Path, issues: list[str]) -> None:
    skill_path = repo_dir / "SKILL.md"
    if not skill_path.exists():
        issues.append("Missing skill package entrypoint: SKILL.md")
        return

    text = skill_path.read_text(encoding="utf-8")
    required_markers = [
        "name: brand-business-context-compiler",
        "description: Use when",
        "brand-skill run-phase1",
        "Source Conversion Engines",
        "source_engine_eval_results.md",
        "review/brand_review.html",
        "library_report.html",
        "_private_test_runs/",
        "Do not",
    ]
    for marker in required_markers:
        if marker not in text:
            issues.append(f"Skill package entrypoint missing marker: {marker}")


def _check_prompt_schema_package(repo_dir: Path, issues: list[str]) -> None:
    prompt_bundle = repo_dir / "prompt_bundle.md"
    if not prompt_bundle.exists():
        issues.append("Missing prompt package bundle: prompt_bundle.md")
    else:
        bundle_text = prompt_bundle.read_text(encoding="utf-8")
        for marker in ["Prompt Bundle", "Source-to-Markdown", "Marketing Semantic Transcript", "Context Asset Index"]:
            if marker not in bundle_text:
                issues.append(f"Prompt package bundle missing marker: {marker}")

    prompts_dir = repo_dir / "prompts"
    for filename in REQUIRED_PHASE1_PROMPTS:
        path = prompts_dir / filename
        if not path.exists():
            issues.append(f"Missing required Phase 1 prompt: prompts/{filename}")
        elif not path.read_text(encoding="utf-8").strip():
            issues.append(f"Empty required Phase 1 prompt: prompts/{filename}")

    schemas_dir = repo_dir / "schemas"
    for filename in REQUIRED_CORE_SCHEMAS:
        path = schemas_dir / filename
        if not path.exists():
            issues.append(f"Missing required core schema: schemas/{filename}")
        elif not path.read_text(encoding="utf-8").strip():
            issues.append(f"Empty required core schema: schemas/{filename}")


def _find_repo_dir(path: Path) -> Path | None:
    current = path.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def _check_repo_privacy(repo_dir: Path, issues: list[str]) -> None:
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=repo_dir,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        issues.append(f"Unable to inspect git tracked files for repo: {repo_dir}")
        return

    for tracked_path in result.stdout.splitlines():
        if tracked_path.startswith("_private_test_runs/"):
            issues.append(f"Tracked private test file: {tracked_path}")
    _check_privacy_terms(repo_dir, result.stdout.splitlines(), issues)


def _check_privacy_terms(repo_dir: Path, tracked_paths: list[str], issues: list[str]) -> None:
    pattern = os.environ.get("BRAND_SKILL_PRIVACY_TERMS_REGEX", "").strip()
    if not pattern:
        return
    try:
        regex = re.compile(pattern)
    except re.error as exc:
        issues.append(f"Invalid BRAND_SKILL_PRIVACY_TERMS_REGEX: {exc}")
        return

    for tracked_path in tracked_paths:
        if tracked_path.startswith("_private_test_runs/"):
            continue
        path = repo_dir / tracked_path
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if regex.search(text):
            issues.append(f"Privacy term match in tracked file: {tracked_path}")


def _check_outputs(project_dir: Path, issues: list[str]) -> None:
    outputs_dir = project_dir / "outputs"
    if not outputs_dir.exists():
        issues.append("Missing outputs directory: outputs/")
        return
    for filename in REQUIRED_OUTPUTS:
        path = outputs_dir / filename
        if not path.exists():
            issues.append(f"Missing required output: outputs/{filename}")
        elif not path.read_text(encoding="utf-8").strip():
            issues.append(f"Empty required output: outputs/{filename}")
    _check_structured_output_markers(outputs_dir, issues)


def _check_structured_output_markers(outputs_dir: Path, issues: list[str]) -> None:
    required_markers = {
        "00_source_index.md": ["内容概述", "转写 Markdown", "Source Facts"],
        "02_document_profile.md": ["文件类型", "文件目的", "信息状态", "待确认"],
        "03_marketing_semantic_transcript.md": ["Marketing Semantic Transcript", "Source Anchor", "原页核心内容转述"],
        "04_key_facts_and_claims.md": ["Key Facts", "信息状态", "待确认"],
        "10_context_asset_index.md": ["Context Asset Index", "适用场景", "信息状态"],
        "11_context_library_update_plan.md": ["Context Library Update Plan", "New Context Entries", "Do Not Promote", "Retrieval Notes", "优先读取", "精读文件", "回看原文"],
    }
    for filename, markers in required_markers.items():
        path = outputs_dir / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                issues.append(f"Structured output missing marker in outputs/{filename}: {marker}")


def _check_unapproved_confirmed_status(project_dir: Path, library_dir: Path, issues: list[str]) -> None:
    candidates = []
    outputs_dir = project_dir / "outputs"
    if outputs_dir.exists():
        candidates.extend(outputs_dir.glob("*.md"))
    if library_dir.exists():
        candidates.extend(
            path
            for path in library_dir.rglob("*.md")
            if "review_queue" not in path.parts and "retrieval_maps" not in path.parts
        )

    for path in candidates:
        if "已品牌确认" not in path.read_text(encoding="utf-8"):
            continue
        label = _display_path(path, project_dir, library_dir)
        issues.append(f"Unapproved confirmed status in generated file: {label}")


def _display_path(path: Path, project_dir: Path, library_dir: Path) -> str:
    try:
        return str(path.relative_to(project_dir))
    except ValueError:
        pass
    try:
        return str(path.relative_to(library_dir))
    except ValueError:
        return str(path)


def _check_source_conversion(project_dir: Path, issues: list[str]) -> None:
    converted_dir = project_dir / "converted_markdown"
    report = converted_dir / "conversion_report.md"
    quality_report = converted_dir / "source_quality_report.md"
    version_report = converted_dir / "source_version_report.md"
    engine_readiness_report = converted_dir / "source_engine_readiness_report.md"
    engine_eval_plan = converted_dir / "source_engine_eval_plan.md"
    engine_eval_results = converted_dir / "source_engine_eval_results.md"
    transcripts_dir = converted_dir / "source_transcripts"
    report_text = ""
    quality_text = ""
    if not report.exists():
        issues.append("Missing source conversion report: converted_markdown/conversion_report.md")
    else:
        report_text = report.read_text(encoding="utf-8")
        for marker in ["原始文件创建时间", "原始文件修改时间", "转写时间", "低置信度"]:
            if marker not in report_text:
                issues.append(f"Source conversion report missing marker: {marker}")
        for marker in ["识别质量摘要", "总页数", "视觉/表格/小字限制", "人工复核建议"]:
            if marker not in report_text:
                issues.append(f"Source conversion report missing quality marker: {marker}")

    transcripts = list(transcripts_dir.glob("*.md")) if transcripts_dir.exists() else []
    if not transcripts:
        issues.append("Missing source transcript Markdown under converted_markdown/source_transcripts/")
        return

    transcript_text = "\n".join(path.read_text(encoding="utf-8") for path in transcripts)
    for marker in ["Source Anchor", "Page Screenshot", "低置信度"]:
        if marker not in transcript_text:
            issues.append(f"Source transcripts missing marker: {marker}")

    if not quality_report.exists():
        issues.append("Missing source quality report: converted_markdown/source_quality_report.md")
    else:
        quality_text = quality_report.read_text(encoding="utf-8")
        for marker in ["识别质量总览", "总页数", "需要复核页数", "表格数", "OCR", "建议动作"]:
            if marker not in quality_text:
                issues.append(f"Source quality report missing marker: {marker}")
    conversion_total = _extract_total_pages(report_text)
    quality_total = _extract_total_pages(quality_text)
    if conversion_total is not None and quality_total is not None and conversion_total != quality_total:
        issues.append(f"Source total page mismatch: conversion_report.md={conversion_total}, source_quality_report.md={quality_total}")
    issues.extend(_source_page_coverage_issues(report_text, transcript_text))

    if not version_report.exists():
        issues.append("Missing source version report: converted_markdown/source_version_report.md")
    else:
        version_text = version_report.read_text(encoding="utf-8")
        for marker in ["版本线索总览", "疑似多版本组数", "不自动覆盖"]:
            if marker not in version_text:
                issues.append(f"Source version report missing marker: {marker}")

    if not engine_readiness_report.exists():
        issues.append("Missing source engine readiness report: converted_markdown/source_engine_readiness_report.md")
    else:
        readiness_text = engine_readiness_report.read_text(encoding="utf-8")
        for marker in ["Source Engine Readiness Report", "pymupdf4llm", "Microsoft MarkItDown", "MinerU", "Source-to-Markdown"]:
            if marker not in readiness_text:
                issues.append(f"Source engine readiness report missing marker: {marker}")

    if not engine_eval_plan.exists():
        issues.append("Missing source engine evaluation plan: converted_markdown/source_engine_eval_plan.md")
    else:
        eval_text = engine_eval_plan.read_text(encoding="utf-8")
        for marker in ["Source Engine Evaluation Plan", "pymupdf4llm", "MarkItDown", "MinerU", "文字覆盖率", "隐私"]:
            if marker not in eval_text:
                issues.append(f"Source engine evaluation plan missing marker: {marker}")

    if not engine_eval_results.exists():
        issues.append("Missing source engine evaluation results: converted_markdown/source_engine_eval_results.md")
    else:
        results_text = engine_eval_results.read_text(encoding="utf-8")
        for marker in ["Source Engine Evaluation Results", "pymupdf4llm", "pymupdf4llm baseline 观测", "MarkItDown", "MinerU", "是否调整默认链路", "隐私"]:
            if marker not in results_text:
                issues.append(f"Source engine evaluation results missing marker: {marker}")


def _check_review_pack(project_dir: Path, issues: list[str]) -> None:
    review_page = project_dir / "review" / "brand_review.html"
    if not review_page.exists():
        issues.append("Missing exception review page: review/brand_review.html")
        return

    text = review_page.read_text(encoding="utf-8")
    required_markers = ["内容读取报告", "读取覆盖状态", "整个文件概述", "文件大纲参考"]
    for marker in required_markers:
        if marker not in text:
            issues.append(f"Review page missing exception-review marker: {marker}")

    if not any(marker in text for marker in ["需要处理的问题", "自动通过，无需人工处理"]):
        issues.append("Review page missing exception-review marker: 需要处理的问题 or 自动通过，无需人工处理")

    backend_markers = [
        "Context Asset Index Review",
        'class="source-anchor"',
        "Review ID",
        "Source Anchor",
        "来源位置：",
        "来源锚点",
        "Risk Level",
        "风险等级",
        "review-controls",
        "setDecision",
        "确认意见",
    ]
    for marker in backend_markers:
        if marker in text:
            issues.append(f"Review page overexposes backend marker: {marker}")


def _check_value_benchmark(project_dir: Path, issues: list[str]) -> None:
    benchmark = project_dir / "evaluation" / "direct_vs_skill_benchmark.md"
    if not benchmark.exists():
        issues.append("Missing value benchmark: evaluation/direct_vs_skill_benchmark.md")
        return

    text = benchmark.read_text(encoding="utf-8")
    for marker in [
        "Direct PDF/PPT vs Skill Benchmark",
        "固定问题集",
        "对比评分表",
        "A/B 评估提示词",
        "直接读 PDF/PPT 的提示词",
        "Skill 链路回答提示词",
        "答案记录模板",
        "覆盖率",
        "来源追溯",
        "长期知识沉淀",
    ]:
        if marker not in text:
            issues.append(f"Value benchmark missing marker: {marker}")


def _check_library(library_dir: Path, issues: list[str]) -> None:
    if not library_dir.exists():
        issues.append(f"Missing context library: {library_dir}")
        return

    entries = [
        path
        for path in library_dir.rglob("*.md")
        if "review_queue" not in path.parts and "retrieval_maps" not in path.parts and path.name != "00_library_index.md"
    ]
    if not entries:
        issues.append("Missing context library Markdown entries")

    required_files = [
        library_dir / "review_queue" / "conflicts.md",
        library_dir / "review_queue" / "updates.md",
        library_dir / "review_queue" / "do_not_promote.md",
        library_dir / "retrieval_maps" / "source_packages.md",
        library_dir / "library_report.html",
    ]
    for path in required_files:
        if not path.exists():
            issues.append(f"Missing library evidence file: {path.relative_to(library_dir)}")

    report = library_dir / "library_report.html"
    if report.exists():
        report_text = report.read_text(encoding="utf-8")
        for marker in ["Brand Context Map", "Knowledge Explorer", "categoryFilter", "statusFilter", "条目详情"]:
            if marker not in report_text:
                issues.append(f"Library report missing marker: {marker}")
        for remote_marker in ["https://", "http://", "src=\"//", "href=\"//"]:
            if remote_marker in report_text:
                issues.append(f"Library report references remote resource: {remote_marker}")
        for backend_marker in ["Source Anchor", "Risk Level", "来源锚点", "风险等级"]:
            if backend_marker in report_text:
                issues.append(f"Library report overexposes backend marker: {backend_marker}")
        for backend_file in ["source_version_report.md", "source_quality_report.md"]:
            if backend_file in report_text:
                issues.append(f"Library report exposes backend report file: {backend_file}")
        _check_library_report_version_review(library_dir, report_text, issues)


def _check_library_report_version_review(library_dir: Path, report_text: str, issues: list[str]) -> None:
    updates_path = library_dir / "review_queue" / "updates.md"
    if not updates_path.exists():
        return
    updates_text = updates_path.read_text(encoding="utf-8")
    if "疑似多版本资料" not in updates_text:
        return
    for marker in ["待处理事项", "建议动作", "最新修改时间线索"]:
        if marker not in report_text:
            issues.append(f"Library report missing version-review marker: {marker}")


def _extract_total_pages(text: str) -> int | None:
    match = re.search(r"总页数[：:]\s*(\d+)", text)
    return int(match.group(1)) if match else None


def _source_page_coverage_issues(report_text: str, transcript_text: str) -> list[str]:
    expected: dict[str, int] = {}
    for line in report_text.splitlines():
        cells = _markdown_cells(line)
        if len(cells) < 10 or not re.fullmatch(r"S\d{3}", cells[0]):
            continue
        expected[cells[0]] = expected.get(cells[0], 0) + _page_count_from_range(cells[9])
    if not expected:
        return []

    seen_pages: dict[str, set[int]] = {}
    for source_id, page_number in re.findall(r"(S\d{3})#page=(\d+)", transcript_text):
        seen_pages.setdefault(source_id, set()).add(int(page_number))

    issues = []
    for source_id, expected_pages in expected.items():
        actual_pages = len(seen_pages.get(source_id, set()))
        if actual_pages != expected_pages:
            issues.append(f"Source page coverage mismatch: {source_id} expected {expected_pages}, transcript anchors {actual_pages}")
    return issues


def _markdown_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def _page_count_from_range(page_range: str) -> int:
    match = re.search(r"(\d+)\s*-\s*(\d+)", page_range)
    if match:
        start, end = int(match.group(1)), int(match.group(2))
        return max(0, end - start + 1)
    numbers = re.findall(r"\d+", page_range)
    return len(numbers) if numbers else 1
