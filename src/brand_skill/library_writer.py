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
    do_not_promote = _extract_section(text, "4. Do Not Promote")
    retrieval_notes = _extract_section(text, "6. Retrieval Notes")
    applied = []
    conflicts = []
    for entry in entries:
        action = entry.get("写入建议", "").strip()
        if action not in {"写入", "暂存"}:
            continue
        location = _normalize_location(entry.get("建议归档位置", ""))
        conflict_path = _find_conflict(target_dir, location, entry)
        if conflict_path:
            conflicts.append((entry, conflict_path))
            continue
        entry_path = _write_library_entry(target_dir, location, entry)
        applied.append((entry, entry_path))

    if conflicts:
        _append_conflict_queue(target_dir, project_dir.name, conflicts)
    if do_not_promote:
        _append_do_not_promote_queue(target_dir, project_dir.name, do_not_promote)
    if retrieval_notes:
        _append_retrieval_notes(target_dir, project_dir.name, retrieval_notes)
    _append_evolution_log(target_dir, project_dir.name, applied)
    print(f"Context library updated: {target_dir}")
    print(f"Entries applied: {len(applied)}")
    print(f"Conflicts queued: {len(conflicts)}")


def _ensure_library_scaffold(library_dir: Path) -> None:
    for dirname in sorted(VALID_LIBRARY_DIRS | {"retrieval_maps", "review_queue"}):
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


def _find_conflict(library_dir: Path, location: str, entry: dict[str, str]) -> Path | None:
    entry_id = entry.get("Entry ID", "LCE000").strip() or "LCE000"
    title = entry.get("标题", "Untitled Context Entry").strip() or "Untitled Context Entry"
    slug = _slugify(f"{entry_id}-{title}")
    exact_path = library_dir / location / f"{slug}.md"
    if exact_path.exists():
        return exact_path

    normalized_title = _normalize_match_text(title)
    for existing in (library_dir / location).glob("*.md"):
        text = existing.read_text(encoding="utf-8")
        first_heading = _first_heading(text)
        if _normalize_match_text(first_heading) == normalized_title:
            return existing
    return None


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


def _append_conflict_queue(library_dir: Path, project_name: str, conflicts: list[tuple[dict[str, str], Path]]) -> None:
    path = library_dir / "review_queue" / "conflicts.md"
    if not path.exists():
        path.write_text("# Context Library Conflict Queue\n\n", encoding="utf-8")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"## {timestamp}｜{project_name}", ""]
    for entry, existing_path in conflicts:
        lines.extend(
            [
                f"### {entry.get('Entry ID', '')}｜{entry.get('标题', '')}",
                "",
                f"- Suggested Section: {entry.get('建议归档位置', '')}",
                f"- Existing Entry: `{existing_path.relative_to(library_dir)}`",
                f"- Stability: {entry.get('稳定性', '')}",
                f"- Write Recommendation: {entry.get('写入建议', '')}",
                f"- Source Asset: {entry.get('来源资产', '')}",
                "",
                "#### New Summary",
                "",
                entry.get("内容摘要", "").strip(),
                "",
                "#### Required Action",
                "",
                "- 判断是补充已有条目、替换旧条目，还是作为新条目另存。",
                "",
            ]
        )
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def _append_do_not_promote_queue(library_dir: Path, project_name: str, content: str) -> None:
    path = library_dir / "review_queue" / "do_not_promote.md"
    if not path.exists():
        path.write_text("# Do Not Promote Queue\n\n", encoding="utf-8")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"## {timestamp}｜{project_name}", "", _clean_section_content(content), ""]
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def _append_retrieval_notes(library_dir: Path, project_name: str, content: str) -> None:
    path = library_dir / "retrieval_maps" / "source_packages.md"
    if not path.exists():
        path.write_text("# Source Package Retrieval Notes\n\n", encoding="utf-8")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [f"## {timestamp}｜{project_name}", "", _clean_section_content(content), ""]
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff_-]+", "", text)
    return text.strip("-_") or "context-entry"


def _clean_section_content(content: str) -> str:
    return content.strip() or "- No content."


def _first_heading(markdown: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _normalize_match_text(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()
