from pathlib import Path
import sys
from unittest.mock import patch

import pytest

from brand_skill.cli import main as cli_main
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


def create_conversion_report(project_dir: Path, source_ids: list[str]) -> None:
    converted = project_dir / "converted_markdown"
    converted.mkdir(parents=True)
    rows = [
        "# Source Conversion Report",
        "",
        "## Source Files",
        "",
        "| 来源编号 | 原始文件 | 转写 Markdown |",
        "|---|---|---|",
    ]
    for source_id in source_ids:
        rows.append(
            f"| {source_id} | {source_id.lower()}_source.md | "
            f"converted_markdown/source_transcripts/{source_id}_source.md |"
        )
    (converted / "conversion_report.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_valid_wiki(project_dir: Path, source_ids: list[str]) -> None:
    wiki = project_dir / "wiki"
    documents = wiki / "documents"
    documents.mkdir(parents=True)
    index_rows = [
        "# 批次索引",
        "",
        "| Source ID | 文件名 | 事实摘要 | 知识页 | 转写稿 | 版本线索 | 何时阅读 |",
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
