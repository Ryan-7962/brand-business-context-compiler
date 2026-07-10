from pathlib import Path
import sys
from unittest.mock import patch

from brand_skill.cli import main as cli_main
from brand_skill.wiki_workflow import prepare_wiki_sources


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
