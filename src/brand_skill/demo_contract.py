"""Run the local demo evidence loop with one command."""

from __future__ import annotations

from pathlib import Path

from .contract_verifier import verify_project_contract
from .library_report import build_library_report
from .library_writer import apply_context_library_update
from .output_compiler import compile_structured_outputs
from .source_quality import build_source_quality_report
from .source_versions import build_source_version_report
from .value_benchmark import build_value_benchmark


def run_demo_contract(project_dir: Path, library_dir: Path | None = None) -> None:
    target_library = library_dir or (project_dir / "brand_context_library")
    build_source_quality_report(project_dir)
    build_source_version_report(project_dir)
    compile_structured_outputs(project_dir, keep_existing=True)
    apply_context_library_update(project_dir, library_dir=target_library)
    build_library_report(target_library)
    build_value_benchmark(project_dir, library_dir=target_library)
    verify_project_contract(
        project_dir,
        library_dir=target_library,
        report_path=project_dir / "contract_verification_report.md",
    )
