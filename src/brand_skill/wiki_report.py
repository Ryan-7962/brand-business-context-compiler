"""Render a small offline HTML report from the prepared wiki."""

from __future__ import annotations

import html
import re
from pathlib import Path


def build_wiki_report(project_dir: Path) -> Path:
    """Write the user-facing wiki report and return its path."""
    wiki_dir = project_dir / "wiki"
    index_path = wiki_dir / "00_index.md"
    uncertainties_path = wiki_dir / "uncertainties.md"
    documents_dir = wiki_dir / "documents"
    required_paths = (index_path, uncertainties_path, documents_dir)
    if not all(path.exists() for path in required_paths):
        print("Missing prepared wiki files. Run prepare-wiki first.")
        raise SystemExit(1)

    report_path = wiki_dir / "report.html"
    report_path.write_text(
        _render_report(
            _render_batch_overview(index_path.read_text(encoding="utf-8")),
            _render_knowledge_pages(documents_dir),
            _render_markdown(uncertainties_path.read_text(encoding="utf-8"), skip_first_heading=True),
        ),
        encoding="utf-8",
    )
    print(f"Wiki report generated: {report_path}")
    return report_path


def _render_batch_overview(markdown: str) -> str:
    rows = _markdown_table_rows(markdown)
    if not rows:
        return "<p>未找到资料批次概览。</p>"
    columns = {name: index for index, name in enumerate(rows[0])}
    fields = ("文件名", "内容概述", "何时阅读")
    if not all(field in columns for field in fields):
        return "<p>未找到资料批次概览。</p>"
    body = []
    for row in rows[1:]:
        if len(row) != len(rows[0]):
            continue
        body.append(
            "<tr>"
            + "".join(f"<td>{html.escape(row[columns[field]])}</td>" for field in fields)
            + "</tr>"
        )
    return (
        "<table><thead><tr>"
        + "".join(f"<th>{field}</th>" for field in fields)
        + "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table>"
    )


def _markdown_table_rows(markdown: str) -> list[list[str]]:
    rows = []
    for line in markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        row = [cell.strip() for cell in stripped.strip("|").split("|")]
        if row and all(set(cell) <= {"-", ":"} for cell in row):
            continue
        rows.append(row)
    return rows


def _render_knowledge_pages(documents_dir: Path) -> str:
    pages = []
    for path in sorted(documents_dir.glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        pages.append(f"<article>{_render_markdown(markdown)}</article>")
    return "".join(pages) or "<p>暂无知识页。</p>"


def _render_markdown(markdown: str, *, skip_first_heading: bool = False) -> str:
    rendered = []
    first_heading_skipped = False
    for line in markdown.splitlines():
        if not line.strip():
            continue
        escaped = html.escape(line.strip())
        heading = re.fullmatch(r"(#{1,3})\s+(.+)", line.strip())
        if heading:
            if skip_first_heading and not first_heading_skipped:
                first_heading_skipped = True
                continue
            level = len(heading.group(1)) + 1
            rendered.append(f"<h{level}>{html.escape(heading.group(2))}</h{level}>")
        elif line.strip().startswith(("- ", "* ")):
            rendered.append(f"<p class=\"item\">{html.escape(line.strip()[2:])}</p>")
        else:
            rendered.append(f"<p>{escaped}</p>")
    return "".join(rendered)


def _render_report(batch_overview: str, knowledge_pages: str, uncertainties: str) -> str:
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>资料 Wiki</title>
<style>
body {{ margin: 0; background: #f7f7f5; color: #1e2926; font: 16px/1.6 -apple-system, BlinkMacSystemFont, \"PingFang SC\", sans-serif; }}
main {{ max-width: 920px; margin: 0 auto; padding: 40px 24px 64px; }}
section {{ border-top: 1px solid #ccd3cf; padding: 28px 0; }}
h1, h2, h3, h4 {{ line-height: 1.25; }} h1 {{ margin-top: 0; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; }} th, td {{ padding: 10px; text-align: left; border: 1px solid #dce2de; vertical-align: top; }} th {{ background: #edf2ee; }}
article {{ padding: 16px 0; border-bottom: 1px solid #dce2de; }} article:last-child {{ border-bottom: 0; }}
.item {{ padding-left: 1em; }} .item::before {{ content: \"- \"; margin-left: -1em; }}
</style>
</head>
<body><main>
<h1>资料 Wiki</h1>
<section><h2>资料批次概览</h2>{batch_overview}</section>
<section><h2>知识页</h2>{knowledge_pages}</section>
<section><h2>需要处理的问题</h2>{uncertainties}</section>
</main></body>
</html>
"""
