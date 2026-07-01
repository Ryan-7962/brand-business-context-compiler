"""Static HTML exception review queue generator."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


REQUIRED_OUTPUTS = [
    "02_document_profile.md",
    "03_marketing_semantic_transcript.md",
    "06_risk_and_review_items.md",
]


SECTION_CONFIG = [
    ("source-status", "读取覆盖状态"),
    ("overview", "整个文件概述"),
    ("context", "文件大纲参考"),
    ("exceptions", "需要处理的问题"),
]


TEXT_REPLACEMENTS = {
    "Document Profile": "文件概述",
    "Marketing Semantic Transcript": "PDF 转述稿",
    "Semantic Transcript": "语义转述稿",
    "Key Facts and Claims": "核心事实和表达",
    "Key Facts / Claims": "核心事实和表达",
    "Key Facts": "核心事实",
    "Claims / Expressions": "可用表达 / 待确认表达",
    "Claim": "表达",
    "Strategy and Execution Map": "策略与执行梳理",
    "Strategy Map": "策略梳理",
    "Risk and Review Items": "未识别清楚、需要确认的点",
    "Risk Items": "风险项",
    "Quality Check Report": "识别质量检查",
    "Source Index": "来源索引",
    "Source Conversion Report": "来源转换报告",
    "Context Asset Index": "后台资产索引",
    "Brand Context Asset": "品牌上下文资产",
    "Page / Slide": "页 / 幻灯片",
    "Source Anchor": "来源位置",
    "Fact ID": "事实编号",
    "Claim ID": "表达编号",
    "Review ID": "确认项编号",
    "Missing Evidence": "缺失依据",
    "Brief Base Summary": "底稿概述",
    "Confirmed Source-backed Context": "来源中明确出现的内容",
    "AI-Structured Context Pending Confirmation": "AI 转述后待确认的内容",
    "Prompt-use Notes": "后续 AI 使用注意",
    "Completeness": "完整性",
    "Source Anchor Check": "来源位置检查",
    "Missing Context": "缺失信息",
    "Overall Assessment": "总体判断",
    "Big Idea": "核心创意主张",
    "轻量转写": "当前自动识别",
    "后续接 OCR/MinerU": "需要对照原图人工确认",
}


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
    sections = _read_sections(project_dir)
    title = project_dir.name or "Marketing Review"
    html_text = _render_html(title, sections)
    output_path = review_dir / "brand_review.html"
    output_path.write_text(html_text, encoding="utf-8")
    print(f"Review pack created: {output_path}")


def _read_sections(project_dir: Path) -> dict[str, str]:
    outputs_dir = project_dir / "outputs"
    sections = {filename: (outputs_dir / filename).read_text(encoding="utf-8") for filename in REQUIRED_OUTPUTS}
    converted_dir = project_dir / "converted_markdown"
    for filename in ["conversion_report.md", "source_quality_report.md"]:
        path = converted_dir / filename
        sections[filename] = path.read_text(encoding="utf-8") if path.exists() else ""
    return sections


def _extract_review_title(sections: dict[str, str], fallback: str) -> str:
    profile = sections.get("02_document_profile.md", "")
    first_line = profile.splitlines()[0].strip() if profile.splitlines() else ""
    if first_line.startswith("# "):
        title = first_line[2:].strip()
        for prefix in ["Document Profile｜", "Document Profile|", "文件概述｜", "文件概述|"]:
            if title.startswith(prefix):
                return title[len(prefix) :].strip()
        if title in TEXT_REPLACEMENTS:
            return fallback
        return title
    return fallback


def _display_text(text: str) -> str:
    for source, target in TEXT_REPLACEMENTS.items():
        text = text.replace(source, target)
    return text


def _extract_heading_section(markdown: str, heading_text: str) -> str:
    pattern = re.compile(rf"^##\s+(?:\d+\.\s*)?{re.escape(heading_text)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    next_heading = re.search(r"^##\s+", markdown[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(markdown)
    return markdown[match.end() : end].strip()


def _remove_source_noise(text: str) -> str:
    text = re.sub(r"(?m)^-\s*(Source Anchor|来源位置)[：:].*$", "", text)
    text = re.sub(r"(?m)^(Source Anchor|来源位置)[：:].*$", "", text)
    text = re.sub(r"S\d{3}#page=[\d,-]+", "", text)
    text = re.sub(r"来源[：:][^。\n]*(。)?", "", text)
    text = re.sub(r"信息状态[：:][^。\n]*(。)?", "", text)
    text = re.sub(r"AI 结构化转述，待确认", "待确认", text)
    text = re.sub(r"AI 初步拟定，待品牌确认", "待确认", text)
    text = re.sub(r"已从来源资料提取", "", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\s+。", "。", text)
    text = re.sub(r"。\s*。", "。", text)
    return text.strip()


def _extract_profile_summary(profile: str) -> str:
    file_position = _extract_heading_section(profile, "文件定位")
    if file_position:
        return _remove_source_noise(file_position)

    rows = _parse_markdown_table(profile)
    fields = []
    for row in rows:
        field = row.get("字段", "")
        value = row.get("内容", "")
        if field and value and field in {"文件类型", "文件目的", "业务阶段", "核心材料类型"}:
            fields.append(f"- {field}：{value}")
    return "\n".join(fields) if fields else "这份文件的整体概述仍需补充。"


def _extract_outline(transcript: str) -> str:
    outline = _extract_heading_section(transcript, "总体结构")
    if outline:
        return _remove_source_noise(outline)

    slide_titles = re.findall(r"^##\s+(Slide|Page)\s+\d+[｜|:：]\s*(.+?)\s*$", transcript, re.MULTILINE)
    if slide_titles:
        return "\n".join(f"- {title.strip()}" for _, title in slide_titles)

    page_blocks = re.findall(r"^##\s+Page / Slide\s+(\d+)\s*$", transcript, re.MULTILINE)
    if page_blocks:
        return "\n".join(f"- 第 {page_number} 页 / 幻灯片" for page_number in page_blocks)

    return "暂未稳定抽取出文件大纲，需要先补全文转述。"


def _extract_main_content(transcript: str) -> str:
    main_content = _extract_heading_section(transcript, "可读转述")
    if not main_content:
        main_content = transcript
    return _remove_source_noise(main_content)


def _extract_source_status(conversion_report: str, quality_report: str) -> str:
    rows = _parse_markdown_table(conversion_report)
    overview = _extract_heading_section(quality_report, "识别质量总览") or _extract_heading_section(conversion_report, "识别质量摘要")
    parts = []
    if overview:
        parts.append(_remove_source_noise(overview))
    else:
        parts.append("- 未生成读取质量总览。")

    source_rows = [
        row
        for row in rows
        if row.get("来源编号") and row.get("原始文件")
    ]
    if source_rows:
        lines = [
            "| 文件 | 页/Slide 范围 | 转写引擎 | 转写稿 | Source Facts |",
            "|---|---|---|---|---|",
        ]
        for row in source_rows:
            transcript_path = row.get("转写 Markdown", "未生成")
            lines.append(
                "| "
                + " | ".join(
                    [
                        row.get("原始文件", "未识别文件名"),
                        row.get("页码/Slide 范围", "未记录"),
                        row.get("转写引擎", "未记录"),
                        transcript_path,
                        _source_facts_path(transcript_path),
                    ]
                )
                + " |"
            )
        parts.append("\n".join(lines))
    else:
        parts.append("- 未生成来源文件清单。")

    unclear_rows = [
        row
        for row in _parse_markdown_table(quality_report)
        if row.get("低置信度说明") and not row.get("低置信度说明", "").startswith("无明显低置信度")
    ]
    if unclear_rows:
        parts.append(
            "\n".join(
                f"- {row.get('原始文件', '未识别文件')}：{row.get('低置信度说明')}。建议：{row.get('建议动作', '人工复核')}"
                for row in unclear_rows
            )
        )
    return "\n\n".join(parts)


def _source_facts_path(transcript_path: str) -> str:
    if not transcript_path.endswith(".md"):
        return "未生成"
    return f"converted_markdown/source_facts/{Path(transcript_path).stem}_source_facts.md"


def _extract_unclear_items(transcript: str, review_items: str) -> str:
    parts = []
    low_confidence = _extract_heading_section(transcript, "低置信度说明")
    if low_confidence:
        filtered_lines = [
            line
            for line in _remove_source_noise(low_confidence).splitlines()
            if _keep_user_confirmation_issue(line)
        ]
        if filtered_lines:
            parts.append("\n".join(filtered_lines))

    issues = _review_table_to_issue_list(review_items)
    if issues:
        parts.append(issues)
    elif review_items.strip() and "|" not in review_items:
        parts.append(_remove_source_noise(review_items))

    return "\n\n".join(parts) if parts else "目前没有额外标记需要人工修正的识别问题。"


def _has_exception_items(text: str) -> bool:
    normalized = text.strip()
    return bool(normalized and "目前没有额外标记" not in normalized)


def _parse_markdown_table(markdown: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in markdown.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    table_lines = []
    for line in lines:
        table_lines.append(line)
        if len(table_lines) > 1 and not line.startswith("|---"):
            continue
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    rows = [row for row in rows if not all(set(cell) <= {"-", ":"} for cell in row)]
    if len(rows) < 2:
        return []
    header = rows[0]
    return [dict(zip(header, row)) for row in rows[1:] if len(row) == len(header)]


def _review_table_to_issue_list(review_items: str) -> str:
    rows = _parse_markdown_table(review_items)
    items = []
    for row in rows:
        issue = row.get("审核项", "").strip()
        suggestion = (row.get("建议处理", "") or row.get("建议", "")).strip()
        if not issue or not _keep_user_confirmation_issue(issue):
            continue
        cleaned_issue = _clean_review_issue(issue)
        text = f"- {cleaned_issue}"
        if suggestion and suggestion not in {"人工复核 / 补充业务信息"}:
            text += f"。建议：{suggestion}"
        items.append(_remove_source_noise(text))
    return "\n".join(items)


def _keep_user_confirmation_issue(text: str) -> bool:
    if not text.strip():
        return False
    if _is_missing_context_issue(text):
        return True
    excluded_terms = [
        "外发",
        "法务",
        "敏感",
        "攻击",
        "竞品",
        "不能外发",
        "风险",
        "品牌口径",
        "正式",
        "策略",
        "预算",
        "功效",
        "人群定位",
        "数据口径",
        "归因",
    ]
    if any(term in text for term in excluded_terms):
        return False
    included_terms = ["未稳定", "错位", "小字", "图表", "图片", "OCR", "识别", "抽取", "会议", "日期", "参会", "决策"]
    return any(term in text for term in included_terms)


def _is_missing_context_issue(text: str) -> bool:
    return any(
        marker in text
        for marker in [
            "来源文本提示信息缺口",
            "资料没有提供",
            "暂未提供",
            "待补充",
            "需要品牌经理补充",
            "需要补充",
            "需补充",
        ]
    )


def _clean_review_issue(text: str) -> str:
    text = re.sub(r"^来源文本提示信息缺口[：:]\s*", "", text.strip())
    text = re.sub(r"^Slide\s+\d+\s*[｜|]\s*", "", text)
    text = re.sub(r"^Page\s+\d+\s*[｜|]\s*", "", text)
    return text.strip()


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
            blocks.append(f"<h4>{html.escape(_display_text(line[4:].strip()))}</h4>")
        elif line.startswith("## "):
            blocks.append(f"<h3>{html.escape(_display_text(line[3:].strip()))}</h3>")
        elif line.startswith("# "):
            blocks.append(f"<h2>{html.escape(_display_text(line[2:].strip()))}</h2>")
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
    thead = "".join(f"<th>{html.escape(_display_text(cell))}</th>" for cell in header)
    body_rows = []
    for row in body:
        cells = "".join(f"<td>{_inline_markup(cell)}</td>" for cell in row)
        body_rows.append(f"<tr>{cells}</tr>")
    return "<div class=\"table-wrap\"><table><thead><tr>" + thead + "</tr></thead><tbody>" + "".join(body_rows) + "</tbody></table></div>"


def _inline_markup(text: str) -> str:
    text = _display_text(text)
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
    display_title = _extract_review_title(sections, title)
    escaped_title = html.escape(display_title)
    js_title = json.dumps(display_title, ensure_ascii=False)
    profile = sections["02_document_profile.md"]
    transcript = sections["03_marketing_semantic_transcript.md"]
    review_items = sections["06_risk_and_review_items.md"]
    conversion_report = sections.get("conversion_report.md", "")
    quality_report = sections.get("source_quality_report.md", "")
    outline = _extract_outline(transcript)
    exceptions = _extract_unclear_items(transcript, review_items)
    has_exceptions = _has_exception_items(exceptions)
    review_content = {
        "source-status": _extract_source_status(conversion_report, quality_report),
        "overview": _extract_profile_summary(profile),
        "exceptions": exceptions if has_exceptions else "这份文件当前没有识别异常需要人工处理，可以先进入结构化知识库。",
        "context": outline,
    }
    unclear_count = max(0, exceptions.count("\n- ") + (1 if exceptions.startswith("- ") else 0)) if has_exceptions else 0
    nav = "\n".join(f'<a href="#{section_id}">{label}</a>' for section_id, label in SECTION_CONFIG)
    section_html = "\n".join(
        _render_section(section_id, label, review_content[section_id]) for section_id, label in SECTION_CONFIG
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}｜内容读取报告</title>
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
      grid-template-columns: 220px minmax(0, 1fr);
      gap: 20px;
      max-width: 1280px;
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
    .metric {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      white-space: nowrap;
    }}
    .metric {{ background: #edf2f7; color: var(--ink); }}
    section p, section li {{ font-size: 15px; }}
    section li {{ margin: 6px 0; }}
    section ul {{ padding-left: 22px; }}
    code {{ background: #f1f5f9; padding: 1px 4px; border-radius: 4px; }}
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
      <h1>{escaped_title}｜内容读取报告</h1>
      <div class="summary">
        <span class="metric">{'需要人工处理' if has_exceptions else '自动通过，无需人工处理'}</span>
        <span class="metric">待处理问题：{unclear_count}</span>
      </div>
    </div>
    <button class="download" onclick="downloadDecisions()">导出修正意见</button>
  </header>
  <div class="layout">
    <nav>{nav}</nav>
    <main>
      <section id="how-to-review">
        <h2>处理规则</h2>
        <ul>
          <li>先看读取覆盖状态和文件大纲，确认系统是否读完整个资料包。</li>
          <li>没有识别异常的文件默认进入结构化 Wiki，不需要逐项确认。</li>
          <li>只有图片、表格、小字、漏读、关键业务字段不明确等问题需要你处理。</li>
          <li>如果确实有问题，在底部写明页码、错误点和正确说法，或重新提供截图 / 原文件。</li>
        </ul>
      </section>
      {section_html}
      <section id="manual-feedback">
        <h2>人工修正</h2>
        <p class="muted">只在上方问题确实需要修正时填写。没有问题可以不处理。</p>
        <textarea id="manual-note" placeholder="例如：第 41 页表格第 3 列识别错了，正确内容是……"></textarea>
      </section>
    </main>
  </div>
  <script>
    function downloadDecisions() {{
      const payloadObject = {{
        "文件": {js_title},
        "人工修正": document.getElementById('manual-note') ? document.getElementById('manual-note').value : ""
      }};
      const payload = JSON.stringify(payloadObject, null, 2);
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
    return f'<section id="{section_id}"><h2>{html.escape(label)}</h2>{_markdown_to_html(markdown)}</section>'
