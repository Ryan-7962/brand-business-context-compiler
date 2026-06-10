"""Generate a marketer-friendly HTML overview for a local context library."""

from __future__ import annotations

import html
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

    section_counts = _section_counts(library_dir)
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
        _render_report(total_entries, pending_count, section_counts, queue_counts, recent_updates, reusable_notes),
        encoding="utf-8",
    )
    print(f"Library report generated: {report_path}")
    return report_path


def _section_counts(library_dir: Path) -> dict[str, int]:
    return {
        section: len(list((library_dir / section).glob("*.md")))
        for section in sorted(VALID_LIBRARY_DIRS)
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
) -> str:
    sections = "\n".join(
        f"""
        <li>
          <span>{html.escape(SECTION_LABELS.get(section, section))}</span>
          <strong>{count}</strong>
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
    .metric, section {{
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
      gap: 12px;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      background: #fbfcfe;
    }}
    @media (max-width: 760px) {{
      header {{ padding: 22px 18px 14px; }}
      main {{ padding: 14px; }}
      .metrics, .grid, .count-list {{ grid-template-columns: 1fr; }}
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
  </main>
</body>
</html>
"""


def _render_list(items: list[str], empty_text: str) -> str:
    if not items:
        return f"<p class=\"muted\">{html.escape(empty_text)}</p>"
    rendered = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    return f"<ul>{rendered}</ul>"
