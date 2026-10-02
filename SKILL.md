---
name: brand-business-context-compiler
description: Use when converting brand or business materials into faithful AI-readable Markdown, either for one-off use or an explicitly requested local knowledge library.
---

# Brand / Business Context Compiler

## What This Skill Is

Use this skill to turn human-facing brand and business materials into source-traceable Markdown for AI agents. A Wiki is optional, not a prerequisite.

## Choose the Smallest Workflow

Default to one-off conversion when the user asks to convert or organize supplied files. Use `prompts/11_compile_once.md` and deliver `compiled/<source-id>.md` (or the requested path). Multiple files alone do not require a Wiki. Do not create library indexes, theme pages or HTML by default.

Use the Wiki workflow below only when the user explicitly requests a knowledge base, ongoing library updates or cross-document knowledge navigation. An explicit user choice overrides the default. Reuse one-off evidence when later adding it to a Wiki; do not repeat conversion unnecessarily.

The core model is:

```text
Raw Sources
-> Deterministic evidence preparation
-> Active Agent semantic compilation
-> One-off structured Markdown OR optional Agent-neutral Wiki
-> Downstream Agent outputs
```

The first-stage deliverable is not a PDF/PPT summary, not a SaaS app, and not enterprise RAG. It is a local skill pack with optional CLI helpers that prepares traceable evidence and guides an active Agent to compile structured Markdown.

## First-Stage Boundary

Do:

- Compile PDF, PPTX, Markdown, TXT, DOCX, and optional MarkItDown-supported files from `source/`.
- Preserve source anchors, page or slide references, file creation time, file modification time, and low-confidence areas.
- Separate source-backed facts, AI-structured interpretation, pending confirmation, and missing context.
- Deliver standalone structured Markdown; for an explicitly requested Wiki, produce `wiki/` with a batch index, source knowledge pages and real uncertainties.
- Keep source transcripts, source facts, quality reports, and version reports as traceability evidence.

Do not:

- Build a formal Web UI, login system, database service, or enterprise RAG stack.
- Treat every input as product material.
- Ask the user to confirm every extracted fact.
- Mark anything as brand-confirmed unless a human confirmation source exists.
- Put real private brand test material into public examples, docs, prompts, or schemas.

## One-Off Workflow (Default)

Read the supplied files with available host tools, or reuse existing source transcripts. Where the local CLI is available, `brand-skill convert-source <project_dir>` can prepare transcripts from `source/`; it is a helper, not a requirement to install the full pipeline.

Follow `prompts/11_compile_once.md`: inspect the actual content, write the detailed structured body with source references, and report only genuine unread regions. Deliver the MD without requiring a Wiki schema, `verify-wiki`, library maintenance or HTML. Apply the shared reading and human-review rules below in both modes.

## Wiki Workflow (Explicit Request)

For a new project:

```bash
brand-skill init <project_dir>
```

Place source files under `source/`, then prepare deterministic evidence:

```bash
.venv/bin/brand-skill prepare-wiki <project_dir>
```

The Wiki workflow is:

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

For image-only or low-text pages, read the actual screenshot with the host Agent's vision/OCR tools before compiling the document in either mode. A saved screenshot or page anchor alone is not evidence that its contents were read. Persist recovered content with its page anchor; list pages that remain unread instead of claiming complete coverage.

For visual evidence, separate verbatim text, observable appearance, and interpretation. Do not infer font names, permitted uses, color codes, or design rules from a logo/chart example unless the source states them. A model's claim that everything is clear is not a quality check; compare important statements against the image and preserve unresolved discrepancies.

For PPTX, check hidden slides and speaker notes as well as visible slide text. Default PDF exports may skip hidden slides; verify counts and source mappings before using an export for visual reading. Preserve hidden content and notes with their status, never as automatically approved copy. Batch large image requests to the host's actual limits, persist successful page evidence, and retry only unresolved regions. Prioritize product/claim conditions, numerical units and material table cells; do not turn every unread decorative label into a user confirmation task.

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

For multi-page MarkItDown input, the transcript can contain one aggregate anchor even when the conversion report records multiple physical pages. Only existing transcript anchors are traceable. Record the Source ID and `MarkItDown 未保留稳定页码/页边界` in the standalone document's reading-status note or `wiki/uncertainties.md`; do not describe unanchored physical pages as page-level traceable.

Use `_private_test_runs/` for real brand samples. Public examples must stay anonymous.

## Human Review Rule

After the Agent has inspected the transcript and available page/slide screenshots, the user should review only unresolved items:

- Which files were read, their page / slide coverage, and whether the outline is obviously wrong.
- OCR, image, chart, small-print, table, or page-boundary areas that remain unclear after Agent inspection.
- Missing business information such as budget, timing, channel list, owner, evidence source, or conflicting versions.
- Key facts that would become risky if reused downstream.

Do not ask the user to inspect every extracted fact. The review page should answer: what was read, what the outline is, what was not read clearly, and how to fix it. Backend-heavy source-anchor tables, risk taxonomies, or asset IDs remain machine-readable evidence.

Do not escalate a business field merely because the source says it is not provided. Keep that as a source-backed gap in the document knowledge page unless it prevents reliable interpretation of the current source. Do not invent generic OCR, layout, screenshot, or brand-confirmation warnings when no concrete reading problem exists.

If `evaluation/human_validation_packet.md` or `.html` exists in a private run, use it first for page / facts sampling, then write the final pass-rate summary back to `evaluation/quality_sampling_log.md`. Treat an existing `quality_sampling_log.md` as human validation evidence; `build-value-benchmark` preserves it instead of refreshing the template.

## Legacy Phase 1 Compatibility

Existing projects can continue to use `brand-skill run-phase1`. That legacy path retains its own `source_engine_eval_results.md`, `review/brand_review.html`, and `library_report.html` outputs. It is not the recommended workflow for new Agent-neutral Wiki work.

## Verification Before Completion

For one-off conversion, compare the file/page inventory, outline, body and key facts against actual evidence as specified in `prompts/11_compile_once.md`. Do not run `verify-wiki` against a standalone document.

Before claiming a Wiki is structurally valid:

```bash
.venv/bin/brand-skill verify-wiki <project_dir>
```

The verifier is intentionally limited. Semantic correctness, source interpretation, and any claim of accuracy require active Agent review and, where appropriate, human review of the underlying sources.
