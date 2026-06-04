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
    "10_context_asset_index.md",
]


SECTION_CONFIG = [
    ("document-profile", "Document Profile Review", "02_document_profile.md"),
    ("key-facts", "Key Facts / Claims Review", "04_key_facts_and_claims.md"),
    ("strategy", "Strategy and Execution Review", "05_strategy_and_execution_map.md"),
    ("risk-review", "Risk and Review Items", "06_risk_and_review_items.md"),
    ("quality", "Quality Check", "09_quality_check_report.md"),
    ("context-assets", "Context Asset Index Review", "10_context_asset_index.md"),
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
    title = project_dir.name or "Marketing Review"
    html_text = _render_html(title, sections)
    output_path = review_dir / "brand_review.html"
    output_path.write_text(html_text, encoding="utf-8")
    print(f"Review pack created: {output_path}")


def _read_sections(outputs_dir: Path) -> dict[str, str]:
    return {filename: (outputs_dir / filename).read_text(encoding="utf-8") for filename in REQUIRED_OUTPUTS}


def _strip_title(markdown: str) -> str:
    lines = markdown.splitlines()
    if lines and lines[0].startswith("# "):
        return "\n".join(lines[1:]).strip()
    return markdown.strip()


def _markdown_to_html(markdown: str) -> str:
    text = _strip_title(markdown)
    if not text:
        return '<p class="muted">暂无内容</p>'
    return _render_blocks(text)


def _render_blocks(markdown: str) -> str:
    blocks: list[str] = []
    lines = markdown.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line:
            index += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index].strip())
                index += 1
            blocks.append(_render_table(table_lines))
            continue
        if line.startswith("### "):
            blocks.append(f"<h4>{html.escape(line[4:].strip())}</h4>")
        elif line.startswith("## "):
            blocks.append(f"<h3>{html.escape(line[3:].strip())}</h3>")
        elif line.startswith("# "):
            blocks.append(f"<h2>{html.escape(line[2:].strip())}</h2>")
        elif line.startswith("- "):
            items = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                items.append(f"<li>{_inline_markup(lines[index].strip()[2:])}</li>")
                index += 1
            blocks.append("<ul>" + "".join(items) + "</ul>")
            continue
        else:
            paragraph = [line]
            while index + 1 < len(lines):
                next_line = lines[index + 1].strip()
                if not next_line or next_line.startswith(("#", "|", "- ")):
                    break
                paragraph.append(next_line)
                index += 1
            blocks.append("<p>" + _inline_markup(" ".join(paragraph)) + "</p>")
        index += 1
    return "\n".join(blocks)


def _render_table(lines: list[str]) -> str:
    if not lines:
        return ""
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    rows = [row for row in rows if not all(set(cell) <= {"-", ":"} for cell in row)]
    if not rows:
        return ""
    header = rows[0]
    body = rows[1:]
    thead = "".join(f"<th>{html.escape(cell)}</th>" for cell in header)
    body_rows = []
    for row in body:
        cells = "".join(f"<td>{_inline_markup(cell)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return "<div class=\"table-wrap\"><table><thead><tr>" + thead + "</tr></thead><tbody>" + "".join(body_rows) + "</tbody></table></div>"


def _inline_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"(S\d{3}#page=\d+)", r'<span class="source-anchor">\1</span>', escaped)
    for status in ["已从来源资料提取", "AI 结构化转述，待确认", "AI 初步拟定，待品牌确认", "待补充", "不适用", "已品牌确认"]:
        escaped = escaped.replace(status, f"<span class=\"status-badge\">{status}</span>")
    if escaped in {"高", "中", "低"}:
        escaped = f'<span class="risk risk-{escaped}">{escaped}</span>'
    return escaped


def _count_term(sections: dict[str, str], term: str) -> int:
    return sum(text.count(term) for text in sections.values())


def _render_html(title: str, sections: dict[str, str]) -> str:
    escaped_title = html.escape(title)
    summary = {
        "project": title,
        "required_files": len(REQUIRED_OUTPUTS),
        "high_risk_count": _count_term(sections, "高"),
        "needs_supplement_count": _count_term(sections, "待补充"),
        "source_anchor_count": len(re.findall(r"S\d{3}#page=\d+", "\n".join(sections.values()))),
    }
    summary_json = html.escape(json.dumps(summary, ensure_ascii=False, indent=2))
    nav = "\n".join(f'<a href="#{section_id}">{label}</a>' for section_id, label, _filename in SECTION_CONFIG)
    section_html = "\n".join(
        _render_section(section_id, label, sections[filename]) for section_id, label, filename in SECTION_CONFIG
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}｜Brand Context Review</title>
  <style>
    :root {{
      --bg: #f6f7f9;
      --panel: #ffffff;
      --ink: #172026;
      --muted: #68737d;
      --line: #d9dee5;
      --accent: #0f766e;
      --risk: #b42318;
      --warn: #b54708;
      --ok: #067647;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }}
    header {{
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      padding: 14px 24px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(8px);
    }}
    h1 {{ margin: 0; font-size: 20px; }}
    h2 {{ margin: 0 0 14px; font-size: 22px; }}
    h3 {{ margin: 20px 0 10px; font-size: 16px; }}
    h4 {{ margin: 16px 0 8px; font-size: 14px; }}
    .layout {{
      display: grid;
      grid-template-columns: 240px minmax(0, 1fr);
      gap: 20px;
      max-width: 1440px;
      margin: 0 auto;
      padding: 20px;
    }}
    nav {{
      position: sticky;
      top: 74px;
      align-self: start;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
    }}
    nav a {{
      display: block;
      padding: 9px 10px;
      border-radius: 6px;
      color: var(--ink);
      text-decoration: none;
      font-size: 14px;
    }}
    nav a:hover {{ background: #eef6f4; color: var(--accent); }}
    section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
      margin-bottom: 18px;
    }}
    .summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 10px;
    }}
    .metric, .status-badge, .source-anchor, .risk {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      white-space: nowrap;
    }}
    .metric {{ background: #edf2f7; color: var(--ink); }}
    .status-badge {{ background: #eef6f4; color: var(--accent); }}
    .source-anchor {{ background: #eef2ff; color: #3730a3; }}
    .risk-高 {{ background: #fef3f2; color: var(--risk); }}
    .risk-中 {{ background: #fffaeb; color: var(--warn); }}
    .risk-低 {{ background: #ecfdf3; color: var(--ok); }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 760px; }}
    th, td {{ padding: 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; font-size: 13px; }}
    th {{ background: #f8fafc; font-weight: 650; }}
    code {{ background: #f1f5f9; padding: 1px 4px; border-radius: 4px; }}
    .review-controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
      padding-top: 12px;
      border-top: 1px solid var(--line);
    }}
    button {{
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      border-radius: 6px;
      padding: 7px 10px;
      cursor: pointer;
    }}
    button:hover {{ border-color: var(--accent); color: var(--accent); }}
    .download {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
    textarea {{
      width: 100%;
      min-height: 150px;
      margin-top: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 12px;
    }}
    .muted {{ color: var(--muted); }}
    @media (max-width: 820px) {{
      header {{ align-items: flex-start; flex-direction: column; }}
      .layout {{ grid-template-columns: 1fr; padding: 12px; }}
      nav {{ position: static; }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>{escaped_title}｜Brand Context Review</h1>
      <div class="summary">
        <span class="metric">Required files: {summary["required_files"]}</span>
        <span class="metric">High risk marks: {summary["high_risk_count"]}</span>
        <span class="metric">待补充: {summary["needs_supplement_count"]}</span>
        <span class="metric">Source anchors: {summary["source_anchor_count"]}</span>
      </div>
    </div>
    <button class="download" onclick="downloadDecisions()">Download review_decisions.json</button>
  </header>
  <div class="layout">
    <nav>{nav}</nav>
    <main>
      <section id="overview">
        <h2>Overview</h2>
        <p class="muted">本页面用于集中审核 Marketing 语义底稿和品牌上下文资产中的关键判断。若本页面由真实测试 PDF 生成，它仅属于本地私有测试结果，不代表正式 Skill 内置 demo。点击每个区块底部按钮可记录审核状态，并导出 review_decisions.json。</p>
        <textarea id="decision-json" readonly>{summary_json}</textarea>
      </section>
      {section_html}
    </main>
  </div>
  <script>
    const decisions = {{}};
    function setDecision(section, value) {{
      decisions[section] = {{
        decision: value,
        updated_at: new Date().toISOString()
      }};
      document.getElementById('decision-json').value = JSON.stringify({{
        summary: {json.dumps(summary, ensure_ascii=False)},
        decisions
      }}, null, 2);
    }}
    function downloadDecisions() {{
      const payload = document.getElementById('decision-json').value;
      const blob = new Blob([payload], {{ type: 'application/json;charset=utf-8' }});
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'review_decisions.json';
      anchor.click();
      URL.revokeObjectURL(url);
    }}
  </script>
</body>
</html>
"""


def _render_section(section_id: str, label: str, markdown: str) -> str:
    controls = f"""
    <div class="review-controls" data-section="{section_id}">
      <button onclick="setDecision('{section_id}', '确认')">确认</button>
      <button onclick="setDecision('{section_id}', '需修改')">需修改</button>
      <button onclick="setDecision('{section_id}', '待补充')">待补充</button>
      <button onclick="setDecision('{section_id}', '不采用')">不采用</button>
    </div>
    """
    return f'<section id="{section_id}"><h2>{html.escape(label)}</h2>{_markdown_to_html(markdown)}{controls}</section>'
