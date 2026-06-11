"""Source-to-Markdown conversion adapters."""

from __future__ import annotations

import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree


SUPPORTED_LIGHTWEIGHT_ENGINE = "pymupdf4llm"
SUPPORTED_SOURCE_SUFFIXES = {".pdf", ".md", ".txt", ".docx", ".pptx"}
IGNORED_SOURCE_FILENAMES = {"README.md", ".DS_Store"}


def _safe_stem(path: Path) -> str:
    stem = re.sub(r"[^\w\u4e00-\u9fff.-]+", "_", path.stem, flags=re.UNICODE)
    return stem.strip("_") or "source"


def _iter_source_pdfs(project_dir: Path) -> list[Path]:
    source_dir = project_dir / "source"
    if not source_dir.exists():
        return []
    return sorted(source_dir.rglob("*.pdf"))


def _source_sort_key(project_dir: Path, source_file: Path) -> str:
    source_dir = project_dir / "source"
    try:
        return source_file.relative_to(source_dir).as_posix().lower()
    except ValueError:
        return source_file.as_posix().lower()


def _iter_unsupported_sources(project_dir: Path) -> list[Path]:
    source_dir = project_dir / "source"
    if not source_dir.exists():
        return []
    return sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file() and path.name not in IGNORED_SOURCE_FILENAMES and path.suffix.lower() not in SUPPORTED_SOURCE_SUFFIXES
    )


def _iter_source_text_documents(project_dir: Path) -> list[Path]:
    source_dir = project_dir / "source"
    if not source_dir.exists():
        return []
    supported_suffixes = {".md", ".txt"}
    return sorted(
        path
        for path in source_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in supported_suffixes and path.name not in IGNORED_SOURCE_FILENAMES
    )


def _iter_source_docx(project_dir: Path) -> list[Path]:
    source_dir = project_dir / "source"
    if not source_dir.exists():
        return []
    return sorted(source_dir.rglob("*.docx"))


def _iter_source_pptx(project_dir: Path) -> list[Path]:
    source_dir = project_dir / "source"
    if not source_dir.exists():
        return []
    return sorted(source_dir.rglob("*.pptx"))


def _source_label(project_dir: Path, source_file: Path) -> str:
    """Use the source category folder as the stable transcript label when present."""
    source_dir = project_dir / "source"
    try:
        relative = source_file.relative_to(source_dir)
    except ValueError:
        return _safe_stem(source_file)
    if len(relative.parts) > 1:
        return _safe_stem(Path(relative.parts[0]))
    return _safe_stem(source_file)


def _file_timestamps(path: Path) -> tuple[str, str]:
    stat = path.stat()
    created_ts = getattr(stat, "st_birthtime", stat.st_ctime)
    modified_ts = stat.st_mtime
    return _format_timestamp(created_ts), _format_timestamp(modified_ts)


def _format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _extract_docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as docx:
            document_xml = docx.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        print(f"Unable to read DOCX source: {path.name}")
        raise SystemExit(1) from exc

    root = ElementTree.fromstring(document_xml)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(f"{namespace}p"):
        texts = [node.text or "" for node in paragraph.iter(f"{namespace}t")]
        paragraph_text = "".join(texts).strip()
        if paragraph_text:
            paragraphs.append(paragraph_text)
    return "\n\n".join(paragraphs)


def _extract_pptx_slides(path: Path) -> list[str]:
    try:
        with zipfile.ZipFile(path) as pptx:
            slide_names = sorted(
                (name for name in pptx.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
                key=_slide_number,
            )
            slide_xmls = [pptx.read(name) for name in slide_names]
    except zipfile.BadZipFile as exc:
        print(f"Unable to read PPTX source: {path.name}")
        raise SystemExit(1) from exc

    namespace = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    slides: list[str] = []
    for slide_xml in slide_xmls:
        root = ElementTree.fromstring(slide_xml)
        texts = [node.text or "" for node in root.iter(f"{namespace}t")]
        slide_text = "\n".join(text.strip() for text in texts if text and text.strip())
        slides.append(slide_text)
    return slides


def _slide_number(path: str) -> int:
    match = re.search(r"slide(\d+)\.xml$", path)
    return int(match.group(1)) if match else 0


def _text_source_kind(path: Path) -> tuple[str, str, str]:
    suffix = path.suffix.lower()
    if suffix == ".md":
        return "Markdown", path.read_text(encoding="utf-8"), "Markdown 源稿转写"
    if suffix == ".txt":
        return "Plain Text", path.read_text(encoding="utf-8"), "Plain Text 源稿转写"
    if suffix == ".docx":
        return "Word Document", _extract_docx_text(path), "Word Document 源稿转写"
    raise ValueError(f"Unsupported text source: {path}")


def convert_source(project_dir: Path, engine: str = SUPPORTED_LIGHTWEIGHT_ENGINE) -> None:
    """Convert source documents into Markdown transcripts.

    The first implementation intentionally keeps MinerU as an optional adapter
    placeholder. The default lightweight path uses PyMuPDF and pymupdf4llm.
    """
    if engine == "mineru":
        print(
            "MinerU CLI is an optional high-fidelity converter and is not configured in this lightweight build. "
            "Install/configure MinerU, then run it with a command such as: "
            "mineru -p <input_path> -o <output_path> -b pipeline"
        )
        raise SystemExit(1)
    if engine != SUPPORTED_LIGHTWEIGHT_ENGINE:
        print(f"Unsupported source conversion engine: {engine}")
        raise SystemExit(1)

    unsupported_sources = _iter_unsupported_sources(project_dir)
    if unsupported_sources:
        print("Unsupported source file(s) found under source/:")
        source_dir = project_dir / "source"
        for source_file in unsupported_sources:
            try:
                label = source_file.relative_to(source_dir)
            except ValueError:
                label = source_file
            print(f"- {label}")
        raise SystemExit(1)

    pdfs = _iter_source_pdfs(project_dir)
    text_sources = [*_iter_source_text_documents(project_dir), *_iter_source_docx(project_dir)]
    pptx_sources = _iter_source_pptx(project_dir)
    supported_sources = sorted([*pdfs, *text_sources, *pptx_sources], key=lambda path: _source_sort_key(project_dir, path))
    if not supported_sources:
        print("No supported source files found under source/.")
        raise SystemExit(1)
    source_ids = {source: f"S{index:03d}" for index, source in enumerate(supported_sources, start=1)}

    converted_dir = project_dir / "converted_markdown"
    transcripts_dir = converted_dir / "source_transcripts"
    assets_root = converted_dir / "assets"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    assets_root.mkdir(parents=True, exist_ok=True)

    report_rows: list[list[str]] = []
    for text_source in text_sources:
        source_id = source_ids[text_source]
        safe_name = _source_label(project_dir, text_source)
        transcript_name = f"{source_id}_{safe_name}.md"
        created_at, modified_at = _file_timestamps(text_source)
        file_type, text, conversion_method = _text_source_kind(text_source)
        low_confidence_text = "无明显低置信度" if text.strip() else "源稿为空"

        lines = [
            f"# Source Transcript｜{text_source.name}",
            "",
            "## Source Metadata",
            f"- Source ID：{source_id}",
            f"- 原始文件：{text_source.name}",
            f"- 文件类型：{file_type}",
            f"- 文件创建时间：{created_at}",
            f"- 文件修改时间：{modified_at}",
            "- 版本判断说明：若多份资料内容冲突，优先参考修改时间更新的文件；但关键品牌口径仍需进入冲突队列或人工复核，不自动覆盖。",
            "- 页数：1",
            f"- 转写引擎：{engine}",
            f"- 转写方式：{conversion_method}",
            f"- 低置信度说明：{file_type} 源稿不包含真实 PDF / PPT 版式截图；若原始资料来自图片、表格或小字，请补充对应截图复核。",
            "",
            "## Page 1",
            f"- Source Anchor：{source_id}#page=1",
            f"- Page Screenshot：不适用（{file_type} source）",
            f"- Extracted text chars：{len(text.strip())}",
            "- Embedded images detected：0",
            "- Vector drawings detected：0",
            "",
            "### Text",
            text.strip() if text.strip() else "> 低置信度，源稿为空。",
            "",
            "### Images / Charts",
            f"{file_type} 源稿未生成页面截图；若来源包含图片、图表或长图，请补充原始视觉文件。",
            "",
            "### Tables",
            f"{file_type} 表格按文本保留，复杂表格仍需人工复核。",
            "",
            "### Notes / Footnotes / Small Print",
            f"{file_type} 源稿不保留原始版式小字信息；如来自 PDF / PPT，请以原始页面为准复核。",
            "",
            "### Low Confidence / Need Review",
            f"- {low_confidence_text}",
            "",
        ]
        (transcripts_dir / transcript_name).write_text("\n".join(lines), encoding="utf-8")

        report_rows.append(
            [
                source_id,
                text_source.name,
                created_at,
                modified_at,
                f"converted_markdown/source_transcripts/{transcript_name}",
                engine,
                conversion_method,
                "不适用",
                "1",
                "按文本保留",
                "不适用",
                "不适用",
                low_confidence_text,
                "检查 Markdown 源稿是否遗漏原始视觉信息",
            ]
        )

    for pptx in pptx_sources:
        source_id = source_ids[pptx]
        safe_name = _source_label(project_dir, pptx)
        transcript_name = f"{source_id}_{safe_name}.md"
        created_at, modified_at = _file_timestamps(pptx)
        slides = _extract_pptx_slides(pptx)
        low_confidence_text = "无明显低置信度" if any(slide.strip() for slide in slides) else "未抽取到 slide 文本"

        lines = [
            f"# Source Transcript｜{pptx.name}",
            "",
            "## Source Metadata",
            f"- Source ID：{source_id}",
            f"- 原始文件：{pptx.name}",
            "- 文件类型：PowerPoint",
            f"- 文件创建时间：{created_at}",
            f"- 文件修改时间：{modified_at}",
            "- 版本判断说明：若多份资料内容冲突，优先参考修改时间更新的文件；但关键品牌口径仍需进入冲突队列或人工复核，不自动覆盖。",
            f"- 页数：{len(slides)}",
            f"- 转写引擎：{engine}",
            "- 转写方式：PowerPoint 源稿转写",
            "- 低置信度说明：轻量路径只抽取 slide 文本，不保留真实版式、图片、图表、动画和备注；关键页面需结合原 PPT 复核。",
            "",
        ]

        for slide_index, slide_text in enumerate(slides, start=1):
            page_low_confidence = "无明显低置信度" if slide_text.strip() else "未抽取到 slide 文本"
            lines.extend(
                [
                    f"## Page {slide_index}",
                    f"- Source Anchor：{source_id}#page={slide_index}",
                    "- Page Screenshot：不适用（PowerPoint source）",
                    f"- Extracted text chars：{len(slide_text.strip())}",
                    "- Embedded images detected：待复核",
                    "- Vector drawings detected：待复核",
                    "",
                    "### Text",
                    slide_text.strip() if slide_text.strip() else "> 低置信度，未抽取到 slide 文本。",
                    "",
                    "### Images / Charts",
                    "PowerPoint 轻量转写未提取图片、图表和版式，请结合原 PPT 复核。",
                    "",
                    "### Tables",
                    "PowerPoint 表格按可见文本抽取，结构需人工复核。",
                    "",
                    "### Notes / Footnotes / Small Print",
                    "PowerPoint 备注、角标、小字和动画信息未完整保留，需人工复核。",
                    "",
                    "### Low Confidence / Need Review",
                    f"- {page_low_confidence}",
                    "",
                ]
            )
            report_rows.append(
                [
                    source_id,
                    pptx.name,
                    created_at,
                    modified_at,
                    f"converted_markdown/source_transcripts/{transcript_name}",
                    engine,
                    "PowerPoint 源稿转写",
                    "不适用",
                    str(slide_index),
                    "按文本保留",
                    "待复核",
                    "待复核",
                    page_low_confidence,
                    "检查原 PPT 版式、图片、图表、备注和小字信息",
                ]
            )

        (transcripts_dir / transcript_name).write_text("\n".join(lines), encoding="utf-8")

    if pdfs:
        try:
            import fitz
            import pymupdf4llm
        except ImportError as exc:
            print(f"Missing conversion dependency: {exc.name}")
            raise SystemExit(1) from exc

    for pdf in pdfs:
        source_id = source_ids[pdf]
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

    report_rows.sort(key=lambda row: row[0])
    _write_conversion_report(converted_dir / "conversion_report.md", report_rows)
    print(f"Converted {len(supported_sources)} source file(s) into {converted_dir}")


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
