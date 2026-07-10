from pathlib import Path
import sys
from unittest.mock import patch

import pytest

from brand_skill.cli import main as cli_main
from brand_skill.wiki_report import build_wiki_report
from brand_skill.wiki_verifier import verify_wiki
from brand_skill.wiki_workflow import prepare_wiki_sources


REQUIRED_HEADINGS = (
    "文件概述",
    "内容大纲",
    "核心观点",
    "关键事实",
    "业务关系",
    "不确定项",
    "来源",
)


def create_conversion_report(
    project_dir: Path,
    source_ids: list[str],
    *,
    page_ranges: dict[str, str] | None = None,
    engine: str = "pymupdf4llm",
) -> None:
    converted = project_dir / "converted_markdown"
    converted.mkdir(parents=True)
    transcripts = converted / "source_transcripts"
    transcripts.mkdir()
    rows = [
        "# Source Conversion Report",
        "",
        "## Source Files",
        "",
        "| 来源编号 | 原始文件 | 转写 Markdown | 转写引擎 | 页码/Slide 范围 |",
        "|---|---|---|---|---|",
    ]
    for source_id in source_ids:
        rows.append(
            f"| {source_id} | {source_id.lower()}_source.md | "
            f"converted_markdown/source_transcripts/{source_id}_source.md | "
            f"{engine} | {(page_ranges or {}).get(source_id, '1-1')} |"
        )
        (transcripts / f"{source_id}_source.md").write_text(
            f"# Source Transcript｜{source_id.lower()}_source.md\n\n"
            f"## Page 1\n\n- Source Anchor：{source_id}#page=1\n",
            encoding="utf-8",
        )
    (converted / "conversion_report.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    write_source_quality_report(project_dir)


def write_real_conversion_report(
    project_dir: Path,
    rows: list[tuple[str, str, str, str, str]],
) -> None:
    converted = project_dir / "converted_markdown"
    converted.mkdir(parents=True)
    lines = [
        "# Source Conversion Report",
        "",
        "## Source Files",
        "",
        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 | 外部来源 |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for source_id, filename, transcript, engine, page_range in rows:
        lines.append(
            f"| {source_id} | {filename} | 2026-01-01 | 2026-01-01 | 2026-01-01 | "
            f"{transcript} | {engine} | 文本解析 | 否 | {page_range} | 中 | 是 | "
            "待复核 | 无明显低置信度 | 检查抽取文本 | 本地 source/ |"
        )
    (converted / "conversion_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_source_transcript(project_dir: Path, source_id: str, page_numbers: list[int]) -> None:
    transcripts = project_dir / "converted_markdown" / "source_transcripts"
    transcripts.mkdir(parents=True, exist_ok=True)
    sections = [f"# Source Transcript｜{source_id.lower()}_source.md", ""]
    for page_number in page_numbers:
        sections.extend(
            [
                f"## Page {page_number}",
                "",
                f"- Source Anchor：{source_id}#page={page_number}",
                "",
            ]
        )
    (transcripts / f"{source_id}_source.md").write_text("\n".join(sections), encoding="utf-8")


def write_source_quality_report(project_dir: Path, review_anchors: list[str] | None = None) -> None:
    rows = [
        "# Source Quality Report",
        "",
        "## 需要复核的页面",
        "",
        "| Source Anchor | 原始文件 | 低置信度说明 | 建议动作 |",
        "|---|---|---|---|",
    ]
    if review_anchors:
        rows.extend(f"| {anchor} | source.md | 需要人工复核 | 人工复核 |" for anchor in review_anchors)
    else:
        rows.append("| - | - | 无明显低置信度页面 | 继续后续语义编译 |")
    (project_dir / "converted_markdown" / "source_quality_report.md").write_text(
        "\n".join(rows) + "\n",
        encoding="utf-8",
    )


def write_valid_wiki(project_dir: Path, source_ids: list[str]) -> None:
    wiki = project_dir / "wiki"
    documents = wiki / "documents"
    documents.mkdir(parents=True)
    index_rows = [
        "# 批次索引",
        "",
        "| Source ID | 文件名 | 内容概述 | 知识页 | 转写稿 | 版本线索 | 何时阅读 |",
        "|---|---|---|---|---|---|---|",
    ]
    for source_id in source_ids:
        index_rows.append(
            f"| {source_id} | {source_id.lower()}_source.md | 摘要 | "
            f"wiki/documents/{source_id}.md | "
            f"converted_markdown/source_transcripts/{source_id}_source.md | 无 | 需要该资料时 |"
        )
        document_sections = [f"# {source_id} 知识页", ""]
        for heading in REQUIRED_HEADINGS:
            document_sections.extend([f"## {heading}", ""])
            if heading == "关键事实":
                document_sections.extend([f"事实 [来源: {source_id}#page=1]", ""])
            elif heading == "不确定项":
                document_sections.extend(["无。", ""])
            else:
                document_sections.extend(["内容。", ""])
        (documents / f"{source_id}.md").write_text("\n".join(document_sections), encoding="utf-8")
    (wiki / "00_index.md").write_text("\n".join(index_rows) + "\n", encoding="utf-8")
    (wiki / "uncertainties.md").write_text(
        "# 异常与不确定项\n\n未发现需要人工处理的读取异常。\n",
        encoding="utf-8",
    )


def test_prepare_wiki_runs_only_deterministic_steps(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    (project_dir / "source").mkdir(parents=True)
    with (
        patch("brand_skill.wiki_workflow.convert_source") as convert,
        patch("brand_skill.wiki_workflow.build_source_facts") as facts,
        patch("brand_skill.wiki_workflow.build_source_quality_report") as quality,
        patch("brand_skill.wiki_workflow.build_source_version_report") as versions,
    ):
        result = prepare_wiki_sources(project_dir)
    assert result == project_dir / "converted_markdown"
    convert.assert_called_once_with(project_dir, engine="pymupdf4llm")
    facts.assert_called_once_with(project_dir)
    quality.assert_called_once_with(project_dir)
    versions.assert_called_once_with(project_dir)


def test_prepare_wiki_cli_dispatches_engine(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    with patch("brand_skill.cli.prepare_wiki_sources") as prepare:
        with patch.object(sys, "argv", ["brand-skill", "prepare-wiki", str(project_dir), "--engine", "mineru"]):
            cli_main()
    prepare.assert_called_once_with(project_dir, engine="mineru")


def test_verify_wiki_requires_one_page_per_source(tmp_path: Path) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"])
    wiki = tmp_path / "wiki"
    wiki.mkdir()
    (wiki / "00_index.md").write_text("# 批次索引\n\nS001\n", encoding="utf-8")
    (wiki / "uncertainties.md").write_text(
        "# 异常与不确定项\n\n未发现需要人工处理的读取异常。\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)


def test_verify_wiki_requires_index_entry_for_every_source(tmp_path: Path) -> None:
    create_conversion_report(tmp_path, source_ids=["S001", "S002"])
    write_valid_wiki(tmp_path, source_ids=["S001", "S002"])
    index = tmp_path / "wiki" / "00_index.md"
    index.write_text(
        "\n".join(line for line in index.read_text(encoding="utf-8").splitlines() if "| S002 |" not in line) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)


def test_verify_wiki_requires_all_document_headings(tmp_path: Path) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"])
    write_valid_wiki(tmp_path, source_ids=["S001"])
    document = tmp_path / "wiki" / "documents" / "S001.md"
    document.write_text(document.read_text(encoding="utf-8").replace("## 业务关系\n\n内容。\n\n", ""), encoding="utf-8")
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)


def test_verify_wiki_requires_source_anchor_on_every_document(tmp_path: Path) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"])
    write_valid_wiki(tmp_path, source_ids=["S001"])
    document = tmp_path / "wiki" / "documents" / "S001.md"
    document.write_text(document.read_text(encoding="utf-8").replace("[来源: S001#page=1]", "[AI归纳]"), encoding="utf-8")
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)


def test_verify_wiki_rejects_unresolved_placeholders(tmp_path: Path) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"])
    write_valid_wiki(tmp_path, source_ids=["S001"])
    document = tmp_path / "wiki" / "documents" / "S001.md"
    document.write_text(document.read_text(encoding="utf-8") + "\n待补充\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)


def test_verify_wiki_rejects_unknown_or_nonexistent_document_anchor(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_conversion_report(tmp_path, source_ids=["S001", "S002"])
    write_valid_wiki(tmp_path, source_ids=["S001", "S002"])
    document = tmp_path / "wiki" / "documents" / "S001.md"
    document.write_text(
        document.read_text(encoding="utf-8").replace(
            "事实 [来源: S001#page=1]",
            "事实 [来源: S001#page=9999]\n跨来源 [来源: S002#page=1]",
        ),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)
    output = capsys.readouterr().out
    assert "S001#page=9999 is not present in its transcript" in output
    assert "S002#page=1 does not belong to S001" in output


def test_verify_wiki_requires_every_conversion_range_anchor_in_its_transcript(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"], page_ranges={"S001": "1-2"})
    write_valid_wiki(tmp_path, source_ids=["S001"])
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)
    assert "S001 conversion range is missing transcript anchor S001#page=2" in capsys.readouterr().out


def test_verify_wiki_merges_real_per_page_conversion_rows_for_one_source(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    transcript = "converted_markdown/source_transcripts/S001_source.md"
    write_real_conversion_report(
        tmp_path,
        [
            ("S001", "s001_source.md", transcript, "pymupdf4llm", "1"),
            ("S001", "s001_source.md", transcript, "pymupdf4llm", "2"),
            ("S001", "s001_source.md", transcript, "pymupdf4llm", "3"),
        ],
    )
    write_source_transcript(tmp_path, "S001", [1, 2, 3])
    write_source_quality_report(tmp_path)
    write_valid_wiki(tmp_path, source_ids=["S001"])

    verify_wiki(tmp_path)

    assert "Wiki verification passed." in capsys.readouterr().out


@pytest.mark.parametrize(
    ("second_filename", "second_transcript", "conflicting_field"),
    [
        ("other.md", "converted_markdown/source_transcripts/S001_source.md", "原始文件"),
        ("s001_source.md", "converted_markdown/source_transcripts/S001_other.md", "转写 Markdown"),
    ],
)
def test_verify_wiki_rejects_conflicting_rows_for_one_source(
    tmp_path: Path,
    second_filename: str,
    second_transcript: str,
    conflicting_field: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    transcript = "converted_markdown/source_transcripts/S001_source.md"
    write_real_conversion_report(
        tmp_path,
        [
            ("S001", "s001_source.md", transcript, "pymupdf4llm", "1"),
            ("S001", second_filename, second_transcript, "pymupdf4llm", "2"),
        ],
    )
    write_source_transcript(tmp_path, "S001", [1, 2])
    write_source_quality_report(tmp_path)
    write_valid_wiki(tmp_path, source_ids=["S001"])

    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)

    assert f"S001 has conflicting {conflicting_field}" in capsys.readouterr().out


def test_verify_wiki_accepts_markitdown_aggregate_anchor_with_explicit_uncertainty(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    transcript = "converted_markdown/source_transcripts/S001_source.md"
    write_real_conversion_report(
        tmp_path,
        [("S001", "s001_source.md", transcript, "markitdown", "1-3")],
    )
    write_source_transcript(tmp_path, "S001", [1])
    write_source_quality_report(tmp_path, review_anchors=["S001#page=1"])
    write_valid_wiki(tmp_path, source_ids=["S001"])
    (tmp_path / "wiki" / "uncertainties.md").write_text(
        "# 异常与不确定项\n\n"
        "- S001 / S001#page=1：MarkItDown 未保留稳定页码/页边界。\n",
        encoding="utf-8",
    )

    verify_wiki(tmp_path)

    assert "Wiki verification passed." in capsys.readouterr().out


def test_verify_wiki_requires_markitdown_page_boundary_uncertainty(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    transcript = "converted_markdown/source_transcripts/S001_source.md"
    write_real_conversion_report(
        tmp_path,
        [("S001", "s001_source.md", transcript, "markitdown", "1-3")],
    )
    write_source_transcript(tmp_path, "S001", [1])
    write_source_quality_report(tmp_path)
    write_valid_wiki(tmp_path, source_ids=["S001"])

    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)

    assert (
        "uncertainties.md must document S001: MarkItDown 未保留稳定页码/页边界"
        in capsys.readouterr().out
    )


def test_verify_wiki_rejects_legacy_document_not_in_conversion_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"])
    write_valid_wiki(tmp_path, source_ids=["S001"])
    (tmp_path / "wiki" / "documents" / "S999.md").write_text("# 遗留页面\n", encoding="utf-8")
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)
    assert "Unknown knowledge page: wiki/documents/S999.md" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("column", "replacement"),
    [
        ("Source ID", ""),
        ("文件名", ""),
        ("内容概述", ""),
        ("知识页", "wiki/documents/S999.md"),
        ("转写稿", "converted_markdown/source_transcripts/S999_source.md"),
        ("版本线索", ""),
        ("何时阅读", ""),
    ],
)
def test_verify_wiki_requires_complete_index_fields_and_expected_paths(
    tmp_path: Path,
    column: str,
    replacement: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"])
    write_valid_wiki(tmp_path, source_ids=["S001"])
    index = tmp_path / "wiki" / "00_index.md"
    headers = index.read_text(encoding="utf-8").splitlines()[2].strip("|").split("|")
    values = index.read_text(encoding="utf-8").splitlines()[4].strip("|").split("|")
    values[headers.index(f" {column} ")] = f" {replacement} "
    index.write_text(
        "\n".join(
            [
                "# 批次索引",
                "",
                "|" + "|".join(headers) + "|",
                "|---|---|---|---|---|---|---|",
                "|" + "|".join(values) + "|",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)
    assert f"index row for S001 has an invalid {column}" in capsys.readouterr().out


def test_verify_wiki_rejects_index_with_missing_or_wrong_column(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"])
    write_valid_wiki(tmp_path, source_ids=["S001"])
    index = tmp_path / "wiki" / "00_index.md"
    index.write_text(
        index.read_text(encoding="utf-8").replace("内容概述 |", "事实摘要 |"),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)
    assert "must use exactly the required seven columns" in capsys.readouterr().out


def test_verify_wiki_requires_uncertainties_to_list_real_review_anchors(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_conversion_report(tmp_path, source_ids=["S001"])
    write_valid_wiki(tmp_path, source_ids=["S001"])
    write_source_quality_report(tmp_path, review_anchors=["S001#page=1"])
    with pytest.raises(SystemExit):
        verify_wiki(tmp_path)
    assert "uncertainties.md must list review anchor S001#page=1" in capsys.readouterr().out


def test_verify_wiki_accepts_a_complete_traceable_wiki(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    create_conversion_report(tmp_path, source_ids=["S001", "S002"])
    write_valid_wiki(tmp_path, source_ids=["S001", "S002"])
    verify_wiki(tmp_path)
    assert "Wiki verification passed." in capsys.readouterr().out


def test_verify_wiki_cli_dispatches_project_dir(tmp_path: Path) -> None:
    with patch("brand_skill.cli.verify_wiki") as verify:
        with patch.object(sys, "argv", ["brand-skill", "verify-wiki", str(tmp_path)]):
            cli_main()
    verify.assert_called_once_with(tmp_path)


def test_report_shows_only_user_facing_content(tmp_path: Path) -> None:
    write_valid_wiki(tmp_path, source_ids=["S001"])

    report = build_wiki_report(tmp_path)

    html = report.read_text(encoding="utf-8")
    assert "资料批次概览" in html
    assert "知识页" in html
    assert "需要处理的问题" in html
    assert "Fact ID" not in html
    assert "Review Priority" not in html
    assert "source_engine_eval" not in html


def test_report_escapes_wiki_markdown_and_loads_no_remote_resources(tmp_path: Path) -> None:
    write_valid_wiki(tmp_path, source_ids=["S001"])
    document = tmp_path / "wiki" / "documents" / "S001.md"
    document.write_text("# 知识页 <script>alert(1)</script>\n", encoding="utf-8")
    (tmp_path / "wiki" / "uncertainties.md").write_text(
        "# 异常与不确定项\n\n- <script>alert(2)</script>\n",
        encoding="utf-8",
    )

    report = build_wiki_report(tmp_path)

    html = report.read_text(encoding="utf-8")
    assert "<script>alert" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;script&gt;alert(2)&lt;/script&gt;" in html
    assert "<link " not in html
    assert " src=" not in html


def test_build_wiki_report_cli_dispatches_project_dir(tmp_path: Path) -> None:
    with patch("brand_skill.cli.build_wiki_report") as build_report:
        with patch.object(sys, "argv", ["brand-skill", "build-wiki-report", str(tmp_path)]):
            cli_main()
    build_report.assert_called_once_with(tmp_path)
