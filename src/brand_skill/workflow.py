"""Workflow helpers for the phase-one brand context skills pack."""

from __future__ import annotations

from pathlib import Path

REQUIRED_INPUTS = ["source"]
OUTPUT_FILES = [
    "00_source_index.md",
    "01_source_conversion_report.md",
    "02_document_profile.md",
    "03_marketing_semantic_transcript.md",
    "04_key_facts_and_claims.md",
    "05_strategy_and_execution_map.md",
    "06_risk_and_review_items.md",
    "07_ai_ready_marketing_brief_base.md",
    "08_review_pack.md",
    "09_quality_check_report.md",
    "10_context_asset_index.md",
    "11_context_library_update_plan.md",
]
PHASE1_PROMPT_FILES = [
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


def init_project(project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "source").mkdir(exist_ok=True)
    (project_dir / "brand_input").mkdir(exist_ok=True)
    (project_dir / "outputs").mkdir(exist_ok=True)
    guide = project_dir / "brand_input" / "README.md"
    if not guide.exists():
        guide.write_text(
            "# Brand Input\n\n"
            "可选：如果已有人工审核结果，请放入 `review_decisions.json`。\n\n"
            "如果没有审核结果，Skill 会先根据来源资料生成 "
            "`outputs/08_review_pack.md` 和 `review/brand_review.html`；"
            "默认只处理识别异常，不要求逐条确认所有 Markdown。\n",
            encoding="utf-8",
        )
    print(f"Initialized project at {project_dir}")


def validate_input(project_dir: Path) -> None:
    missing = [item for item in REQUIRED_INPUTS if not (project_dir / item).exists()]
    if missing:
        print("Missing required inputs:")
        for item in missing:
            print(f"- {item}")
        raise SystemExit(1)
    print("Input validation passed.")


def scaffold_output(project_dir: Path) -> None:
    out_dir = project_dir / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    for filename in OUTPUT_FILES:
        path = out_dir / filename
        if not path.exists():
            title = filename.removesuffix(".md").replace("_", " ").title()
            path.write_text(f"# {title}\n\n待生成。\n", encoding="utf-8")
    print(f"Output scaffold created at {out_dir}")


def build_prompt_pack(project_dir: Path) -> None:
    prompt_bundle = project_dir / "prompt_bundle.md"
    prompts_dir = project_dir / "prompts"
    sections = [
        "# Prompt Bundle｜Phase 1 Brand Marketing Context Compiler",
        "",
        "按以下顺序执行第一阶段品牌上下文资产编译提示词。第二阶段派生 brief prompt 不纳入本 bundle。",
        "",
    ]
    for filename in PHASE1_PROMPT_FILES:
        path = prompts_dir / filename
        if not path.exists():
            continue
        sections.extend([f"<!-- {filename} -->", path.read_text(encoding="utf-8").strip(), ""])
    prompt_bundle.write_text("\n".join(sections), encoding="utf-8")
    print(f"Prompt bundle created: {prompt_bundle}")
