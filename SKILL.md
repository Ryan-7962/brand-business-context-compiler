---
name: brand-business-context-compiler
description: Use when converting brand, marketing, sales, product, meeting, campaign, training, review, competitor, or channel materials into a local AI-readable context library.
---

# Brand / Business Context Compiler

## What This Skill Is

Use this skill to turn human-facing brand and business materials into a local, source-traceable Markdown context library for AI agents.

The first-stage deliverable is not a PDF/PPT summary, not a SaaS app, and not enterprise RAG. It is a local skill pack plus CLI workflow that produces structured evidence files and a static HTML knowledge report.

## First-Stage Boundary

Do:

- Compile PDF, PPTX, Markdown, TXT, DOCX, and optional MarkItDown-supported files from `source/`.
- Preserve source anchors, page or slide references, file creation time, file modification time, and low-confidence areas.
- Separate source-backed facts, AI-structured interpretation, pending confirmation, and missing context.
- Write a local `brand_context_library/` or caller-provided library directory.
- Generate `review/brand_review.html` for exception review and `library_report.html` for knowledge-map viewing.

Do not:

- Build a formal Web UI, login system, database service, or enterprise RAG stack.
- Treat every input as product material.
- Ask the user to confirm every extracted fact.
- Mark anything as brand-confirmed unless a human confirmation source exists.
- Put real private brand test material into public examples, docs, prompts, or schemas.

## Required Workflow

For a new project:

```bash
brand-skill init <project_dir>
```

Place source files under `source/`, then run:

```bash
brand-skill run-phase1 <project_dir> --library-dir <brand_context_library_dir>
```

The full first-stage loop is:

```text
source/
-> converted_markdown/source_transcripts/
-> converted_markdown/source_quality_report.md
-> converted_markdown/source_version_report.md
-> converted_markdown/source_facts/
-> outputs/02_document_profile.md
-> outputs/03_marketing_semantic_transcript.md
-> outputs/04_key_facts_and_claims.md
-> outputs/05_strategy_and_execution_map.md
-> outputs/06_risk_and_review_items.md
-> outputs/10_context_asset_index.md
-> outputs/11_context_library_update_plan.md
-> review/brand_review.html
-> brand_context_library/
-> brand_context_library/library_report.html
-> evaluation/direct_vs_skill_benchmark.md
-> contract_verification_report.md
```

## Source Conversion Engines

Default:

```bash
brand-skill convert-source <project_dir> --engine pymupdf4llm
```

Optional local candidate:

```bash
brand-skill convert-source <project_dir> --engine markitdown
```

MarkItDown is optional. If it is not installed, keep the default engine. Do not make MarkItDown or MinerU default only because a project is popular. Require local sample evidence:

```bash
brand-skill check-source-engines <project_dir>
brand-skill plan-source-engine-eval <project_dir> --max-pages 5
brand-skill scaffold-source-engine-eval-results <project_dir>
```

Use `_private_test_runs/` for real brand samples. Public examples must stay anonymous.

## Human Review Rule

The user should review only:

- Whether the file outline and core meaning are correct.
- Low-confidence OCR, image, chart, small-print, table, or page-boundary areas.
- Missing business information such as budget, timing, channel list, owner, evidence source, or conflicting versions.
- Key facts that would become risky if reused downstream.

Do not expose backend-heavy source-anchor tables, risk taxonomies, or asset IDs as the main review experience. Those remain machine-readable evidence.

## Verification Before Completion

Before claiming a project run is valid:

```bash
.venv/bin/python -m pytest tests/test_phase1_workflow.py -q
.venv/bin/python -m compileall src tests
brand-skill demo-contract examples/anonymous_marketing_campaign --library-dir /tmp/bmcc_demo_contract
brand-skill verify-contract examples/anonymous_marketing_campaign --library-dir /tmp/bmcc_demo_contract --write-report
```

Expected evidence includes:

- `converted_markdown/conversion_report.md`
- `converted_markdown/source_quality_report.md`
- `converted_markdown/source_version_report.md`
- `converted_markdown/source_engine_readiness_report.md`
- `converted_markdown/source_engine_eval_plan.md`
- `converted_markdown/source_engine_eval_results.md`
- `outputs/03_marketing_semantic_transcript.md`
- `outputs/10_context_asset_index.md`
- `outputs/11_context_library_update_plan.md`
- `review/brand_review.html`
- `library_report.html`
- `evaluation/direct_vs_skill_benchmark.md`
- `contract_verification_report.md`
