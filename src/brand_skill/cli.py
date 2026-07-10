"""CLI skeleton for Brand Marketing Context Compiler.

This is intentionally lightweight. Codex should expand it in the first development pass.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .contract_verifier import verify_project_contract
from .demo_contract import run_demo_contract
from .ima_importer import import_ima_media
from .library_report import build_library_report
from .library_writer import apply_context_library_update
from .mineru_adapter import check_mineru_readiness, plan_mineru_evaluation, scaffold_mineru_evaluation_results
from .output_compiler import compile_structured_outputs
from .phase1_runner import run_phase1_workflow
from .review_pack import build_review_pack
from .source_facts import build_source_facts
from .source_converter import convert_source
from .source_engine_eval import check_source_engines, plan_source_engine_evaluation, scaffold_source_engine_evaluation_results
from .source_quality import build_source_quality_report
from .source_versions import build_source_version_report
from .value_benchmark import build_value_benchmark
from .wiki_verifier import verify_wiki
from .wiki_report import build_wiki_report
from .wiki_workflow import prepare_wiki_sources
from .workflow import init_project, scaffold_output, validate_input, build_prompt_pack
from .validators import check_brand_lock_sheet_draft, check_claim_matrix


def main() -> None:
    parser = argparse.ArgumentParser(prog="brand-skill")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("project_name")

    p_validate = sub.add_parser("validate-input")
    p_validate.add_argument("project_dir")

    p_scaffold = sub.add_parser("scaffold-output")
    p_scaffold.add_argument("project_dir")

    p_claim = sub.add_parser("check-claim-matrix")
    p_claim.add_argument("project_dir")

    p_brand_lock = sub.add_parser("check-brand-lock")
    p_brand_lock.add_argument("project_dir")

    p_prompt = sub.add_parser("build-prompt-pack")
    p_prompt.add_argument("project_dir")

    p_review = sub.add_parser("build-review-pack")
    p_review.add_argument("project_dir")

    p_convert = sub.add_parser("convert-source")
    p_convert.add_argument("project_dir")
    p_convert.add_argument("--engine", default="pymupdf4llm", choices=["pymupdf4llm", "markitdown", "mineru"])

    p_source_facts = sub.add_parser("build-source-facts")
    p_source_facts.add_argument("project_dir")

    p_source_quality = sub.add_parser("build-source-quality-report")
    p_source_quality.add_argument("project_dir")

    p_source_versions = sub.add_parser("build-source-version-report")
    p_source_versions.add_argument("project_dir")

    p_prepare_wiki = sub.add_parser("prepare-wiki")
    p_prepare_wiki.add_argument("project_dir")
    p_prepare_wiki.add_argument(
        "--engine",
        default="pymupdf4llm",
        choices=["pymupdf4llm", "markitdown", "mineru"],
    )

    p_verify_wiki = sub.add_parser("verify-wiki")
    p_verify_wiki.add_argument("project_dir")

    p_build_wiki_report = sub.add_parser("build-wiki-report")
    p_build_wiki_report.add_argument("project_dir")

    p_check_source_engines = sub.add_parser("check-source-engines")
    p_check_source_engines.add_argument("project_dir")

    p_plan_source_engines = sub.add_parser("plan-source-engine-eval")
    p_plan_source_engines.add_argument("project_dir")
    p_plan_source_engines.add_argument("--max-pages", type=int, default=5)

    p_scaffold_source_engine_results = sub.add_parser("scaffold-source-engine-eval-results")
    p_scaffold_source_engine_results.add_argument("project_dir")

    p_check_mineru = sub.add_parser("check-mineru")
    p_check_mineru.add_argument("project_dir")

    p_plan_mineru = sub.add_parser("plan-mineru-eval")
    p_plan_mineru.add_argument("project_dir")
    p_plan_mineru.add_argument("--max-pages", type=int, default=5)

    p_scaffold_mineru_results = sub.add_parser("scaffold-mineru-eval-results")
    p_scaffold_mineru_results.add_argument("project_dir")

    p_compile_outputs = sub.add_parser("compile-outputs")
    p_compile_outputs.add_argument("project_dir")
    p_compile_outputs.add_argument("--keep-existing", action="store_true")

    p_ima_import = sub.add_parser("import-ima-media")
    p_ima_import.add_argument("project_dir")
    p_ima_import.add_argument("--media-id", required=True)
    p_ima_import.add_argument("--title", required=True)
    p_ima_import.add_argument("--knowledge-base", default="")
    p_ima_import.add_argument("--knowledge-path", default="")
    p_ima_import.add_argument("--api-script")

    p_library = sub.add_parser("apply-library-update")
    p_library.add_argument("project_dir")
    p_library.add_argument("--library-dir")

    p_library_report = sub.add_parser("build-library-report")
    p_library_report.add_argument("library_dir")

    p_value_benchmark = sub.add_parser("build-value-benchmark")
    p_value_benchmark.add_argument("project_dir")
    p_value_benchmark.add_argument("--library-dir")

    p_contract = sub.add_parser("verify-contract")
    p_contract.add_argument("project_dir")
    p_contract.add_argument("--library-dir")
    p_contract.add_argument("--write-report", action="store_true")

    p_demo_contract = sub.add_parser("demo-contract")
    p_demo_contract.add_argument("project_dir")
    p_demo_contract.add_argument("--library-dir")

    p_run_phase1 = sub.add_parser("run-phase1")
    p_run_phase1.add_argument("project_dir")
    p_run_phase1.add_argument("--library-dir")
    p_run_phase1.add_argument("--engine", default="pymupdf4llm", choices=["pymupdf4llm", "markitdown", "mineru"])
    p_run_phase1.add_argument("--keep-existing", action="store_true")

    args = parser.parse_args()
    project_dir = Path(getattr(args, "project_dir", getattr(args, "project_name", ".")))

    if args.command == "init":
        init_project(project_dir)
    elif args.command == "validate-input":
        validate_input(project_dir)
    elif args.command == "scaffold-output":
        scaffold_output(project_dir)
    elif args.command == "check-claim-matrix":
        check_claim_matrix(project_dir)
    elif args.command == "check-brand-lock":
        check_brand_lock_sheet_draft(project_dir)
    elif args.command == "build-prompt-pack":
        build_prompt_pack(project_dir)
    elif args.command == "build-review-pack":
        build_review_pack(project_dir)
    elif args.command == "convert-source":
        convert_source(project_dir, engine=args.engine)
    elif args.command == "build-source-facts":
        build_source_facts(project_dir)
    elif args.command == "build-source-quality-report":
        build_source_quality_report(project_dir)
    elif args.command == "build-source-version-report":
        build_source_version_report(project_dir)
    elif args.command == "prepare-wiki":
        prepare_wiki_sources(project_dir, engine=args.engine)
    elif args.command == "verify-wiki":
        verify_wiki(project_dir)
    elif args.command == "build-wiki-report":
        build_wiki_report(project_dir)
    elif args.command == "check-source-engines":
        check_source_engines(project_dir)
    elif args.command == "plan-source-engine-eval":
        plan_source_engine_evaluation(project_dir, max_pages=args.max_pages)
    elif args.command == "scaffold-source-engine-eval-results":
        scaffold_source_engine_evaluation_results(project_dir)
    elif args.command == "check-mineru":
        check_mineru_readiness(project_dir)
    elif args.command == "plan-mineru-eval":
        plan_mineru_evaluation(project_dir, max_pages=args.max_pages)
    elif args.command == "scaffold-mineru-eval-results":
        scaffold_mineru_evaluation_results(project_dir)
    elif args.command == "compile-outputs":
        compile_structured_outputs(project_dir, keep_existing=args.keep_existing)
    elif args.command == "import-ima-media":
        api_script = Path(args.api_script) if args.api_script else None
        kwargs = {"api_script": api_script} if api_script else {}
        import_ima_media(
            project_dir,
            media_id=args.media_id,
            title=args.title,
            knowledge_base=args.knowledge_base,
            knowledge_path=args.knowledge_path,
            **kwargs,
        )
    elif args.command == "apply-library-update":
        library_dir = Path(args.library_dir) if args.library_dir else None
        apply_context_library_update(project_dir, library_dir=library_dir)
    elif args.command == "build-library-report":
        build_library_report(Path(args.library_dir))
    elif args.command == "build-value-benchmark":
        library_dir = Path(args.library_dir) if args.library_dir else None
        build_value_benchmark(project_dir, library_dir=library_dir)
    elif args.command == "verify-contract":
        library_dir = Path(args.library_dir) if args.library_dir else None
        report_path = project_dir / "contract_verification_report.md" if args.write_report else None
        verify_project_contract(project_dir, library_dir=library_dir, report_path=report_path)
    elif args.command == "demo-contract":
        library_dir = Path(args.library_dir) if args.library_dir else None
        run_demo_contract(project_dir, library_dir=library_dir)
    elif args.command == "run-phase1":
        library_dir = Path(args.library_dir) if args.library_dir else None
        run_phase1_workflow(
            project_dir,
            library_dir=library_dir,
            engine=args.engine,
            keep_existing=args.keep_existing,
        )


if __name__ == "__main__":
    main()
