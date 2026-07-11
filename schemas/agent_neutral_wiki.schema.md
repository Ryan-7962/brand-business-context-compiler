# Schema｜Agent-Neutral Wiki

This contract is the handoff boundary between deterministic source preparation and an active AI agent's semantic compilation. It preserves source traceability without claiming that structural validation proves semantic accuracy.

## Required Files

```text
wiki/
├── 00_index.md
├── uncertainties.md
└── documents/
    ├── S001.md
    └── <source-id>.md
```

- Create exactly one `wiki/documents/<source-id>.md` page for every unique `来源编号` in `converted_markdown/conversion_report.md`. Default PDF/PPT conversion may use multiple per-page rows for the same source; merge those rows by Source ID, original file, and transcript path.
- Keep `converted_markdown/` as evidence. The Wiki is a derived semantic layer, not a replacement for source transcripts, source facts, quality reports, or version reports.

## `wiki/00_index.md`

```markdown
# 批次索引

| Source ID | 文件名 | 内容概述 | 知识页 | 转写稿 | 版本线索 | 何时阅读 |
|---|---|---|---|---|---|---|
| S001 | <原始文件名> | <只写来源资料支持的简要事实摘要> | wiki/documents/S001.md | converted_markdown/source_transcripts/S001_<file>.md | <source_version_report.md 的相关线索或无明显冲突> | <需要该资料时的阅读建议> |
```

The index has exactly these seven non-empty columns and one row for every source. `知识页` must be `wiki/documents/<source-id>.md`; `转写稿` must be the existing transcript path declared for that source in `conversion_report.md`. Its factual summary must be source-backed; it does not replace the detailed knowledge page.

## `wiki/documents/<source-id>.md`

```markdown
# <文件名>｜<source-id>

## 文件概述

## 内容大纲

## 核心观点

## 关键事实

## 业务关系

## 不确定项

## 来源
```

Every page must contain every heading above, even when a section only records `[资料未提供]`.

### Traceability Labels

- Source-backed statements use `[来源: S001#page=1]` or `[来源: S001#slide=1]` with an anchor that exists in the same source's transcript. Do not cite another source or an unrecorded page/slide.
- Default pageable conversion must preserve every page/slide anchor declared by the conversion report. A multi-page MarkItDown transcript may expose only one aggregate anchor; cite only that real anchor and do not claim page-level traceability for the remaining physical pages.
- Agent synthesis that combines source-backed facts uses `[AI归纳]`; it must remain distinguishable from direct source statements.
- Information absent from the evidence uses `[资料未提供]`. Do not leave `待补充`, `待填写`, `TODO`, or template placeholders in the finished Wiki.
- Do not present automatic structural verification as a check of semantic accuracy, factual truth, or completeness of the agent's interpretation.

## `wiki/uncertainties.md`

```markdown
# 异常与不确定项

<只记录未读页面、转写/提取不确定性、版本冲突，或必须补充的资料。>
```

When there are no exceptions, the body is exactly:

```markdown
未发现需要人工处理的读取异常。
```

Rows in `source_quality_report.md` under `需要复核的页面` are Agent inspection candidates, not automatic human exceptions. Inspect the matching transcript and available screenshot, and list only items that remain unread or uncertain. For a multi-page MarkItDown source with fewer transcript anchors than physical pages, include the Source ID and the exact limitation `MarkItDown 未保留稳定页码/页边界`. Do not claim that there are no reading exceptions when this boundary limitation exists. Do not use this file as a generic task list or a restatement of the Wiki.

This file is an action queue for problems that block reliable source-to-Wiki compilation. Do not list a downstream business field merely because the source states it is not provided; preserve that fact in the matching document page. Do not add generic caveats about hypothetical formats, OCR, screenshots, or brand confirmation without a concrete issue in the supplied source.
