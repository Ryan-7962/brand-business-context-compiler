"""Generate a marketer-friendly HTML overview for a local context library."""

from __future__ import annotations

import html
import json
from pathlib import Path

from .library_writer import VALID_LIBRARY_DIRS


SECTION_LABELS = {
    "brand": "品牌认知",
    "product": "产品资料",
    "project": "项目与活动",
    "asset": "素材资产",
    "language": "表达话术",
    "persona": "人群洞察",
    "network": "渠道网络",
    "case": "案例复盘",
    "decision": "关键决策",
}


def build_library_report(library_dir: Path) -> Path:
    if not library_dir.exists():
        print(f"Missing context library: {library_dir}")
        raise SystemExit(1)

    taxonomy = _parse_taxonomy(library_dir)
    entries = _collect_entries(library_dir, taxonomy)
    section_counts = _section_counts(library_dir, taxonomy)
    total_entries = sum(section_counts.values())
    queue_counts = {
        "冲突待判断": _count_queue_batches(library_dir / "review_queue" / "conflicts.md"),
        "旧知识待更新": _count_queue_batches(library_dir / "review_queue" / "updates.md"),
        "不进入长期库": _count_queue_batches(library_dir / "review_queue" / "do_not_promote.md"),
    }
    pending_count = queue_counts["冲突待判断"] + queue_counts["旧知识待更新"]
    recent_updates = _recent_evolution(library_dir / "evolution_log.md")
    reusable_notes = _retrieval_notes(library_dir / "retrieval_maps" / "source_packages.md")

    report_path = library_dir / "library_report.html"
    report_path.write_text(
        _render_report(
            total_entries,
            pending_count,
            section_counts,
            queue_counts,
            recent_updates,
            reusable_notes,
            taxonomy,
            entries,
        ),
        encoding="utf-8",
    )
    print(f"Library report generated: {report_path}")
    return report_path


def _parse_taxonomy(library_dir: Path) -> dict[str, dict[str, str]]:
    taxonomy_path = library_dir / "taxonomy.md"
    taxonomy = {
        section: {
            "id": section,
            "label": SECTION_LABELS.get(section, section),
            "description": "默认推荐分类",
            "source": "默认推荐",
            "status": "已启用",
        }
        for section in sorted(VALID_LIBRARY_DIRS)
    }
    if not taxonomy_path.exists():
        return taxonomy

    table_lines = [
        line.strip()
        for line in taxonomy_path.read_text(encoding="utf-8").splitlines()
        if line.strip().startswith("|")
    ]
    for row in _parse_markdown_table(table_lines):
        category_id = row.get("分类 ID", "").strip()
        if not category_id:
            continue
        taxonomy[category_id] = {
            "id": category_id,
            "label": row.get("展示名称", category_id).strip() or category_id,
            "description": row.get("说明", "").strip(),
            "source": row.get("来源", "").strip() or "AI 建议",
            "status": row.get("状态", "").strip() or "待确认",
        }
    return taxonomy


def _parse_markdown_table(lines: list[str]) -> list[dict[str, str]]:
    if len(lines) < 2:
        return []
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    rows = [row for row in rows if not all(set(cell) <= {"-", ":"} for cell in row)]
    if len(rows) < 2:
        return []
    header = rows[0]
    return [dict(zip(header, row)) for row in rows[1:] if len(row) == len(header)]


def _collect_entries(library_dir: Path, taxonomy: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    entries = []
    category_ids = set(taxonomy)
    category_ids.update(path.name for path in library_dir.iterdir() if path.is_dir())
    for category_id in sorted(category_ids):
        category_dir = library_dir / category_id
        if not category_dir.is_dir() or category_id in {"review_queue", "retrieval_maps"}:
            continue
        for markdown_path in sorted(category_dir.glob("*.md")):
            text = markdown_path.read_text(encoding="utf-8")
            entries.append(
                {
                    "id": markdown_path.stem,
                    "title": _first_heading(text) or markdown_path.stem,
                    "summary": _extract_summary(text),
                    "category": category_id,
                    "categoryLabel": taxonomy.get(category_id, {}).get("label", category_id),
                    "path": str(markdown_path.relative_to(library_dir)),
                    "status": "正常",
                }
            )
    return entries


def _section_counts(library_dir: Path, taxonomy: dict[str, dict[str, str]]) -> dict[str, int]:
    category_ids = set(taxonomy)
    category_ids.update(path.name for path in library_dir.iterdir() if path.is_dir())
    return {
        section: len(list((library_dir / section).glob("*.md")))
        for section in sorted(category_ids)
        if (library_dir / section).is_dir() and section not in {"review_queue", "retrieval_maps"}
    }


def _count_queue_batches(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("## "))


def _recent_evolution(path: Path) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    bullets = [line[2:].strip() for line in lines if line.startswith("- ")]
    return bullets[-6:]


def _retrieval_notes(path: Path) -> list[str]:
    if not path.exists():
        return []
    notes = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("##"):
            continue
        notes.append(stripped.lstrip("- ").strip())
    return notes[-6:]


def _render_report(
    total_entries: int,
    pending_count: int,
    section_counts: dict[str, int],
    queue_counts: dict[str, int],
    recent_updates: list[str],
    reusable_notes: list[str],
    taxonomy: dict[str, dict[str, str]],
    entries: list[dict[str, str]],
) -> str:
    categories = _report_categories(section_counts, taxonomy)
    data = {
        "categories": categories,
        "entries": entries,
        "queueCounts": queue_counts,
        "recentUpdates": recent_updates,
        "reusableNotes": reusable_notes,
    }
    embedded_data = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    sections = "\n".join(
        f"""
        <li>
          <span>{html.escape(taxonomy.get(section, {}).get("label", section))}</span>
          <strong>{count}</strong>
          <small>{html.escape(taxonomy.get(section, {}).get("source", ""))} · {html.escape(taxonomy.get(section, {}).get("status", ""))}</small>
        </li>
        """.strip()
        for section, count in section_counts.items()
    )
    queues = "\n".join(
        f"<li><span>{html.escape(label)}</span><strong>{count}</strong></li>"
        for label, count in queue_counts.items()
    )
    recent = _render_list(recent_updates, "还没有入库记录。")
    reusable = _render_list(reusable_notes, "还没有可复用场景说明。")
    context_map = _render_context_map(categories, entries)
    category_options = "\n".join(
        f'<option value="{html.escape(category["id"])}">{html.escape(category["label"])}</option>'
        for category in categories
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>品牌知识库概览</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1f2933;
      --muted: #5f6b7a;
      --line: #d9e0e8;
      --bg: #f6f8fb;
      --panel: #ffffff;
      --accent: #0f766e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: var(--bg);
      line-height: 1.55;
    }}
    header {{
      padding: 28px 32px 18px;
      background: var(--panel);
      border-bottom: 1px solid var(--line);
    }}
    h1 {{ margin: 0 0 8px; font-size: 28px; }}
    h2 {{ margin: 0 0 14px; font-size: 18px; }}
    main {{
      display: grid;
      gap: 16px;
      max-width: 1120px;
      margin: 0 auto;
      padding: 20px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}
    .metric, section, aside {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .metric strong {{
      display: block;
      color: var(--accent);
      font-size: 30px;
      line-height: 1.1;
    }}
    .metric span, .muted {{ color: var(--muted); }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .workbench {{
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.65fr);
      gap: 16px;
      align-items: start;
    }}
    ul {{ margin: 0; padding-left: 20px; }}
    .count-list {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
      padding: 0;
      list-style: none;
    }}
    .count-list li {{
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      background: #fbfcfe;
    }}
    .count-list small {{
      flex-basis: 100%;
      color: var(--muted);
      font-size: 12px;
    }}
    .context-map {{
      overflow: hidden;
    }}
    .map-canvas {{
      display: grid;
      gap: 14px;
    }}
    .map-center {{
      justify-self: center;
      border: 2px solid var(--accent);
      border-radius: 999px;
      padding: 16px 22px;
      font-weight: 700;
      color: var(--accent);
      background: #effcf9;
    }}
    .map-branches {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .map-category {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfcfe;
    }}
    .map-category > button, .map-entry {{
      width: 100%;
      border: 0;
      text-align: left;
      background: transparent;
      color: var(--ink);
      font: inherit;
      cursor: pointer;
    }}
    .map-category > button {{
      font-weight: 700;
    }}
    .map-entry {{
      display: block;
      margin-top: 8px;
      border-left: 3px solid #b7c5d4;
      padding: 7px 8px;
      background: #ffffff;
      border-radius: 6px;
    }}
    .map-entry span, .explorer-item span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    .explorer-controls {{
      display: grid;
      grid-template-columns: 1.4fr 1fr 1fr;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .explorer-controls input, .explorer-controls select {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 9px 10px;
      font: inherit;
      background: #ffffff;
    }}
    .explorer-list {{
      display: grid;
      gap: 8px;
    }}
    .explorer-item {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      text-align: left;
      background: #fbfcfe;
      color: var(--ink);
      font: inherit;
      cursor: pointer;
    }}
    .detail-panel dl {{
      display: grid;
      grid-template-columns: 72px minmax(0, 1fr);
      gap: 8px 12px;
      margin: 0;
    }}
    .detail-panel dt {{
      color: var(--muted);
    }}
    .detail-panel dd {{
      margin: 0;
      overflow-wrap: anywhere;
    }}
    @media (max-width: 760px) {{
      header {{ padding: 22px 18px 14px; }}
      main {{ padding: 14px; }}
      .metrics, .grid, .count-list, .workbench, .map-branches, .explorer-controls {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>品牌知识库概览</h1>
    <p class="muted">这页用于快速判断：现在沉淀了什么、还有哪些需要处理、后续哪些营销任务可以直接复用。</p>
  </header>
  <main>
    <div class="metrics">
      <div class="metric"><strong>已沉淀 {total_entries} 个知识条目</strong><span>来自品牌、产品、活动、话术、人群、案例等长期上下文。</span></div>
      <div class="metric"><strong>待处理 {pending_count} 项</strong><span>只统计需要人工判断的冲突和旧知识更新，不要求逐条确认全部内容。</span></div>
    </div>
    {context_map}
    <div class="workbench">
      <section class="knowledge-explorer" aria-label="Knowledge Explorer">
        <h2>Knowledge Explorer｜知识目录</h2>
        <div class="explorer-controls">
          <input data-role="searchInput" type="search" placeholder="搜索知识条目">
          <select data-role="categoryFilter" aria-label="分类筛选">
            <option value="all">全部分类</option>
            {category_options}
          </select>
          <select data-role="statusFilter" aria-label="状态筛选">
            <option value="all">全部状态</option>
            <option value="正常">正常</option>
            <option value="待更新">待更新</option>
            <option value="冲突">冲突</option>
          </select>
        </div>
        <div class="explorer-list" data-role="explorerList">
          {_render_explorer_items(entries)}
        </div>
      </section>
      <aside class="detail-panel" data-role="detailPanel">
        <h2>条目详情</h2>
        <p class="muted">点击知识地图或目录里的条目，查看摘要、分类、路径和状态。</p>
      </aside>
    </div>
    <section>
      <h2>知识分布</h2>
      <ul class="count-list">{sections}</ul>
    </section>
    <div class="grid">
      <section>
        <h2>需要处理</h2>
        <ul class="count-list">{queues}</ul>
      </section>
      <section>
        <h2>最近入库</h2>
        {recent}
      </section>
    </div>
    <section>
      <h2>后续可直接复用的场景</h2>
      {reusable}
    </section>
    <section>
      <h2>知识条目</h2>
      {_render_entry_list(entries)}
    </section>
    <script>
      window.__BRAND_CONTEXT_LIBRARY__ = {embedded_data};
    </script>
  </main>
</body>
</html>
"""


def _report_categories(section_counts: dict[str, int], taxonomy: dict[str, dict[str, str]]) -> list[dict[str, str | int]]:
    return [
        {
            "id": category_id,
            "label": taxonomy.get(category_id, {}).get("label", category_id),
            "description": taxonomy.get(category_id, {}).get("description", ""),
            "source": taxonomy.get(category_id, {}).get("source", ""),
            "status": taxonomy.get(category_id, {}).get("status", ""),
            "count": count,
        }
        for category_id, count in section_counts.items()
    ]


def _render_context_map(categories: list[dict[str, str | int]], entries: list[dict[str, str]]) -> str:
    branches = []
    for category in categories:
        category_entries = [entry for entry in entries if entry["category"] == category["id"]]
        entry_nodes = "\n".join(
            f"""
            <button class="map-entry" type="button" data-node-type="entry" data-entry-id="{html.escape(entry["id"])}">
              {html.escape(entry["title"])}
              <span>{html.escape(entry["status"])}</span>
            </button>
            """.strip()
            for entry in category_entries
        )
        branches.append(
            f"""
            <div class="map-category">
              <button type="button" data-node-type="category" data-category-id="{html.escape(str(category["id"]))}">
                {html.escape(str(category["label"]))}
                <span>{category["count"]} 个条目 · {html.escape(str(category["status"]))}</span>
              </button>
              {entry_nodes or '<p class="muted">暂无条目。</p>'}
            </div>
            """.strip()
        )
    return f"""
    <section class="context-map" aria-label="Brand Context Map">
      <h2>Brand Context Map｜知识地图</h2>
      <div class="map-canvas">
        <div class="map-center">品牌知识库</div>
        <div class="map-branches">{''.join(branches)}</div>
      </div>
    </section>
    """


def _render_explorer_items(entries: list[dict[str, str]]) -> str:
    if not entries:
        return '<p class="muted">还没有知识条目。</p>'
    return "".join(
        f"""
        <button class="explorer-item" type="button" data-entry-id="{html.escape(entry["id"])}">
          {html.escape(entry["title"])}
          <span>{html.escape(entry["categoryLabel"])} · {html.escape(entry["status"])}</span>
        </button>
        """.strip()
        for entry in entries
    )


def _render_list(items: list[str], empty_text: str) -> str:
    if not items:
        return f"<p class=\"muted\">{html.escape(empty_text)}</p>"
    rendered = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    return f"<ul>{rendered}</ul>"


def _render_entry_list(entries: list[dict[str, str]]) -> str:
    if not entries:
        return "<p class=\"muted\">还没有知识条目。</p>"
    rendered = "".join(
        f"<li><strong>{html.escape(entry['title'])}</strong><span>{html.escape(entry['categoryLabel'])}</span><p>{html.escape(entry['summary'])}</p></li>"
        for entry in entries
    )
    return f"<ul>{rendered}</ul>"


def _first_heading(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _extract_summary(markdown: str) -> str:
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == "## 内容摘要":
            summary_lines = []
            for next_line in lines[index + 1 :]:
                if next_line.startswith("## "):
                    break
                if next_line.strip():
                    summary_lines.append(next_line.strip())
            return " ".join(summary_lines).strip() or "暂无摘要。"
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("-"):
            return stripped
    return "暂无摘要。"
