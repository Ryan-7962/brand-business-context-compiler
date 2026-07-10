---
name: brand-business-context-compiler
description: Use when converting brand, marketing, sales, product, meeting, campaign, training, review, competitor, or channel materials into a local AI-readable context library.
---

# Brand / Business Context Compiler

## What This Skill Is

Use this skill to turn human-facing brand and business materials into a local, source-traceable Markdown Wiki for AI agents.

The core model is:

```text
Raw Sources
-> Deterministic evidence preparation
-> Active Agent semantic compilation
-> Agent-neutral Wiki
-> Downstream Agent outputs
```

The first-stage deliverable is not a PDF/PPT summary, not a SaaS app, and not enterprise RAG. It is a local skill pack plus CLI workflow that prepares traceable evidence and guides an active Agent to compile an Agent-neutral Wiki.

## First-Stage Boundary

Do:

- Compile PDF, PPTX, Markdown, TXT, DOCX, and optional MarkItDown-supported files from `source/`.
- Preserve source anchors, page or slide references, file creation time, file modification time, and low-confidence areas.
- Separate source-backed facts, AI-structured interpretation, pending confirmation, and missing context.
- Produce a local `wiki/` with a batch index, one knowledge page per source, and real uncertainties.
- Keep source transcripts, source facts, quality reports, and version reports as traceability evidence.

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

Place source files under `source/`, then prepare deterministic evidence:

```bash
.venv/bin/brand-skill prepare-wiki <project_dir>
```

The recommended two-stage workflow is:

```text
source/
-> prepare-wiki
-> active Agent reads every prepared transcript and evidence file
-> active Agent writes wiki/
-> build-wiki-report
-> verify-wiki
```

Use `prompts/10_compile_agent_neutral_wiki.md` and `schemas/agent_neutral_wiki.schema.md` for the active Agent step. `verify-wiki` validates coverage, required file structure, source anchors, and unresolved placeholders; it does not validate semantic accuracy.

When the CLI is unavailable in WorkBuddy, use WorkBuddy's native file-reading tools to read the same prepared evidence and produce the same `wiki/` contract. Explicitly record every unread file or page in `wiki/uncertainties.md`.

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

For multi-page MarkItDown input, the transcript can contain one aggregate anchor even when the conversion report records multiple physical pages. Only existing transcript anchors are traceable. Record the Source ID and `MarkItDown 未保留稳定页码/页边界` in `wiki/uncertainties.md`; do not describe unanchored physical pages as page-level traceable.

Use `_private_test_runs/` for real brand samples. Public examples must stay anonymous.

## Human Review Rule

The user should review only:

- Which files were read, their page / slide coverage, and whether the outline is obviously wrong.
- Low-confidence OCR, image, chart, small-print, table, or page-boundary areas.
- Missing business information such as budget, timing, channel list, owner, evidence source, or conflicting versions.
- Key facts that would become risky if reused downstream.

Do not ask the user to inspect every extracted fact. The review page should answer: what was read, what the outline is, what was not read clearly, and how to fix it. Backend-heavy source-anchor tables, risk taxonomies, or asset IDs remain machine-readable evidence.

If `evaluation/human_validation_packet.md` or `.html` exists in a private run, use it first for page / facts sampling, then write the final pass-rate summary back to `evaluation/quality_sampling_log.md`. Treat an existing `quality_sampling_log.md` as human validation evidence; `build-value-benchmark` preserves it instead of refreshing the template.

## Legacy Phase 1 Compatibility

Existing projects can continue to use `brand-skill run-phase1`. That legacy path retains its own `source_engine_eval_results.md`, `review/brand_review.html`, and `library_report.html` outputs. It is not the recommended workflow for new Agent-neutral Wiki work.

## Verification Before Completion

Before claiming a Wiki is structurally valid:

```bash
.venv/bin/brand-skill verify-wiki <project_dir>
```

The verifier is intentionally limited. Semantic correctness, source interpretation, and any claim of accuracy require active Agent review and, where appropriate, human review of the underlying sources.
