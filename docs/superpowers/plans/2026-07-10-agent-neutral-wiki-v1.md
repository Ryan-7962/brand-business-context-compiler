# Agent-neutral Wiki V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the keyword-driven default path with a minimal workflow where deterministic tools prepare complete source evidence and Codex or WorkBuddy performs the semantic compilation into an agent-neutral Markdown Wiki.

**Architecture:** Keep the existing converters, source facts, quality report, and version report as the deterministic evidence layer. Add a small `prepare-wiki` entrypoint, a strict Wiki contract, a lightweight verifier/report builder, and a privacy-safe WorkBuddy package. Legacy outputs remain available but leave the recommended path.

**Tech Stack:** Python 3.10+, standard library, existing PyMuPDF/pymupdf4llm dependencies, Markdown Skill instructions, static HTML.

## Global Constraints

- Codex is the primary development, test, and personal-use environment.
- Tencent WorkBuddy must be able to import and invoke the distributed Skill package.
- Markdown Wiki is durable and agent-neutral.
- Deterministic code handles inventory, conversion, anchors, page coverage, timestamps, and version clues.
- AI agents handle outlines, core viewpoints, facts, business relationships, and uncertainty interpretation.
- Raw files remain the factual source of truth and are never overwritten.
- Human review is exception-driven.
- Do not add a Web App, RAG stack, model API orchestration, multi-user system, or downstream brief generators.
- Do not put private brand names, commercial data, or private test files in tracked packages.
- Do not delete legacy commands during this plan; revisit deletion only after V1 evidence exists.

---

### Task 1: Deterministic `prepare-wiki` Entry

**Files:**
- Create: `src/brand_skill/wiki_workflow.py`
- Modify: `src/brand_skill/cli.py`
- Test: `tests/test_wiki_workflow.py`

**Interfaces:**
- Consumes: `convert_source`, `build_source_facts`, `build_source_quality_report`, and `build_source_version_report`.
- Produces: `prepare_wiki_sources(project_dir: Path, engine: str = "pymupdf4llm") -> Path`.

- [ ] **Step 1: Write the failing workflow test**

```python
def test_prepare_wiki_runs_only_deterministic_steps(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    (project_dir / "source").mkdir(parents=True)
    with (
        patch("brand_skill.wiki_workflow.convert_source") as convert,
        patch("brand_skill.wiki_workflow.build_source_facts") as facts,
        patch("brand_skill.wiki_workflow.build_source_quality_report") as quality,
        patch("brand_skill.wiki_workflow.build_source_version_report") as versions,
    ):
        result = prepare_wiki_sources(project_dir)
    assert result == project_dir / "converted_markdown"
    convert.assert_called_once_with(project_dir, engine="pymupdf4llm")
    facts.assert_called_once_with(project_dir)
    quality.assert_called_once_with(project_dir)
    versions.assert_called_once_with(project_dir)
```

- [ ] **Step 2: Run the test and confirm it fails**

Run: `.venv/bin/python -m pytest tests/test_wiki_workflow.py::test_prepare_wiki_runs_only_deterministic_steps -q`

Expected: `ModuleNotFoundError: No module named 'brand_skill.wiki_workflow'`.

- [ ] **Step 3: Implement the minimal workflow**

```python
"""Prepare source evidence for an AI agent to compile into a Wiki."""

from pathlib import Path

from .source_converter import convert_source
from .source_facts import build_source_facts
from .source_quality import build_source_quality_report
from .source_versions import build_source_version_report


def prepare_wiki_sources(project_dir: Path, engine: str = "pymupdf4llm") -> Path:
    convert_source(project_dir, engine=engine)
    build_source_facts(project_dir)
    build_source_quality_report(project_dir)
    build_source_version_report(project_dir)
    converted_dir = project_dir / "converted_markdown"
    print(f"Source evidence prepared: {converted_dir}")
    print("Next: the active AI agent must compile wiki/ from the prepared evidence.")
    return converted_dir
```

- [ ] **Step 4: Add the recommended CLI command**

```python
p_prepare_wiki = sub.add_parser("prepare-wiki")
p_prepare_wiki.add_argument("project_dir")
p_prepare_wiki.add_argument(
    "--engine",
    default="pymupdf4llm",
    choices=["pymupdf4llm", "markitdown", "mineru"],
)

elif args.command == "prepare-wiki":
    prepare_wiki_sources(project_dir, engine=args.engine)
```

- [ ] **Step 5: Add a CLI dispatch test and run Task 1 tests**

Run: `.venv/bin/python -m pytest tests/test_wiki_workflow.py -q`

Expected: all Task 1 tests pass.

- [ ] **Step 6: Commit**

```bash
git add src/brand_skill/wiki_workflow.py src/brand_skill/cli.py tests/test_wiki_workflow.py
git commit -m "feat: add deterministic wiki preparation"
```

---

### Task 2: AI Semantic Wiki Contract and Verification

**Files:**
- Create: `prompts/10_compile_agent_neutral_wiki.md`
- Create: `schemas/agent_neutral_wiki.schema.md`
- Create: `src/brand_skill/wiki_verifier.py`
- Modify: `src/brand_skill/cli.py`
- Modify: `SKILL.md`
- Test: `tests/test_wiki_workflow.py`

**Interfaces:**
- Consumes: conversion report, every source transcript, source facts, quality report, and version report.
- Produces: `wiki/00_index.md`, one `wiki/documents/<source-id>.md` per source, and `wiki/uncertainties.md`.
- Produces: `verify_wiki(project_dir: Path) -> None`.

- [ ] **Step 1: Write failing tests for missing index entries, documents, headings, anchors, and placeholder text**

```python
def test_verify_wiki_requires_one_page_per_source(tmp_path: Path) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"])
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "00_index.md").write_text("# 批次索引\n\nS001\n", encoding="utf-8")
    (wiki / "uncertainties.md").write_text(
        "# 异常与不确定项\n\n未发现需要人工处理的读取异常。\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)
```

- [ ] **Step 2: Run the test and confirm the verifier is missing**

Run: `.venv/bin/python -m pytest tests/test_wiki_workflow.py::test_verify_wiki_requires_one_page_per_source -q`

Expected: collection fails because `brand_skill.wiki_verifier` does not exist.

- [ ] **Step 3: Write the canonical Wiki schema**

Every `wiki/documents/<source-id>.md` must contain:

```markdown
## 文件概述
## 内容大纲
## 核心观点
## 关键事实
## 业务关系
## 不确定项
## 来源
```

Source facts use `[来源: S001#page=1]` or `[来源: S001#slide=1]`. Agent synthesis uses `[AI归纳]`. Missing information uses `[资料未提供]`.

`wiki/00_index.md` has one row per source: Source ID, file name, factual summary, knowledge page, transcript, version clue, and when to read it.

`wiki/uncertainties.md` contains only unread pages, extraction uncertainty, version conflicts, or required missing information. With no exceptions, it says `未发现需要人工处理的读取异常。`.

- [ ] **Step 4: Write the AI compilation prompt**

The prompt must require the active agent to read every transcript completely, infer the real document structure from full context, avoid fixed taxonomies and keyword-only classification, write one knowledge page per source, then write the batch index and real uncertainties.

- [ ] **Step 5: Implement the minimal verifier**

```python
REQUIRED_HEADINGS = (
    "文件概述",
    "内容大纲",
    "核心观点",
    "关键事实",
    "业务关系",
    "不确定项",
    "来源",
)


def verify_wiki(project_dir: Path) -> None:
    issues = collect_wiki_issues(project_dir)
    if issues:
        print("Wiki verification failed:")
        for issue in issues:
            print(f"- {issue}")
        raise SystemExit(1)
    print("Wiki verification passed.")
```

The verifier checks coverage and traceability only. It does not claim semantic accuracy.

- [ ] **Step 6: Add `verify-wiki` to the CLI and finish focused tests**

Run: `.venv/bin/python -m pytest tests/test_wiki_workflow.py -q`

Expected: valid Wiki passes; missing source, document, heading, anchor, or unresolved placeholder fails.

- [ ] **Step 7: Rewrite `SKILL.md` around the two-stage workflow**

Recommended path:

```text
prepare-wiki
→ active Agent reads all prepared evidence
→ active Agent writes wiki/
→ build-wiki-report
→ verify-wiki
```

When the CLI is unavailable in WorkBuddy, the Skill uses WorkBuddy native file-reading tools, produces the same Wiki contract, and explicitly reports every unread file or page. Remove the old 12-output list and generic A/B templates from the recommended workflow.

- [ ] **Step 8: Commit**

```bash
git add SKILL.md prompts/10_compile_agent_neutral_wiki.md schemas/agent_neutral_wiki.schema.md src/brand_skill/wiki_verifier.py src/brand_skill/cli.py tests/test_wiki_workflow.py
git commit -m "feat: define agent semantic wiki contract"
```

---

### Task 3: Minimal Chinese Wiki Report

**Files:**
- Create: `src/brand_skill/wiki_report.py`
- Modify: `src/brand_skill/cli.py`
- Test: `tests/test_wiki_workflow.py`

**Interfaces:**
- Consumes: `wiki/00_index.md`, `wiki/documents/*.md`, and `wiki/uncertainties.md`.
- Produces: `build_wiki_report(project_dir: Path) -> Path`, writing `wiki/report.html`.

- [ ] **Step 1: Write a failing report test**

```python
def test_report_shows_only_user_facing_content(tmp_path: Path) -> None:
    create_valid_wiki(tmp_path)
    report = build_wiki_report(tmp_path)
    html = report.read_text(encoding="utf-8")
    assert "资料批次概览" in html
    assert "知识页" in html
    assert "需要处理的问题" in html
    assert "Fact ID" not in html
    assert "Review Priority" not in html
    assert "source_engine_eval" not in html
```

- [ ] **Step 2: Run the test and confirm the report module is missing**

Run: `.venv/bin/python -m pytest tests/test_wiki_workflow.py::test_report_shows_only_user_facing_content -q`

Expected: collection fails because `brand_skill.wiki_report` does not exist.

- [ ] **Step 3: Implement a dependency-free static report**

Use `html.escape` and a small Markdown subset. The page has only three sections: `资料批次概览`, `知识页`, and `需要处理的问题`. Keep CSS inline and load no remote resources. Do not expose engine reports, risk taxonomies, Fact IDs, asset IDs, contract status, or validation templates.

- [ ] **Step 4: Add `build-wiki-report` to the CLI and test HTML escaping/offline behavior**

Run: `.venv/bin/python -m pytest tests/test_wiki_workflow.py -q`

Expected: all Wiki workflow tests pass; source `<script>` is escaped; output contains no remote resource reference.

- [ ] **Step 5: Commit**

```bash
git add src/brand_skill/wiki_report.py src/brand_skill/cli.py tests/test_wiki_workflow.py
git commit -m "feat: add minimal wiki report"
```

---

### Task 4: WorkBuddy Package and Real Validation

**Files:**
- Create: `scripts/build_workbuddy_package.py`
- Create: `docs/workbuddy_validation_checklist.md`
- Modify: `README.md`
- Test: `tests/test_workbuddy_package.py`
- Private output only: `_private_test_runs/<chosen-package>/wiki/`

**Interfaces:**
- Consumes: canonical `SKILL.md`, AI compilation prompt, and Wiki schema.
- Produces: `dist/brand-business-context-compiler-workbuddy.zip` with only those three public files under one Skill directory.

- [ ] **Step 1: Write a failing package privacy test**

```python
def test_workbuddy_package_contains_only_public_files(tmp_path: Path) -> None:
    archive = build_workbuddy_package(REPO_ROOT, tmp_path)
    with ZipFile(archive) as package:
        names = sorted(package.namelist())
    assert names == [
        "brand-business-context-compiler/SKILL.md",
        "brand-business-context-compiler/references/agent_neutral_wiki.schema.md",
        "brand-business-context-compiler/references/compile_agent_neutral_wiki.md",
    ]
    assert all("_private_test_runs" not in name for name in names)
```

- [ ] **Step 2: Run the test and confirm the package builder is missing**

Run: `.venv/bin/python -m pytest tests/test_workbuddy_package.py -q`

Expected: collection fails because `scripts.build_workbuddy_package` does not exist.

- [ ] **Step 3: Implement the builder with `zipfile` only**

Copy exactly the canonical Skill, prompt, and schema into the ZIP. Do not walk the repository or include examples, docs, source data, Git history, or private test directories.

- [ ] **Step 4: Run Codex validation on one existing private multi-file package**

```bash
.venv/bin/brand-skill prepare-wiki _private_test_runs/<chosen-package>
.venv/bin/brand-skill build-wiki-report _private_test_runs/<chosen-package>
.venv/bin/brand-skill verify-wiki _private_test_runs/<chosen-package>
```

Between prepare and report, the active Codex agent reads every transcript and writes the Wiki. Inspect a small original-page sample for topic match, page coverage, working anchors, and real exceptions only.

- [ ] **Step 5: Build and inspect the WorkBuddy package**

```bash
.venv/bin/python scripts/build_workbuddy_package.py
unzip -l dist/brand-business-context-compiler-workbuddy.zip
```

Expected: exactly three files, no private path, no test brand term, and no raw data.

- [ ] **Step 6: Complete the user-assisted WorkBuddy validation**

Record: ZIP imports, Skill appears, a source folder triggers it, WorkBuddy creates the three Markdown artifacts, unread content is reported honestly, and one representative office task uses the Wiki. The user performs the company-computer UI import; Codex does not mark this requirement complete before that evidence exists.

- [ ] **Step 7: Run focused and regression verification**

```bash
.venv/bin/python -m pytest tests/test_wiki_workflow.py tests/test_workbuddy_package.py -q
.venv/bin/python -m pytest tests/test_phase1_workflow.py -q
.venv/bin/python -m compileall src tests scripts
git diff --check
```

Expected: all tests pass, compileall exits 0, and diff check has no output.

- [ ] **Step 8: Commit**

```bash
git add scripts/build_workbuddy_package.py docs/workbuddy_validation_checklist.md README.md tests/test_workbuddy_package.py
git commit -m "feat: package compiler skill for WorkBuddy"
```

## Plan Self-Review

- Deterministic evidence maps to Task 1.
- True Agent semantic compilation and the Wiki contract map to Task 2.
- Minimal Chinese user report maps to Task 3.
- Codex/WorkBuddy validation and privacy-safe distribution map to Task 4.
- Semantic correctness remains a real-source validation requirement; the verifier checks structure and traceability only.
- WorkBuddy completion remains unproven until the real import and task run happen on the company computer.
