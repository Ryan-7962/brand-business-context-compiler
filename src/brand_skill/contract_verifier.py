"""Verify project evidence against the local success contract."""

from __future__ import annotations

import subprocess
from pathlib import Path


REQUIRED_OUTPUTS = [
    "02_document_profile.md",
    "03_marketing_semantic_transcript.md",
    "04_key_facts_and_claims.md",
    "05_strategy_and_execution_map.md",
    "06_risk_and_review_items.md",
    "10_context_asset_index.md",
    "11_context_library_update_plan.md",
]


def verify_project_contract(project_dir: Path, library_dir: Path | None = None, repo_dir: Path | None = None) -> None:
    issues: list[str] = []
    target_library = library_dir or (project_dir / "brand_context_library")
    target_repo = repo_dir or _find_repo_dir(project_dir)

    if target_repo:
        _check_repo_privacy(target_repo, issues)
    _check_outputs(project_dir, issues)
    _check_source_conversion(project_dir, issues)
    _check_library(target_library, issues)

    if issues:
        print("Contract verification failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)

    print("Contract verification passed.")


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


def _check_source_conversion(project_dir: Path, issues: list[str]) -> None:
    converted_dir = project_dir / "converted_markdown"
    report = converted_dir / "conversion_report.md"
    transcripts_dir = converted_dir / "source_transcripts"
    if not report.exists():
        issues.append("Missing source conversion report: converted_markdown/conversion_report.md")
    else:
        report_text = report.read_text(encoding="utf-8")
        for marker in ["原始文件创建时间", "原始文件修改时间", "低置信度"]:
            if marker not in report_text:
                issues.append(f"Source conversion report missing marker: {marker}")

    transcripts = list(transcripts_dir.glob("*.md")) if transcripts_dir.exists() else []
    if not transcripts:
        issues.append("Missing source transcript Markdown under converted_markdown/source_transcripts/")
        return

    transcript_text = "\n".join(path.read_text(encoding="utf-8") for path in transcripts)
    for marker in ["Source Anchor", "Page Screenshot", "低置信度"]:
        if marker not in transcript_text:
            issues.append(f"Source transcripts missing marker: {marker}")


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
