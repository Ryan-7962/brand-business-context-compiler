"""Source-to-Markdown conversion adapters."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_LIGHTWEIGHT_ENGINE = "pymupdf4llm"


def _safe_stem(path: Path) -> str:
    stem = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", path.stem, flags=re.UNICODE)
    return stem.strip("_") or "source"


def _iter_source_pdfs(project_dir: Path) -> list[Path]:
    source_dir = project_dir / "source"
    if not source_dir.exists():
        return []
    return sorted(source_dir.rglob("*.pdf"))


def _source_label(project_dir: Path, pdf: Path) -> str:
    """Use the source category folder as the stable transcript label when present."""
    source_dir = project_dir / "source"
    try:
        relative = pdf.relative_to(source_dir)
    except ValueError:
        return _safe_stem(pdf)
    if len(relative.parts) > 1:
        return _safe_stem(Path(relative.parts[0]))
    return _safe_stem(pdf)


def _file_timestamps(path: Path) -> tuple[str, str]:
    stat = path.stat()
    created_ts = getattr(stat, "st_birthtime", stat.st_ctime)
    modified_ts = stat.st_mtime
    return _format_timestamp(created_ts), _format_timestamp(modified_ts)


def _format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def convert_source(project_dir: Path, engine: str = SUPPORTED_LIGHTWEIGHT_ENGINE) -> None:
    """Convert source documents into Markdown transcripts.

    The first implementation intentionally keeps MinerU as an optional adapter
    placeholder. The default lightweight path uses PyMuPDF and pymupdf4llm.
    """
    if engine == "mineru":
        print("MinerU adapter is optional and not installed/configured in this lightweight build.")
        raise SystemExit(1)
    if engine != SUPPORTED_LIGHTWEIGHT_ENGINE:
        print(f"Unsupported source conversion engine: {engine}")
        raise SystemExit(1)

    try:
        import fitz
        import pymupdf4llm
    except ImportError as exc:
        print(f"Missing conversion dependency: {exc.name}")
        raise SystemExit(1) from exc

    pdfs = _iter_source_pdfs(project_dir)
    if not pdfs:
        print("No PDF source files found under source/.")
        raise SystemExit(1)

    converted_dir = project_dir / "converted_markdown"
    transcripts_dir = converted_dir / "source_transcripts"
    assets_root = converted_dir / "assets"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    assets_root.mkdir(parents=True, exist_ok=True)

    report_rows: list[list[str]] = []
    for index, pdf in enumerate(pdfs, start=1):
        source_id = f"S{index:03d}"
        safe_name = _source_label(project_dir, pdf)
        transcript_name = f"{source_id}_{safe_name}.md"
        asset_dir_name = f"{source_id}_{safe_name}"
        asset_dir = assets_root / asset_dir_name
        asset_dir.mkdir(parents=True, exist_ok=True)
        created_at, modified_at = _file_timestamps(pdf)

        doc = fitz.open(pdf)
        chunks = pymupdf4llm.to_markdown(
            str(pdf),
            page_chunks=True,
            page_separators=True,
            write_images=True,
            image_path=str(asset_dir),
            image_format="png",
        )

        lines = [
            f"# Source Transcript｜{pdf.name}",
            "",
            "## Source Metadata",
            f"- Source ID：{source_id}",
            f"- 原始文件：{pdf.name}",
            "- 文件类型：PDF",
            f"- 文件创建时间：{created_at}",
            f"- 文件修改时间：{modified_at}",
            "- 版本判断说明：若多份资料内容冲突，优先参考修改时间更新的文件；但关键品牌口径仍需进入冲突队列或人工复核，不自动覆盖。",
            f"- 页数：{doc.page_count}",
            f"- 转写引擎：{engine}",
            "- 转写方式：PyMuPDF / pymupdf4llm 文本解析 + 每页截图占位",
            "- 低置信度说明：视觉页、复杂表格、小字、角标和图片信息需结合页面截图复核。",
            "",
        ]

        for page_index, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            screenshot = asset_dir / f"page_{page_index:02d}.png"
            pix.save(screenshot)

            raw_text = page.get_text("text").strip()
            chunk = chunks[page_index - 1] if page_index - 1 < len(chunks) else {}
            md_text = chunk.get("text", "").strip() if isinstance(chunk, dict) else str(chunk).strip()
            tables = chunk.get("tables") or [] if isinstance(chunk, dict) else []
            image_count = len(page.get_images(full=True))
            drawing_count = len(page.get_drawings())

            table_quality = "中" if tables else "待复核"
            low_confidence = []
            if len(raw_text) < 20:
                low_confidence.append("可抽取文字较少")
            if image_count:
                low_confidence.append("含图片/视觉信息")
            low_confidence_text = "；".join(low_confidence) if low_confidence else "无明显低置信度"

            screenshot_rel = f"../assets/{asset_dir_name}/page_{page_index:02d}.png"
            lines.extend(
                [
                    f"## Page {page_index}",
                    f"- Source Anchor：{source_id}#page={page_index}",
                    f"- Page Screenshot：{screenshot_rel}",
                    f"- Extracted text chars：{len(raw_text)}",
                    f"- Embedded images detected：{image_count}",
                    f"- Vector drawings detected：{drawing_count}",
                    "",
                    "### Text",
                    md_text if md_text else "> 低置信度，未抽取到可用文本。请查看页面截图。",
                    "",
                    "### Images / Charts",
                    "| Asset ID | 位置 | 客观说明 | 文件路径/截图编号 | 待复核 |",
                    "|---|---|---|---|---|",
                    f"| P{page_index:02d}_FULL | 整页 | 页面完整截图，用于保留视觉信息和版面 | {screenshot_rel} | 是 |",
                    "",
                    "### Tables",
                    f"检测到 {len(tables)} 个表格结构，需人工复核。" if tables else "表格结构待人工复核。",
                    "",
                    "### Notes / Footnotes / Small Print",
                    "待人工复核页面截图中的角标、小字、页脚和备注。",
                    "",
                    "### Low Confidence / Need Review",
                    f"- {low_confidence_text}",
                    "",
                ]
            )

            report_rows.append(
                [
                    source_id,
                    pdf.name,
                    created_at,
                    modified_at,
                    f"converted_markdown/source_transcripts/{transcript_name}",
                    engine,
                    "文本解析 + 每页截图",
                    "否",
                    str(page_index),
                    table_quality,
                    "是",
                    "待复核",
                    low_confidence_text,
                    "检查页面截图与抽取文本是否一致",
                ]
            )

        (transcripts_dir / transcript_name).write_text("\n".join(lines), encoding="utf-8")
        doc.close()

    _write_conversion_report(converted_dir / "conversion_report.md", report_rows)
    print(f"Converted {len(pdfs)} source file(s) into {converted_dir}")


def _write_conversion_report(path: Path, rows: list[list[str]]) -> None:
    total_pages = sum(_page_count_from_range(row[8]) for row in rows)
    low_confidence_rows = [row for row in rows if row[12] != "无明显低置信度"]
    report = [
        "# Source Conversion Report",
        "",
        "## 识别质量摘要",
        "",
        f"- 总页数：{total_pages}",
        f"- 低置信度页数：{len(low_confidence_rows)}",
        "- 视觉/表格/小字限制：复杂版式、图片中文字、表格结构、角标、脚注和极小字号默认需要结合页面截图复核。",
        "- 人工复核建议：优先检查低置信度区域、含图片/图表页面、表格页、关键数字和品牌口径页。",
        "",
        "## Source Files",
        "",
        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        report.append("| " + " | ".join(cell.replace("|", "/") for cell in row) + " |")
    path.write_text("\n".join(report), encoding="utf-8")


def _page_count_from_range(page_range: str) -> int:
    match = re.search(r"(\d+)\s*-\s*(\d+)", page_range)
    if match:
        start, end = int(match.group(1)), int(match.group(2))
        return max(0, end - start + 1)
    numbers = re.findall(r"\d+", page_range)
    return len(numbers) if numbers else 1
