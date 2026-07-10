# Prompt｜Compile an Agent-Neutral Wiki

You are the active semantic compiler. Build the `wiki/` directory for this project from the prepared evidence. Your output must follow `schemas/agent_neutral_wiki.schema.md` exactly.

## Read Before Writing

Read all of the following before you classify or summarize anything:

1. `converted_markdown/conversion_report.md`
2. Every file in `converted_markdown/source_transcripts/`, completely
3. Every matching file in `converted_markdown/source_facts/`
4. `converted_markdown/source_quality_report.md`
5. `converted_markdown/source_version_report.md`

Treat the complete transcript as the primary reading evidence. Source facts help navigation and traceability, but do not replace complete reading. Use the quality report to expose unread or uncertain pages and the version report to expose conflicts or version clues.

## Compilation Rules

1. Infer each document's real structure, purpose, audience, and business role from its full context. Do not apply a fixed taxonomy or classify from filenames or keywords alone.
2. Write one complete `wiki/documents/<source-id>.md` page for every unique Source ID in the conversion report. When the default PDF/PPT converter emits one row per page, merge rows that share the same Source ID, original file, and transcript.
3. Include all required headings on every page. A section with no evidence must say `[资料未提供]` rather than silently inventing content or leaving a placeholder.
4. Mark direct source-backed statements only with a page or slide anchor that actually exists in the matching transcript, such as `[来源: S001#page=1]` or `[来源: S001#slide=1]`.
5. Mark cross-source organization, synthesis, or interpretation as `[AI归纳]`. Do not make synthesis look like a direct source claim.
6. Write `wiki/00_index.md` last, with one row per source and a factual source-backed summary, knowledge-page path, transcript path, version clue, and a practical cue for when another agent should read the page.
7. Write `wiki/uncertainties.md` from real evidence only. It may contain only unread pages, extraction uncertainty, version conflicts, or required missing information. For a multi-page MarkItDown source with fewer transcript anchors than physical pages, explicitly record its Source ID and `MarkItDown 未保留稳定页码/页边界`; do not claim page-level traceability for unanchored pages. When there are no exceptions, write `未发现需要人工处理的读取异常。`.

Do not claim that the resulting Wiki is semantically accurate merely because it passes `verify-wiki`; that command checks file coverage, required structure, source anchors, and unresolved placeholders only.
