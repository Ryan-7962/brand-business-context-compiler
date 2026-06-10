"""CLI skeleton for Brand Marketing Context Compiler.

This is intentionally lightweight. Codex should expand it in the first development pass.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .contract_verifier import verify_project_contract
from .library_report import build_library_report
from .library_writer import apply_context_library_update
from .review_pack import build_review_pack
from .source_converter import convert_source
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
    p_convert.add_argument("--engine", default="pymupdf4llm", choices=["pymupdf4llm", "mineru"])

    p_library = sub.add_parser("apply-library-update")
    p_library.add_argument("project_dir")
    p_library.add_argument("--library-dir")

    p_library_report = sub.add_parser("build-library-report")
    p_library_report.add_argument("library_dir")

    p_contract = sub.add_parser("verify-contract")
    p_contract.add_argument("project_dir")
    p_contract.add_argument("--library-dir")
    p_contract.add_argument("--write-report", action="store_true")

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
    elif args.command == "apply-library-update":
        library_dir = Path(args.library_dir) if args.library_dir else None
        apply_context_library_update(project_dir, library_dir=library_dir)
    elif args.command == "build-library-report":
        build_library_report(Path(args.library_dir))
    elif args.command == "verify-contract":
        library_dir = Path(args.library_dir) if args.library_dir else None
        report_path = project_dir / "contract_verification_report.md" if args.write_report else None
        verify_project_contract(project_dir, library_dir=library_dir, report_path=report_path)


if __name__ == "__main__":
    main()
