"""Write context library update plans into a local Markdown library."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


VALID_LIBRARY_DIRS = {
    "brand",
    "product",
    "project",
    "asset",
    "language",
    "persona",
    "network",
    "case",
    "decision",
}


def apply_context_library_update(project_dir: Path, library_dir: Path | None = None) -> None:
    update_plan = project_dir / "outputs" / "11_context_library_update_plan.md"
    if not update_plan.exists():
        print("Missing required library update plan:")
        print("- outputs/11_context_library_update_plan.md")
        raise SystemExit(1)

    target_dir = library_dir or (project_dir / "brand_context_library")
    target_dir.mkdir(parents=True, exist_ok=True)
    _ensure_library_scaffold(target_dir)

    text = update_plan.read_text(encoding="utf-8")
    entries = _parse_new_context_entries(text)
    applied = []
    for entry in entries:
        action = entry.get("写入建议", "").strip()
        if action not in {"写入", "暂存"}:
            continue
        location = _normalize_location(entry.get("建议归档位置", ""))
        entry_path = _write_library_entry(target_dir, location, entry)
        applied.append((entry, entry_path))

    _append_evolution_log(target_dir, project_dir.name, applied)
    print(f"Context library updated: {target_dir}")
    print(f"Entries applied: {len(applied)}")


def _ensure_library_scaffold(library_dir: Path) -> None:
    for dirname in sorted(VALID_LIBRARY_DIRS | {"retrieval_maps"}):
        (library_dir / dirname).mkdir(parents=True, exist_ok=True)
    index = library_dir / "00_library_index.md"
    if not index.exists():
        index.write_text(
            "# Brand Context Library Index\n\n"
            "本目录用于沉淀长期品牌上下文。条目由 `11_context_library_update_plan.md` 写入或暂存。\n",
            encoding="utf-8",
        )
    log = library_dir / "evolution_log.md"
    if not log.exists():
        log.write_text("# Context Evolution Log\n\n", encoding="utf-8")


def _parse_new_context_entries(markdown: str) -> list[dict[str, str]]:
    section = _extract_section(markdown, "2. New Context Entries")
    if not section:
        return []
    table_lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    rows = _parse_table(table_lines)
    return rows


def _extract_section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return ""
    next_heading = re.search(r"^##\s+", markdown[match.end() :], re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(markdown)
    return markdown[match.end() : end].strip()


def _parse_table(lines: list[str]) -> list[dict[str, str]]:
    if len(lines) < 2:
        return []
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    rows = [row for row in rows if not all(set(cell) <= {"-", ":"} for cell in row)]
    if len(rows) < 2:
        return []
    header = rows[0]
    return [dict(zip(header, row)) for row in rows[1:] if len(row) == len(header)]


def _normalize_location(raw_location: str) -> str:
    first = raw_location.split("/")[0].strip().lower()
    return first if first in VALID_LIBRARY_DIRS else "project"


def _write_library_entry(library_dir: Path, location: str, entry: dict[str, str]) -> Path:
    entry_id = entry.get("Entry ID", "LCE000").strip() or "LCE000"
    title = entry.get("标题", "Untitled Context Entry").strip() or "Untitled Context Entry"
    slug = _slugify(f"{entry_id}-{title}")
    path = library_dir / location / f"{slug}.md"
    path.write_text(_render_entry(entry, location), encoding="utf-8")
    return path


def _render_entry(entry: dict[str, str], location: str) -> str:
    title = entry.get("标题", "Untitled Context Entry").strip() or "Untitled Context Entry"
    return "\n".join(
        [
            f"# {title}",
            "",
            f"- Entry ID: {entry.get('Entry ID', '').strip()}",
            f"- Library Section: {location}",
            f"- Stability: {entry.get('稳定性', '').strip()}",
            f"- Write Recommendation: {entry.get('写入建议', '').strip()}",
            f"- Source Asset: {entry.get('来源资产', '').strip()}",
            "",
            "## 内容摘要",
            "",
            entry.get("内容摘要", "").strip(),
            "",
        ]
    )


def _append_evolution_log(library_dir: Path, project_name: str, applied: list[tuple[dict[str, str], Path]]) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"## {timestamp}｜{project_name}", ""]
    if not applied:
        lines.append("- No context entries applied.")
    else:
        for entry, path in applied:
            lines.append(f"- {entry.get('Entry ID', '')}: {entry.get('标题', '')} -> `{path.relative_to(library_dir)}`")
    lines.append("")
    with (library_dir / "evolution_log.md").open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff_-]+", "", text)
    return text.strip("-_") or "context-entry"
