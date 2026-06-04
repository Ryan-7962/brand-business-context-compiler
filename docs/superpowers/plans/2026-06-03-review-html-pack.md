# Review HTML Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `brand-skill build-review-pack <project_dir>` to generate a local static Marketing review HTML from first-phase Markdown outputs.

**Architecture:** Implement a focused `review_pack.py` module that reads required output Markdown files, renders a self-contained HTML review console, and writes `review/brand_review.html`. The CLI delegates to this module. Tests verify required-file validation and generated section content.

**Tech Stack:** Python standard library only, existing `unittest` suite, no backend, no frontend framework.

---

### Task 1: Add Review Pack Tests

**Files:**
- Modify: `tests/test_phase1_workflow.py`

- [ ] **Step 1: Add imports**

Add:

```python
from brand_skill.review_pack import build_review_pack
```

- [ ] **Step 2: Add a helper that writes minimum default outputs**

Add this helper in `Phase1WorkflowTests`:

```python
    def _write_minimum_marketing_outputs(self, project_dir: Path) -> None:
        outputs = project_dir / "outputs"
        outputs.mkdir()
        files = {
            "02_document_profile.md": "# Document Profile\n\n| 字段 | 内容 | 信息状态 |\n|---|---|---|\n| 文件类型 | 活动方案 | AI 结构化转述，待确认 |\n",
            "04_key_facts_and_claims.md": "# Key Facts and Claims\n\n| 项目 | 内容 | 来源 | 信息状态 |\n|---|---|---|---|\n| 核心事实 | 活动目标为提升品牌声量 | S001#page=2 | 已从来源资料提取 |\n",
            "05_strategy_and_execution_map.md": "# Strategy and Execution Map\n\n## 核心目标\n\n提升品牌声量。\n",
            "06_risk_and_review_items.md": "# Risk and Review Items\n\n| Review ID | 类型 | 审核项 | 来源锚点 | 风险等级 | 建议处理 |\n|---|---|---|---|---|---|\n| R001 | 数据口径 | 声量目标缺少衡量口径 | S001#page=2 | 高 | 补充指标定义 |\n",
            "09_quality_check_report.md": "# Quality Check Report\n\n## 总体结论\n\n有条件通过。\n",
        }
        for filename, text in files.items():
            (outputs / filename).write_text(text, encoding="utf-8")
```

- [ ] **Step 3: Add success test**

Add:

```python
    def test_build_review_pack_creates_static_html(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            self._write_minimum_marketing_outputs(project_dir)

            with redirect_stdout(StringIO()):
                build_review_pack(project_dir)

            html = project_dir / "review" / "brand_review.html"
            text = html.read_text(encoding="utf-8")
            self.assertTrue(html.exists())
            self.assertIn("Document Profile Review", text)
            self.assertIn("Key Facts / Claims Review", text)
            self.assertIn("Strategy and Execution Review", text)
            self.assertIn("Risk and Review Items", text)
            self.assertIn("活动方案", text)
            self.assertIn("Download review_decisions.json", text)
```

- [ ] **Step 4: Add missing-file test**

Add:

```python
    def test_build_review_pack_requires_key_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            (project_dir / "outputs").mkdir()

            with redirect_stdout(StringIO()):
                with self.assertRaises(SystemExit):
                    build_review_pack(project_dir)
```

- [ ] **Step 5: Run the tests and see failure**

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Expected: import fails because `brand_skill.review_pack` does not exist.

### Task 2: Implement Review Pack Module

**Files:**
- Create: `src/brand_skill/review_pack.py`

- [ ] **Step 1: Create module with required-file validation**

Create `review_pack.py` with:

```python
"""Static HTML review pack generator."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

REQUIRED_OUTPUTS = [
    "02_document_profile.md",
    "04_key_facts_and_claims.md",
    "05_strategy_and_execution_map.md",
    "06_risk_and_review_items.md",
    "09_quality_check_report.md",
]


def build_review_pack(project_dir: Path) -> None:
    outputs_dir = project_dir / "outputs"
    missing = [filename for filename in REQUIRED_OUTPUTS if not (outputs_dir / filename).exists()]
    if missing:
        print("Missing required review inputs:")
        for filename in missing:
            print(f"- outputs/{filename}")
        raise SystemExit(1)

    review_dir = project_dir / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    sections = _read_sections(outputs_dir)
    html_text = _render_html(project_dir.name or "Marketing Review", sections)
    (review_dir / "brand_review.html").write_text(html_text, encoding="utf-8")
    print(f"Review pack created: {review_dir / 'brand_review.html'}")
```

- [ ] **Step 2: Add Markdown reading helpers**

Add:

```python
def _read_sections(outputs_dir: Path) -> dict[str, str]:
    return {filename: (outputs_dir / filename).read_text(encoding="utf-8") for filename in REQUIRED_OUTPUTS}


def _strip_title(markdown: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip()
    return markdown.strip()


def _markdown_to_html(markdown: str) -> str:
    escaped = html.escape(_strip_title(markdown))
    escaped = re.sub(r"^### (.+)$", r"<h4>\\1</h4>", escaped, flags=re.MULTILINE)
    escaped = re.sub(r"^## (.+)$", r"<h3>\\1</h3>", escaped, flags=re.MULTILINE)
    escaped = re.sub(r"^# (.+)$", r"<h2>\\1</h2>", escaped, flags=re.MULTILINE)
    escaped = escaped.replace("\n\n", "</p><p>")
    escaped = escaped.replace("\n", "<br>")
    return f"<p>{escaped}</p>" if escaped else "<p class=\"muted\">暂无内容</p>"


def _count_term(sections: dict[str, str], term: str) -> int:
    return sum(text.count(term) for text in sections.values())
```

- [ ] **Step 3: Add HTML renderer**

Add a self-contained HTML renderer with CSS and JavaScript for local review-state export.

- [ ] **Step 4: Run tests**

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Expected: all tests pass.

### Task 3: Expose CLI Command

**Files:**
- Modify: `src/brand_skill/cli.py`
- Modify: `README.md`

- [ ] **Step 1: Import function**

Add:

```python
from .review_pack import build_review_pack
```

- [ ] **Step 2: Add parser**

Add:

```python
    p_review = sub.add_parser("build-review-pack")
    p_review.add_argument("project_dir")
```

- [ ] **Step 3: Add command branch**

Add:

```python
    elif args.command == "build-review-pack":
        build_review_pack(project_dir)
```

- [ ] **Step 4: Update README CLI section**

Add:

```bash
brand-skill build-review-pack <project_dir>
```

- [ ] **Step 5: Run CLI manually**

Create scaffold outputs, fill required files, and run:

```bash
PYTHONPATH=src python3 -m brand_skill.cli build-review-pack /tmp/review_pack_check
```

Expected: `review/brand_review.html` is created.

### Task 4: Final Verification

**Files:**
- No new files expected.

- [ ] **Step 1: Run full tests**

Run:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

Expected: all tests pass.

- [ ] **Step 2: Run compile check**

Run:

```bash
PYTHONPATH=src python3 -m compileall -q src tests
```

Expected: exit code 0.

- [ ] **Step 3: Generate demo review pack if default outputs exist**

Run:

```bash
PYTHONPATH=src python3 -m brand_skill.cli build-review-pack examples/private_product_training_sample
```

Expected: It should fail until the demo has default Marketing outputs, which is acceptable for this task. Product demo migration is a separate task.

- [ ] **Step 4: Clean caches**

Run:

```bash
find . -type d -name __pycache__ -prune -exec rm -rf {} + && find . -type f -name '*.pyc' -delete
```
