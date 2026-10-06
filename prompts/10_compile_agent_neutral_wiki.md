# Prompt｜Compile an Agent-Neutral Wiki

You are the active semantic compiler. Build the `wiki/` directory for this project from the prepared evidence. Your output must follow `schemas/agent_neutral_wiki.schema.md` exactly.

## Read Before Writing

Read all of the following before you classify or summarize anything:

1. `converted_markdown/conversion_report.md`
2. Every file in `converted_markdown/source_transcripts/`, completely
3. Matching files in `converted_markdown/source_facts/` as navigation aids; consult relevant rows when needed, rather than stuffing thousands of duplicate rows into the same context as a completely read transcript
4. `converted_markdown/source_quality_report.md`
5. `converted_markdown/source_version_report.md`

Treat the complete transcript as the primary reading evidence. Source facts help navigation and traceability, but do not replace complete reading. Treat quality-report review rows as Agent inspection candidates: inspect their transcript text and available page/slide screenshot first, then escalate only what remains unread or uncertain. Use the version report to expose conflicts or version clues.

An index entry is navigation, not evidence of existence or absence. When answering from selected sections, say what was not found in those sections; do not infer that the entire document lacks it. Consumer agreement percentages do not establish objective efficacy, self-testing, or third-party testing; preserve the source wording and determine methods only from actual report evidence.

If the host context limit prevents complete reading, split the document into anchored batches and merge their persisted evidence. Do not label content as `资料未提供` merely because it was omitted from the model context: report the actual unread scope and retry smaller inputs first. Do not invent approval requirements or absolute prohibitions on using source statements; distinguish source content, missing evidence, and business approval status without making unsupported policy decisions.

If a page has no usable extracted text, read its actual screenshot using available vision/OCR tools and persist the recovered content with that page's anchor. Converter control markers are not facts. Do not count a screenshot that has merely been generated as a visually read page. Separate visible text and literal visual descriptions from interpretation; do not invent fonts, color codes or usage rules from examples. Verify important visual claims against the image, and record pages still unread if the tools cannot read them.

For PPTX, inspect hidden-slide flags and speaker notes when the host tools allow it. A PDF exported from the same presentation may omit hidden slides; compare actual counts and retain the mapping to original slide/page anchors rather than silently renumbering. Preserve hidden slides and speaker notes as internal source evidence, not automatically approved public wording. An alternative Office renderer can help read content, but does not prove exact PowerPoint typography or layout.

Batch vision reads within the host's request-size limits. Record exactly which source anchors each response covers, reject wrong file/page mappings, and reuse successful evidence rather than rereading it. Read critical image text and conditions at adequate resolution; retry a specific unclear region before escalating it. Unread decorative background labels do not automatically block the whole document; unread claim conditions, data units or material table cells do.

## Compilation Rules

1. Infer each document's real structure, purpose, audience, and business role from its full context. Do not apply a fixed taxonomy or classify from filenames or keywords alone.
2. Write one complete `wiki/documents/<source-id>.md` page for every unique Source ID in the conversion report. When the default PDF/PPT converter emits one row per page, merge rows that share the same Source ID, original file, and transcript.
3. Include all required headings on every page. A section with no evidence must say `[资料未提供]` rather than silently inventing content or leaving a placeholder.
4. Mark direct source-backed statements only with a page or slide anchor that actually exists in the matching transcript, such as `[来源: S001#page=1]` or `[来源: S001#slide=1]`.
5. Mark cross-source organization, synthesis, or interpretation as `[AI归纳]`. Do not make synthesis look like a direct source claim.
6. Write `wiki/00_index.md` last, with one row per source and a factual source-backed summary, knowledge-page path, transcript path, version clue, and a practical cue for when another agent should read the page.
7. Write `wiki/uncertainties.md` from real evidence only. A row in the quality report is not automatically a human exception. Inspect the matching transcript and screenshot when available; list an item only when user action is required to make this source-to-Wiki compilation reliable: an unread or missing page, unresolved extraction uncertainty, a material version conflict, or missing source information that blocks faithful interpretation of this document. Information that the source explicitly says is not provided, such as a downstream campaign budget or execution owner, belongs in the document knowledge page as `[资料未提供]` when it does not block faithful Wiki compilation; do not escalate it to the batch uncertainty file. Do not add generic disclaimers about hypothetical PDF/PPT layout, OCR, screenshots, or brand confirmation when the supplied source was read completely and no concrete issue exists. For a multi-page MarkItDown source with fewer transcript anchors than physical pages, explicitly record its Source ID and `MarkItDown 未保留稳定页码/页边界`; do not claim page-level traceability for unanchored pages. When there are no exceptions, write `未发现需要人工处理的读取异常。`.

Do not claim that the resulting Wiki is semantically accurate merely because it passes `verify-wiki`; that command checks file coverage, required structure, source anchors, and unresolved placeholders only.
