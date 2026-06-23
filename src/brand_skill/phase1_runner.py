"""Run the full local Phase 1 workflow from source files to verification."""

from __future__ import annotations

from pathlib import Path

from .contract_verifier import verify_project_contract
from .library_report import build_library_report
from .library_writer import apply_context_library_update
from .output_compiler import compile_structured_outputs
from .review_pack import build_review_pack
from .source_converter import convert_source
from .source_facts import build_source_facts
from .source_quality import build_source_quality_report
from .source_versions import build_source_version_report
from .value_benchmark import build_value_benchmark


def run_phase1_workflow(
    project_dir: Path,
    *,
    library_dir: Path | None = None,
    engine: str = "pymupdf4llm",
    keep_existing: bool = False,
) -> None:
    """Execute the first-stage evidence loop for a real local project."""
    target_library = library_dir or (project_dir / "brand_context_library")
    convert_source(project_dir, engine=engine)
    build_source_facts(project_dir)
    build_source_quality_report(project_dir)
    build_source_version_report(project_dir)
    compile_structured_outputs(project_dir, keep_existing=keep_existing)
    build_review_pack(project_dir)
    apply_context_library_update(project_dir, library_dir=target_library)
    build_library_report(target_library)
    build_value_benchmark(project_dir, library_dir=target_library)
    verify_project_contract(
        project_dir,
        library_dir=target_library,
        report_path=project_dir / "contract_verification_report.md",
    )
    print("Phase 1 workflow completed.")
