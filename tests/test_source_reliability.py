from pathlib import Path
from types import SimpleNamespace
import os

import pytest

from brand_skill.source_converter import (
    _extract_pptx_slides,
    _iter_source_docx,
    _iter_source_pdfs,
    _iter_source_pptx,
    convert_source,
)
from brand_skill.source_facts import _fact_candidates
from brand_skill.source_versions import _likely_version_groups, _normalize_version_key


def test_pptx_preserves_display_order_hidden_state_and_speaker_notes(tmp_path: Path) -> None:
    from zipfile import ZipFile

    source = tmp_path / "anonymous.pptx"
    p = "http://schemas.openxmlformats.org/presentationml/2006/main"
    a = "http://schemas.openxmlformats.org/drawingml/2006/main"
    r = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    rel = "http://schemas.openxmlformats.org/package/2006/relationships"
    with ZipFile(source, "w") as package:
        package.writestr("ppt/presentation.xml", f'<p:presentation xmlns:p="{p}" xmlns:r="{r}"><p:sldIdLst><p:sldId r:id="r2"/><p:sldId r:id="r1"/></p:sldIdLst></p:presentation>')
        package.writestr("ppt/_rels/presentation.xml.rels", f'<Relationships xmlns="{rel}"><Relationship Id="r1" Target="slides/slide1.xml"/><Relationship Id="r2" Target="slides/slide2.xml"/></Relationships>')
        package.writestr("ppt/slides/slide1.xml", f'<p:sld xmlns:p="{p}" xmlns:a="{a}"><a:t>First XML</a:t></p:sld>')
        package.writestr("ppt/slides/slide2.xml", f'<p:sld xmlns:p="{p}" xmlns:a="{a}" show="0"><a:t>Second XML</a:t></p:sld>')
        package.writestr("ppt/slides/_rels/slide2.xml.rels", f'<Relationships xmlns="{rel}"><Relationship Id="n1" Type="{r}/notesSlide" Target="../notesSlides/notesSlide9.xml"/></Relationships>')
        package.writestr("ppt/notesSlides/notesSlide9.xml", f'<p:notes xmlns:p="{p}" xmlns:a="{a}"><p:sp><p:ph type="body"/><a:t>Speaker detail</a:t></p:sp><p:sp><p:ph type="sldNum"/><a:t>99</a:t></p:sp></p:notes>')
    slides = _extract_pptx_slides(source)
    assert len(slides) == 2
    assert "Second XML" in slides[0] and "隐藏" in slides[0]
    assert "Speaker detail" in slides[0] and "演讲者备注" in slides[0]
    assert "99" not in slides[0]
    assert slides[1] == "First XML"


def _generated_bytes(project_dir: Path) -> dict[str, bytes]:
    generated = project_dir / "converted_markdown"
    return {
        path.relative_to(generated).as_posix(): path.read_bytes()
        for path in generated.rglob("*")
        if path.is_file()
    }


def _make_text_sources(project_dir: Path) -> Path:
    source_dir = project_dir / "source"
    source_dir.mkdir()
    (source_dir / "a.txt").write_text("匿名样本 A。", encoding="utf-8")
    return source_dir


def test_invalid_utf8_failure_preserves_previous_generated_bytes(tmp_path: Path) -> None:
    source_dir = _make_text_sources(tmp_path)
    second_source = source_dir / "b.txt"
    second_source.write_text("匿名样本 B。", encoding="utf-8")
    convert_source(tmp_path)
    before = _generated_bytes(tmp_path)
    assert any(name.startswith("source_transcripts/") for name in before)
    assert "conversion_report.md" in before

    second_source.write_bytes(b"\xff")
    with pytest.raises(UnicodeDecodeError):
        convert_source(tmp_path)

    assert _generated_bytes(tmp_path) == before


def test_first_conversion_failure_leaves_no_partial_files(tmp_path: Path) -> None:
    source_dir = _make_text_sources(tmp_path)
    (source_dir / "b.txt").write_bytes(b"\xff")

    with pytest.raises(UnicodeDecodeError):
        convert_source(tmp_path)

    assert _generated_bytes(tmp_path) == {}


def test_markitdown_failure_preserves_previous_generated_bytes(tmp_path: Path) -> None:
    source_dir = _make_text_sources(tmp_path)
    (source_dir / "b.txt").write_text("匿名样本 B。", encoding="utf-8")

    class FakeConverter:
        def __init__(self) -> None:
            self.calls = 0

        def convert(self, _path: str) -> SimpleNamespace:
            self.calls += 1
            if self.calls == 2:
                raise RuntimeError("匿名注入故障")
            return SimpleNamespace(text_content="匿名转换文本")

    class SeedConverter:
        def convert(self, _path: str) -> SimpleNamespace:
            return SimpleNamespace(text_content="初始匿名文本")

    convert_source(tmp_path, engine="markitdown", markitdown_factory=SeedConverter)
    asset = tmp_path / "converted_markdown" / "assets" / "preserve.bin"
    asset.write_bytes(b"anonymous asset bytes")
    before = _generated_bytes(tmp_path)

    with pytest.raises(RuntimeError, match="匿名注入故障"):
        convert_source(tmp_path, engine="markitdown", markitdown_factory=FakeConverter)

    assert _generated_bytes(tmp_path) == before


def test_markitdown_dependency_system_exit_preserves_previous_generated_bytes(
    tmp_path: Path,
) -> None:
    source_dir = _make_text_sources(tmp_path)

    class SeedConverter:
        def convert(self, _path: str) -> SimpleNamespace:
            return SimpleNamespace(text_content="初始匿名文本")

    convert_source(tmp_path, engine="markitdown", markitdown_factory=SeedConverter)
    asset = tmp_path / "converted_markdown" / "assets" / "preserve.bin"
    asset.write_bytes(b"anonymous asset bytes")
    before = _generated_bytes(tmp_path)

    def unavailable_dependency() -> None:
        raise SystemExit("匿名依赖不可用")

    with pytest.raises(SystemExit, match="匿名依赖不可用"):
        convert_source(
            tmp_path,
            engine="markitdown",
            markitdown_factory=unavailable_dependency,
        )

    assert _generated_bytes(tmp_path) == before


def test_fact_candidates_discards_page_footer_but_keeps_sentence() -> None:
    candidates = _fact_candidates(
        "正常句子保留。\n--- end of page.page_number=1 ---"
    )

    assert candidates == ["正常句子保留。"]


def test_version_names_normalize_update_markers_without_merging_topics(
    tmp_path: Path,
) -> None:
    updated = "月会-已更新.pptx"
    pending = "月会-待更新.pptx"
    other_topic = "季度复盘-已更新.pptx"
    assert _normalize_version_key(updated) == _normalize_version_key(pending)
    assert _normalize_version_key(updated) != _normalize_version_key(other_topic)

    rows = [
        {"source_id": "S001", "file_name": updated, "transcript": "a.md"},
        {"source_id": "S002", "file_name": pending, "transcript": "b.md"},
        {"source_id": "S003", "file_name": other_topic, "transcript": "c.md"},
    ]
    for name, text in {
        "a.md": "## Page 1\n### Text\n月会讨论下月安排与资源协同。",
        "b.md": "## Page 1\n### Text\n月会讨论下月安排与资源协同。",
        "c.md": "## Page 1\n### Text\n季度复盘讨论年度预算与销售结果。",
    }.items():
        (tmp_path / name).write_text(text, encoding="utf-8")

    groups = _likely_version_groups(rows, tmp_path)
    assert len(groups) == 1
    assert {row["file_name"] for row in next(iter(groups.values()))} == {updated, pending}


@pytest.mark.parametrize(
    ("filename", "collector"),
    [
        ("sample.PDF", _iter_source_pdfs),
        ("sample.DOCX", _iter_source_docx),
        ("sample.PPTX", _iter_source_pptx),
    ],
)
def test_default_source_collectors_accept_uppercase_suffixes(
    tmp_path: Path, filename: str, collector
) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source_file = source_dir / filename
    source_file.write_bytes(b"anonymous minimal sample")

    assert collector(tmp_path) == [source_file]


def test_uppercase_txt_is_converted_by_default_engine(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "sample.TXT").write_text("匿名 TXT 内容。", encoding="utf-8")

    convert_source(tmp_path)

    generated = _generated_bytes(tmp_path)
    assert any(name.startswith("source_transcripts/") for name in generated)
    assert "conversion_report.md" in generated


def test_publish_failure_restores_previous_outputs(tmp_path: Path, monkeypatch) -> None:
    source_dir = _make_text_sources(tmp_path)
    convert_source(tmp_path)
    generated = tmp_path / "converted_markdown"
    (generated / "assets" / "preserve.bin").write_bytes(b"old asset")
    (generated / "quality_keep.md").write_text("keep", encoding="utf-8")
    before = _generated_bytes(tmp_path)
    (source_dir / "a.txt").write_text("new content", encoding="utf-8")
    calls = 0

    def fault_once(original):
        def rename(source, destination, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected publish failure")
            return original(source, destination, *args, **kwargs)
        return rename

    monkeypatch.setattr(os, "replace", fault_once(os.replace))
    monkeypatch.setattr(os, "rename", fault_once(os.rename))
    with pytest.raises(OSError, match="injected publish failure"):
        convert_source(tmp_path)
    assert _generated_bytes(tmp_path) == before


def test_success_preserves_unmanaged_evidence(tmp_path: Path) -> None:
    source_dir = _make_text_sources(tmp_path)
    convert_source(tmp_path)
    retained = tmp_path / "converted_markdown" / "quality_keep.md"
    retained.write_bytes(b"unmanaged evidence")
    (source_dir / "a.txt").write_text("new content", encoding="utf-8")
    convert_source(tmp_path)
    assert retained.read_bytes() == b"unmanaged evidence"
