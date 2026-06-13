import tempfile
import unittest
import warnings
import json
import os
import subprocess
import zipfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from brand_skill.cli import main as cli_main
from brand_skill.contract_verifier import verify_project_contract
from brand_skill.library_report import build_library_report
from brand_skill.library_writer import apply_context_library_update
from brand_skill.ima_importer import import_ima_media
from brand_skill.output_compiler import compile_structured_outputs
from brand_skill.review_pack import build_review_pack
from brand_skill.mineru_adapter import check_mineru_readiness
from brand_skill.source_quality import build_source_quality_report
from brand_skill.source_facts import build_source_facts
from brand_skill.source_versions import build_source_version_report
from brand_skill.source_converter import convert_source
from brand_skill.validators import (
    check_brand_lock_sheet_draft,
    check_claim_matrix,
    check_public_safe_text,
)
from brand_skill.workflow import OUTPUT_FILES, build_prompt_pack, scaffold_output


class Phase1WorkflowTests(unittest.TestCase):
    def _write_minimum_marketing_outputs(self, project_dir: Path) -> None:
        outputs = project_dir / "outputs"
        outputs.mkdir()
        files = {
            "02_document_profile.md": "# Document Profile\n\n| 字段 | 内容 | 信息状态 |\n|---|---|---|\n| 文件类型 | 活动方案 | AI 结构化转述，待确认 |\n",
            "03_marketing_semantic_transcript.md": "# Marketing Semantic Transcript\n\n## Page / Slide 1\n\n- Source Anchor：S001#page=1\n\n### 原页核心内容转述\n\n活动方案提出提升品牌声量。\n",
            "04_key_facts_and_claims.md": "# Key Facts and Claims\n\n| 项目 | 内容 | 来源 | 信息状态 |\n|---|---|---|---|\n| 核心事实 | 活动目标为提升品牌声量 | S001#page=2 | 已从来源资料提取 |\n",
            "05_strategy_and_execution_map.md": "# Strategy and Execution Map\n\n## 核心目标\n\n提升品牌声量。\n",
            "06_risk_and_review_items.md": "# Risk and Review Items\n\n| Review ID | 类型 | 审核项 | 来源锚点 | 风险等级 | 建议处理 |\n|---|---|---|---|---|---|\n| R001 | 数据口径 | 声量目标缺少衡量口径 | S001#page=2 | 高 | 补充指标定义 |\n",
            "09_quality_check_report.md": "# Quality Check Report\n\n## 总体结论\n\n有条件通过。\n",
            "10_context_asset_index.md": "# Context Asset Index\n\n| Asset ID | 上下文类型 | 可复用资产 | 来源锚点 | 信息状态 |\n|---|---|---|---|---|\n| CA001 | 项目上下文 | 活动目标为提升品牌声量 | S001#page=2 | 已从来源资料提取 |\n",
        }
        for filename, text in files.items():
            (outputs / filename).write_text(text, encoding="utf-8")

    def test_scaffold_output_uses_phase1_marketing_semantic_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            with redirect_stdout(StringIO()):
                scaffold_output(project_dir)

            output_files = sorted(path.name for path in (project_dir / "outputs").iterdir())
            self.assertEqual(output_files, sorted(OUTPUT_FILES))
            self.assertIn("01_source_conversion_report.md", output_files)
            self.assertIn("02_document_profile.md", output_files)
            self.assertIn("03_marketing_semantic_transcript.md", output_files)
            self.assertIn("07_ai_ready_marketing_brief_base.md", output_files)
            self.assertIn("10_context_asset_index.md", output_files)
            self.assertIn("11_context_library_update_plan.md", output_files)
            self.assertNotIn("04_product_knowledge_base_internal.md", output_files)
            self.assertNotIn("10_geo_activation_pack.md", output_files)

    def test_brand_lock_sheet_draft_requires_information_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            outputs = project_dir / "outputs"
            outputs.mkdir()
            (outputs / "02_brand_lock_sheet_draft.md").write_text(
                "# Brand Lock Sheet Draft\n\n## 一句话核心卖点\n示例产品A。\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                with self.assertRaises(SystemExit):
                    check_brand_lock_sheet_draft(project_dir)

    def test_claim_matrix_requires_applicable_sku_or_fragrance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            outputs = project_dir / "outputs"
            outputs.mkdir()
            (outputs / "06_claim_matrix.md").write_text(
                "\n".join(
                    [
                        "# Claim Matrix",
                        "",
                        "| Claim ID | Claim 名称 | 适用产品/SKU/香型 | 可外发表述 | 支撑数据 | 是否可用于全系列 | 风险等级 |",
                        "|---|---|---|---|---|---|---|",
                        "| C001 | 即刻降温 6.62℃ |  | 深海龙涎香型即刻清凉 | 检测数据 6.62℃ | 否 | 中 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                with self.assertRaises(SystemExit):
                    check_claim_matrix(project_dir)

    def test_public_safe_text_flags_internal_sensitive_terms(self) -> None:
        risky_terms = check_public_safe_text("外发安全版不应出现竞品弱点、攻击点或必赢这类表达。")

        self.assertIn("竞品弱点", risky_terms)
        self.assertIn("攻击点", risky_terms)
        self.assertIn("必赢", risky_terms)

    def test_build_prompt_pack_uses_phase1_prompts_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            prompts_dir = project_dir / "prompts"
            prompts_dir.mkdir()
            (prompts_dir / "01_generate_document_profile.md").write_text("# Prompt 01\n", encoding="utf-8")
            (prompts_dir / "02_generate_marketing_semantic_transcript.md").write_text("# Prompt 02\n", encoding="utf-8")
            (prompts_dir / "03_generate_key_facts_and_claims.md").write_text("# Prompt 03\n", encoding="utf-8")
            (prompts_dir / "08_generate_context_asset_index.md").write_text("# Context Asset Prompt\n", encoding="utf-8")
            (prompts_dir / "09_generate_context_library_update_plan.md").write_text("# Library Update Prompt\n", encoding="utf-8")
            (prompts_dir / "05_generate_claim_matrix.md").write_text("# Optional Product Module\n", encoding="utf-8")
            (prompts_dir / "07_generate_geo_pack.md").write_text("# Second Phase\n", encoding="utf-8")

            with redirect_stdout(StringIO()):
                build_prompt_pack(project_dir)

            bundle = (project_dir / "prompt_bundle.md").read_text(encoding="utf-8")
            self.assertIn("# Prompt 01", bundle)
            self.assertIn("# Prompt 02", bundle)
            self.assertIn("# Prompt 03", bundle)
            self.assertIn("# Context Asset Prompt", bundle)
            self.assertIn("# Library Update Prompt", bundle)
            self.assertNotIn("# Optional Product Module", bundle)
            self.assertNotIn("# Second Phase", bundle)

    def test_convert_source_creates_transcript_assets_and_report(self) -> None:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", DeprecationWarning)
                import fitz
        except ImportError:
            self.skipTest("PyMuPDF is not installed")

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "product_training"
            source_dir.mkdir(parents=True)
            pdf_path = source_dir / "sample.pdf"
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((72, 72), "示例产品A")
            doc.save(pdf_path)
            doc.close()

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")

            transcript = project_dir / "converted_markdown" / "source_transcripts" / "S001_product_training.md"
            report = project_dir / "converted_markdown" / "conversion_report.md"
            page_image = project_dir / "converted_markdown" / "assets" / "S001_product_training" / "page_01.png"
            self.assertTrue(transcript.exists())
            self.assertTrue(report.exists())
            self.assertTrue(page_image.exists())
            self.assertIn("Source Anchor：S001#page=1", transcript.read_text(encoding="utf-8"))
            transcript_text = transcript.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("文件创建时间：", transcript_text)
            self.assertIn("文件修改时间：", transcript_text)
            self.assertIn("原始文件创建时间", report_text)
            self.assertIn("原始文件修改时间", report_text)
            self.assertIn("识别质量摘要", report_text)
            self.assertIn("总页数", report_text)
            self.assertIn("视觉/表格/小字限制", report_text)
            self.assertIn("人工复核建议", report_text)
            self.assertIn("pymupdf4llm", report_text)

    def test_convert_source_accepts_markdown_source_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "meeting_notes"
            source_dir.mkdir(parents=True)
            (source_dir / "sample.md").write_text(
                "# 品牌月会\n\n## 核心内容\n\n- 本月重点是渠道复盘。\n- 下月需要补充投放数据。\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")

            transcript = project_dir / "converted_markdown" / "source_transcripts" / "S001_meeting_notes.md"
            report = project_dir / "converted_markdown" / "conversion_report.md"
            transcript_text = transcript.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("文件类型：Markdown", transcript_text)
            self.assertIn("Source Anchor：S001#page=1", transcript_text)
            self.assertIn("Page Screenshot：不适用", transcript_text)
            self.assertIn("渠道复盘", transcript_text)
            self.assertIn("Markdown 源稿转写", report_text)
            self.assertIn("识别质量摘要", report_text)

    def test_convert_source_accepts_plain_text_source_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "meeting_transcript"
            source_dir.mkdir(parents=True)
            (source_dir / "sample.txt").write_text(
                "品牌周会记录\n\n本周重点：终端物料复盘。\n下周动作：补充渠道反馈。",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")

            transcript = project_dir / "converted_markdown" / "source_transcripts" / "S001_meeting_transcript.md"
            report = project_dir / "converted_markdown" / "conversion_report.md"
            transcript_text = transcript.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("文件类型：Plain Text", transcript_text)
            self.assertIn("Source Anchor：S001#page=1", transcript_text)
            self.assertIn("终端物料复盘", transcript_text)
            self.assertIn("Plain Text 源稿转写", report_text)
            self.assertIn("识别质量摘要", report_text)

    def test_convert_source_accepts_docx_source_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "brand_doc"
            source_dir.mkdir(parents=True)
            docx_path = source_dir / "sample.docx"
            document_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                "<w:body>"
                "<w:p><w:r><w:t>品牌策略文档</w:t></w:r></w:p>"
                "<w:p><w:r><w:t>核心内容：渠道打法复盘。</w:t></w:r></w:p>"
                "</w:body>"
                "</w:document>"
            )
            with zipfile.ZipFile(docx_path, "w") as docx:
                docx.writestr("word/document.xml", document_xml)

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")

            transcript = project_dir / "converted_markdown" / "source_transcripts" / "S001_brand_doc.md"
            report = project_dir / "converted_markdown" / "conversion_report.md"
            transcript_text = transcript.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("文件类型：Word Document", transcript_text)
            self.assertIn("Source Anchor：S001#page=1", transcript_text)
            self.assertIn("渠道打法复盘", transcript_text)
            self.assertIn("Word Document 源稿转写", report_text)
            self.assertIn("识别质量摘要", report_text)

    def test_convert_source_accepts_pptx_source_documents(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "launch_plan"
            source_dir.mkdir(parents=True)
            pptx_path = source_dir / "sample.pptx"
            slide_1 = (
                '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                "<p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>上市节奏</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>"
                "</p:sld>"
            )
            slide_2 = (
                '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                "<p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>渠道动作复盘</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>"
                "</p:sld>"
            )
            with zipfile.ZipFile(pptx_path, "w") as pptx:
                pptx.writestr("ppt/slides/slide1.xml", slide_1)
                pptx.writestr("ppt/slides/slide2.xml", slide_2)

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")

            transcript = project_dir / "converted_markdown" / "source_transcripts" / "S001_launch_plan.md"
            report = project_dir / "converted_markdown" / "conversion_report.md"
            transcript_text = transcript.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("文件类型：PowerPoint", transcript_text)
            self.assertIn("Source Anchor：S001#page=1", transcript_text)
            self.assertIn("Source Anchor：S001#page=2", transcript_text)
            self.assertIn("上市节奏", transcript_text)
            self.assertIn("渠道动作复盘", transcript_text)
            self.assertIn("PowerPoint 源稿转写", report_text)
            self.assertIn("2", report_text)
            self.assertIn("低置信度页数：2", report_text)
            self.assertIn("PowerPoint 轻量转写未保留真实版式、图片、图表、动画和备注", report_text)

    def test_convert_source_assigns_ids_by_source_path_across_file_types(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            deck_dir = project_dir / "source" / "01_deck"
            notes_dir = project_dir / "source" / "02_notes"
            deck_dir.mkdir(parents=True)
            notes_dir.mkdir(parents=True)
            pptx_path = deck_dir / "sample.pptx"
            slide_1 = (
                '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                "<p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>新品节奏</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld>"
                "</p:sld>"
            )
            with zipfile.ZipFile(pptx_path, "w") as pptx:
                pptx.writestr("ppt/slides/slide1.xml", slide_1)
            (notes_dir / "sample.md").write_text("# 会议纪要\n\n补充渠道复盘。", encoding="utf-8")

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")

            transcripts_dir = project_dir / "converted_markdown" / "source_transcripts"
            self.assertTrue((transcripts_dir / "S001_01_deck.md").exists())
            self.assertTrue((transcripts_dir / "S002_02_notes.md").exists())
            report_text = (project_dir / "converted_markdown" / "conversion_report.md").read_text(encoding="utf-8")
            self.assertLess(report_text.index("| S001 | sample.pptx |"), report_text.index("| S002 | sample.md |"))

    def test_convert_source_fails_when_unsupported_source_files_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "campaign"
            source_dir.mkdir(parents=True)
            (source_dir / "brief.md").write_text("# Brief\n\n活动重点。\n", encoding="utf-8")
            (source_dir / "long_image.png").write_bytes(b"not-a-real-image")

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    convert_source(project_dir, engine="pymupdf4llm")

            output = stdout.getvalue()
            self.assertIn("Unsupported source file", output)
            self.assertIn("campaign/long_image.png", output)
            self.assertFalse((project_dir / "converted_markdown" / "conversion_report.md").exists())

    def test_convert_source_marks_mineru_as_optional(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    convert_source(Path(temp_dir), engine="mineru")
            output = stdout.getvalue()
            self.assertIn("MinerU CLI", output)
            self.assertIn("mineru -p <input_path> -o <output_path>", output)

    def test_check_mineru_readiness_reports_missing_optional_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            with redirect_stdout(StringIO()):
                report_path = check_mineru_readiness(project_dir, which=lambda _: None)

            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("# MinerU Readiness Report", report_text)
            self.assertIn("未检测到 MinerU CLI", report_text)
            self.assertIn("不影响第一阶段闭环", report_text)
            self.assertIn("真实品牌资料只能放在 `_private_test_runs/`", report_text)

    def test_check_mineru_readiness_records_cli_path_and_version_output(self) -> None:
        class FakeResult:
            returncode = 0
            stdout = "MinerU 1.2.3\n"
            stderr = ""

        calls = []

        def fake_runner(command, **_kwargs):
            calls.append(command)
            return FakeResult()

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            with redirect_stdout(StringIO()):
                report_path = check_mineru_readiness(
                    project_dir,
                    which=lambda _: "/usr/local/bin/mineru",
                    runner=fake_runner,
                )

            report_text = report_path.read_text(encoding="utf-8")
            self.assertEqual(calls, [["/usr/local/bin/mineru", "--version"]])
            self.assertIn("已检测到 MinerU CLI", report_text)
            self.assertIn("/usr/local/bin/mineru", report_text)
            self.assertIn("MinerU 1.2.3", report_text)
            self.assertIn("后续可在私有测试目录做 5 页以内小样对比", report_text)

    def test_cli_check_mineru_command_writes_readiness_report(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            argv = sys.argv
            sys.argv = ["brand-skill", "check-mineru", str(project_dir)]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            report_path = project_dir / "converted_markdown" / "mineru_readiness_report.md"
            self.assertTrue(report_path.exists())
            self.assertIn("MinerU Readiness Report", report_path.read_text(encoding="utf-8"))

    def test_build_source_facts_creates_traceable_fact_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "meeting_notes"
            source_dir.mkdir(parents=True)
            (source_dir / "sample.md").write_text(
                "# 品牌月会\n\n- 本月重点是渠道复盘。\n- 下月需要补充投放数据。\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")
                build_source_facts(project_dir)

            facts_path = project_dir / "converted_markdown" / "source_facts" / "S001_meeting_notes_source_facts.md"
            facts_text = facts_path.read_text(encoding="utf-8")
            self.assertIn("# Source Facts｜sample.md", facts_text)
            self.assertIn("| SF001-001 | S001#page=1 | 本月重点是渠道复盘。 | 已从来源资料提取 | 无明显低置信度 |", facts_text)
            self.assertIn("| SF001-002 | S001#page=1 | 下月需要补充投放数据。 | 已从来源资料提取 | 无明显低置信度 |", facts_text)
            self.assertIn("不做品牌确认判断", facts_text)

    def test_build_source_facts_preserves_headings_and_table_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            transcripts_dir = project_dir / "converted_markdown" / "source_transcripts"
            transcripts_dir.mkdir(parents=True)
            (transcripts_dir / "S001_strategy.md").write_text(
                "\n".join(
                    [
                        "# Source Transcript｜strategy.pdf",
                        "",
                        "## Source Metadata",
                        "- Source ID：S001",
                        "- 原始文件：strategy.pdf",
                        "",
                        "## Page 1",
                        "- Source Anchor：S001#page=1",
                        "",
                        "### Text",
                        "#### 市场背景",
                        "- 活动目标是建立夏季清爽心智。",
                        "",
                        "| 模块 | 信息 |",
                        "|---|---|",
                        "| 渠道 | 抖音内容和电商承接 |",
                        "| 待补充 | 预算和负责人 |",
                        "",
                        "### Low Confidence / Need Review",
                        "- 表格结构需复核",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_source_facts(project_dir)

            facts_text = (
                project_dir / "converted_markdown" / "source_facts" / "S001_strategy_source_facts.md"
            ).read_text(encoding="utf-8")
            self.assertIn("市场背景：活动目标是建立夏季清爽心智。", facts_text)
            self.assertIn("表格行：模块=渠道；信息=抖音内容和电商承接", facts_text)
            self.assertIn("表格行：模块=待补充；信息=预算和负责人", facts_text)
            self.assertIn("表格结构需复核", facts_text)

    def test_convert_source_preserves_external_source_manifest_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "brand_content"
            source_dir.mkdir(parents=True)
            (source_dir / "sample.md").write_text("# 品牌资料\n\n品牌历史内容。", encoding="utf-8")
            (project_dir / "source" / "source_manifest.json").write_text(
                json.dumps(
                    {
                        "sources": [
                            {
                                "path": "brand_content/sample.md",
                                "source_platform": "ima",
                                "knowledge_base": "示例品牌知识库",
                                "knowledge_path": "品牌内容 / sample.md",
                                "media_id": "media_sample_001",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")

            transcript = project_dir / "converted_markdown" / "source_transcripts" / "S001_brand_content.md"
            report = project_dir / "converted_markdown" / "conversion_report.md"
            transcript_text = transcript.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("外部来源平台：ima", transcript_text)
            self.assertIn("外部知识库：示例品牌知识库", transcript_text)
            self.assertIn("外部来源路径：品牌内容 / sample.md", transcript_text)
            self.assertIn("media_sample_001", transcript_text)
            self.assertIn("外部来源", report_text)
            self.assertIn("ima / 示例品牌知识库 / 品牌内容 / sample.md / media_sample_001", report_text)

    def test_import_ima_media_refuses_public_examples_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir) / "examples" / "bad_public_target"

            with redirect_stdout(StringIO()):
                with self.assertRaises(SystemExit):
                    import_ima_media(
                        target_dir,
                        media_id="media_sample_001",
                        title="sample.pdf",
                        knowledge_base="示例品牌知识库",
                        knowledge_path="品牌内容 / sample.pdf",
                        api_script=Path(temp_dir) / "fake_ima_api.cjs",
                    )

    def test_import_ima_media_downloads_to_private_source_and_writes_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            sample_file = temp_path / "remote_sample.pdf"
            sample_file.write_bytes(b"%PDF-1.4\n% sample\n")
            api_script = temp_path / "fake_ima_api.cjs"
            api_script.write_text(
                "\n".join(
                    [
                        "#!/usr/bin/env node",
                        "const path = require('path');",
                        "const sample = process.env.FAKE_IMA_SAMPLE_PATH;",
                        "process.stdout.write(JSON.stringify({",
                        "  code: 0,",
                        "  msg: 'success',",
                        "  data: { media_type: 1, url_info: { url: 'file://' + path.resolve(sample), headers: {} } }",
                        "}));",
                    ]
                ),
                encoding="utf-8",
            )
            api_script.chmod(0o755)
            target_dir = temp_path / "_private_test_runs" / "ima_import_probe"

            with redirect_stdout(StringIO()):
                import_ima_media(
                    target_dir,
                    media_id="media_sample_001",
                    title="sample.pdf",
                    knowledge_base="示例品牌知识库",
                    knowledge_path="品牌内容 / sample.pdf",
                    api_script=api_script,
                    env={"FAKE_IMA_SAMPLE_PATH": str(sample_file)},
                )

            downloaded = target_dir / "source" / "ima_imports" / "sample.pdf"
            manifest = json.loads((target_dir / "source" / "source_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(downloaded.read_bytes(), sample_file.read_bytes())
            self.assertEqual(manifest["sources"][0]["path"], "ima_imports/sample.pdf")
            self.assertEqual(manifest["sources"][0]["source_platform"], "ima")
            self.assertEqual(manifest["sources"][0]["knowledge_base"], "示例品牌知识库")
            self.assertEqual(manifest["sources"][0]["knowledge_path"], "品牌内容 / sample.pdf")
            self.assertEqual(manifest["sources"][0]["media_id"], "media_sample_001")

    def test_build_source_quality_report_summarizes_low_confidence_pages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            transcripts_dir = project_dir / "converted_markdown" / "source_transcripts"
            transcripts_dir.mkdir(parents=True)
            (transcripts_dir / "S001_brand_content.md").write_text(
                "\n".join(
                    [
                        "# Source Transcript｜sample.pdf",
                        "",
                        "## Source Metadata",
                        "- Source ID：S001",
                        "- 原始文件：sample.pdf",
                        "- 文件类型：PDF",
                        "",
                        "## Page 1",
                        "- Source Anchor：S001#page=1",
                        "- Page Screenshot：../assets/S001/page_01.png",
                        "- Extracted text chars：120",
                        "- Embedded images detected：0",
                        "- Vector drawings detected：0",
                        "",
                        "### Text",
                        "品牌资料第一页文字完整。",
                        "",
                        "### Low Confidence / Need Review",
                        "- 无明显低置信度。",
                        "",
                        "## Page 2",
                        "- Source Anchor：S001#page=2",
                        "- Page Screenshot：../assets/S001/page_02.png",
                        "- Extracted text chars：8",
                        "- Embedded images detected：3",
                        "- Vector drawings detected：2",
                        "",
                        "### Text",
                        "> 低置信度，未抽取到可用文本。请查看页面截图。",
                        "",
                        "### Low Confidence / Need Review",
                        "- 可抽取文字较少；含图片/视觉信息",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_source_quality_report(project_dir)

            report = project_dir / "converted_markdown" / "source_quality_report.md"
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("# Source Quality Report", report_text)
            self.assertIn("- 总页数：2", report_text)
            self.assertIn("- 需要复核页数：1", report_text)
            self.assertIn("| S001#page=2 | sample.pdf | 8 | 3 | 2 | 可抽取文字较少；含图片/视觉信息 | OCR / MinerU / 人工复核 |", report_text)
            self.assertIn("优先处理含图片、低文字量、表格或小字页面", report_text)

    def test_build_source_version_report_groups_likely_versions_by_modified_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "conversion_report.md").write_text(
                "\n".join(
                    [
                        "# Source Conversion Report",
                        "",
                        "## Source Files",
                        "",
                        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 | 外部来源 |",
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
                        "| S001 | brand_strategy_v1.pdf | 2026-01-01T09:00:00+08:00 | 2026-01-02T09:00:00+08:00 | source_transcripts/S001_brand_strategy_v1.md | pymupdf4llm | PDF | no | pages 1-10 | 待复核 | 截图 | 待复核 | 无明显低置信度 | 否 | ima / 示例库 |",
                        "| S002 | brand_strategy_v2.pdf | 2026-01-01T09:00:00+08:00 | 2026-03-08T18:30:00+08:00 | source_transcripts/S002_brand_strategy_v2.md | pymupdf4llm | PDF | no | pages 1-12 | 待复核 | 截图 | 待复核 | 无明显低置信度 | 否 | ima / 示例库 |",
                        "| S003 | trade_recap.pdf | 2026-02-01T09:00:00+08:00 | 2026-02-02T09:00:00+08:00 | source_transcripts/S003_trade_recap.md | pymupdf4llm | PDF | no | pages 1-3 | 待复核 | 截图 | 待复核 | 无明显低置信度 | 否 | ima / 示例库 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_source_version_report(project_dir)

            report_text = (converted / "source_version_report.md").read_text(encoding="utf-8")
            self.assertIn("# Source Version Report", report_text)
            self.assertIn("疑似多版本组数：1", report_text)
            self.assertIn("brand_strategy", report_text)
            self.assertIn("S002", report_text)
            self.assertIn("最新修改时间线索", report_text)
            self.assertIn("不自动覆盖", report_text)
            self.assertIn("进入更新/冲突复核队列", report_text)

    def test_build_source_version_report_groups_noisy_final_date_hash_suffixes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "conversion_report.md").write_text(
                "\n".join(
                    [
                        "# Source Conversion Report",
                        "",
                        "## Source Files",
                        "",
                        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 | 外部来源 |",
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
                        "| S001 | brand_BPM-FINAL0729-FFFFFFFF.pdf | 2026-07-29T09:00:00+08:00 | 2026-07-29T18:00:00+08:00 | source_transcripts/S001.md | pymupdf4llm | PDF | no | pages 1-20 | 待复核 | 截图 | 待复核 | 无明显低置信度 | 否 | ima / 示例库 |",
                        "| S002 | brand BPM final 0801 copy.pdf | 2026-08-01T09:00:00+08:00 | 2026-08-01T18:00:00+08:00 | source_transcripts/S002.md | pymupdf4llm | PDF | no | pages 1-22 | 待复核 | 截图 | 待复核 | 无明显低置信度 | 否 | ima / 示例库 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_source_version_report(project_dir)

            report_text = (converted / "source_version_report.md").read_text(encoding="utf-8")
            self.assertIn("疑似多版本组数：1", report_text)
            self.assertIn("### brand_bpm", report_text)
            self.assertIn("S002 / brand BPM final 0801 copy.pdf / 2026-08-01T18:00:00+08:00", report_text)
            self.assertIn("brand_BPM-FINAL0729-FFFFFFFF.pdf", report_text)

    def test_cli_build_source_version_report_command(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "conversion_report.md").write_text(
                "\n".join(
                    [
                        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 | 外部来源 |",
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
                        "| S001 | campaign_plan_2025.pdf | 2025-05-01T09:00:00+08:00 | 2025-05-02T09:00:00+08:00 | source_transcripts/S001.md | pymupdf4llm | PDF | no | pages 1-2 | 待复核 | 截图 | 待复核 | 无明显低置信度 | 否 | - |",
                        "| S002 | campaign_plan_2026.pdf | 2026-05-01T09:00:00+08:00 | 2026-05-02T09:00:00+08:00 | source_transcripts/S002.md | pymupdf4llm | PDF | no | pages 1-2 | 待复核 | 截图 | 待复核 | 无明显低置信度 | 否 | - |",
                    ]
                ),
                encoding="utf-8",
            )
            argv = sys.argv
            sys.argv = ["brand-skill", "build-source-version-report", str(project_dir)]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            self.assertTrue((converted / "source_version_report.md").exists())

    def test_compile_structured_outputs_builds_phase1_markdown_from_source_facts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            facts = converted / "source_facts"
            transcripts.mkdir(parents=True)
            facts.mkdir()
            (converted / "conversion_report.md").write_text(
                "\n".join(
                    [
                        "# Source Conversion Report",
                        "",
                        "## Source Files",
                        "",
                        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 | 外部来源 |",
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
                        "| S001 | campaign.md | 2026-01-01T09:00:00+08:00 | 2026-01-02T09:00:00+08:00 | source_transcripts/S001.md | manual | Markdown | no | pages 1-3 | 不适用 | 不适用 | 不适用 | 目标人群缺少数据 | 是 | - |",
                    ]
                ),
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n## 识别质量总览\n\n- 总页数：3\n- 需要复核页数：1\n\n## 需要复核的页面\n\n| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 低置信度说明 | 建议动作 |\n|---|---|---|---|---|---|---|\n| S001#page=2 | campaign.md | 80 | 0 | 0 | 目标人群缺少数据 | 人工复核 |\n",
                encoding="utf-8",
            )
            (converted / "source_version_report.md").write_text(
                "# Source Version Report\n\n## 版本线索总览\n\n- 疑似多版本组数：0\n- 最新修改时间线索：不自动覆盖旧知识。\n",
                encoding="utf-8",
            )
            (transcripts / "S001.md").write_text(
                "\n".join(
                    [
                        "# Source Transcript｜campaign.md",
                        "",
                        "## Page 1",
                        "- Source Anchor：S001#page=1",
                        "",
                        "### Text",
                        "品牌希望建立城市清爽的活动联想。",
                        "",
                        "## Page 2",
                        "- Source Anchor：S001#page=2",
                        "",
                        "### Text",
                        "目标人群是城市通勤人群，但缺少调研数据。",
                    ]
                ),
                encoding="utf-8",
            )
            (facts / "S001_source_facts.md").write_text(
                "\n".join(
                    [
                        "# Source Facts｜campaign.md",
                        "",
                        "## Fact Candidates",
                        "",
                        "| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |",
                        "|---|---|---|---|---|",
                        "| SF001-001 | S001#page=1 | 品牌希望建立城市清爽的活动联想。 | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-002 | S001#page=2 | 目标人群是城市通勤人群，但缺少调研数据。 | 已从来源资料提取 | 目标人群缺少数据。 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                compile_structured_outputs(project_dir)

            outputs = project_dir / "outputs"
            self.assertTrue((outputs / "02_document_profile.md").exists())
            self.assertIn("campaign.md", (outputs / "00_source_index.md").read_text(encoding="utf-8"))
            self.assertIn("品牌希望建立城市清爽", (outputs / "03_marketing_semantic_transcript.md").read_text(encoding="utf-8"))
            self.assertIn("SF001-001", (outputs / "04_key_facts_and_claims.md").read_text(encoding="utf-8"))
            self.assertIn("S001#page=2", (outputs / "06_risk_and_review_items.md").read_text(encoding="utf-8"))
            self.assertIn("CA001", (outputs / "10_context_asset_index.md").read_text(encoding="utf-8"))
            self.assertIn("LCE001", (outputs / "11_context_library_update_plan.md").read_text(encoding="utf-8"))

    def test_cli_compile_outputs_command(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            facts = project_dir / "converted_markdown" / "source_facts"
            facts.mkdir(parents=True)
            (facts / "S001_source_facts.md").write_text(
                "# Source Facts\n\n| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |\n|---|---|---|---|---|\n| SF001-001 | S001#page=1 | 示例事实。 | 已从来源资料提取 | 无明显低置信度。 |\n",
                encoding="utf-8",
            )
            argv = sys.argv
            sys.argv = ["brand-skill", "compile-outputs", str(project_dir)]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            self.assertTrue((project_dir / "outputs" / "11_context_library_update_plan.md").exists())

    def test_compile_structured_outputs_detects_document_type_and_business_stage(self) -> None:
        cases = [
            (
                "brand_meeting",
                "本次 BPM 会议纪要明确下周动作、决策事项和负责人。",
                "会议纪要",
                "会议对齐 / 决策同步",
                "decision",
            ),
            (
                "media_recap",
                "本次抖音投放复盘总结了素材表现、转化数据、经验教训和后续优化动作。",
                "投放复盘",
                "复盘 / 优化",
                "case",
            ),
        ]
        for project_name, evidence, expected_type, expected_stage, expected_location in cases:
            with self.subTest(project_name=project_name):
                with tempfile.TemporaryDirectory() as temp_dir:
                    project_dir = Path(temp_dir) / project_name
                    facts = project_dir / "converted_markdown" / "source_facts"
                    facts.mkdir(parents=True)
                    (facts / "S001_source_facts.md").write_text(
                        "\n".join(
                            [
                                "# Source Facts",
                                "",
                                "| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |",
                                "|---|---|---|---|---|",
                                f"| SF001-001 | S001#page=1 | {evidence} | 已从来源资料提取 | 无明显低置信度。 |",
                            ]
                        ),
                        encoding="utf-8",
                    )

                    with redirect_stdout(StringIO()):
                        compile_structured_outputs(project_dir)

                    profile = (project_dir / "outputs" / "02_document_profile.md").read_text(encoding="utf-8")
                    strategy = (project_dir / "outputs" / "05_strategy_and_execution_map.md").read_text(encoding="utf-8")
                    plan = (project_dir / "outputs" / "11_context_library_update_plan.md").read_text(encoding="utf-8")
                    self.assertIn(f"| 文件类型 | {expected_type} |", profile)
                    self.assertIn(f"| 业务阶段 | {expected_stage} |", profile)
                    self.assertIn(f"## {expected_type} 结构化转述重点", strategy)
                    self.assertIn(f"| LCE001 | {expected_location} |", plan)

    def test_compile_structured_outputs_groups_facts_into_marketing_outline(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            facts = project_dir / "converted_markdown" / "source_facts"
            facts.mkdir(parents=True)
            (facts / "S001_source_facts.md").write_text(
                "\n".join(
                    [
                        "# Source Facts",
                        "",
                        "| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |",
                        "|---|---|---|---|---|",
                        "| SF001-001 | S001#page=1 | 活动目标是建立城市清爽心智。 | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-002 | S001#page=2 | 渠道触点包括线下快闪、社媒内容和电商承接。 | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-003 | S001#page=3 | 下一步动作是补充预算、负责人和排期。 | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-004 | S001#page=4 | 预算和渠道合作名单暂未提供。 | 已从来源资料提取 | 信息缺失。 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                compile_structured_outputs(project_dir)

            strategy = (project_dir / "outputs" / "05_strategy_and_execution_map.md").read_text(encoding="utf-8")
            brief = (project_dir / "outputs" / "07_ai_ready_marketing_brief_base.md").read_text(encoding="utf-8")
            quality = (project_dir / "outputs" / "09_quality_check_report.md").read_text(encoding="utf-8")
            self.assertIn("## 自动识别的大纲", strategy)
            self.assertIn("### 目标 / 要解决的问题", strategy)
            self.assertIn("活动目标是建立城市清爽心智", strategy)
            self.assertIn("### 渠道 / 触点 / 场景", strategy)
            self.assertIn("线下快闪、社媒内容和电商承接", strategy)
            self.assertIn("### 下一步动作 / 执行要求", strategy)
            self.assertIn("补充预算、负责人和排期", strategy)
            self.assertIn("### 缺口 / 待补充", strategy)
            self.assertIn("预算和渠道合作名单暂未提供", strategy)
            self.assertIn("自动识别的大纲", brief)
            self.assertIn("大纲分类：4 类", quality)

    def test_compile_structured_outputs_keeps_table_facts_as_structured_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            facts = project_dir / "converted_markdown" / "source_facts"
            facts.mkdir(parents=True)
            (facts / "S001_source_facts.md").write_text(
                "\n".join(
                    [
                        "# Source Facts",
                        "",
                        "| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |",
                        "|---|---|---|---|---|",
                        "| SF001-001 | S001#page=1 | 市场背景：活动目标是建立夏季清爽心智。 | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-002 | S001#page=2 | 表格行：模块=渠道；信息=抖音内容和电商承接 | 已从来源资料提取 | 表格结构需复核。 |",
                        "| SF001-003 | S001#page=2 | 表格行：模块=待补充；信息=预算和负责人 | 已从来源资料提取 | 表格结构需复核。 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                compile_structured_outputs(project_dir)

            strategy = (project_dir / "outputs" / "05_strategy_and_execution_map.md").read_text(encoding="utf-8")
            asset_index = (project_dir / "outputs" / "10_context_asset_index.md").read_text(encoding="utf-8")
            plan = (project_dir / "outputs" / "11_context_library_update_plan.md").read_text(encoding="utf-8")
            self.assertIn("### 表格结构信息", strategy)
            self.assertIn("表格行：模块=渠道；信息=抖音内容和电商承接", strategy)
            self.assertIn("| CA002 | structured_table |", asset_index)
            self.assertIn("| LCE002 | structured_table |", plan)

    def test_cli_exposes_brand_lock_check(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            outputs = project_dir / "outputs"
            outputs.mkdir()
            (outputs / "02_brand_lock_sheet_draft.md").write_text(
                "# Brand Lock Sheet Draft\n\n| 字段 | 内容 | 信息状态 |\n|---|---|---|\n| 产品 | 示例品牌 | 已从来源资料提取 |\n",
                encoding="utf-8",
            )
            argv = sys.argv
            sys.argv = ["brand-skill", "check-brand-lock", str(project_dir)]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

    def test_build_review_pack_creates_static_html(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            self._write_minimum_marketing_outputs(project_dir)

            with redirect_stdout(StringIO()):
                build_review_pack(project_dir)

            html = project_dir / "review" / "brand_review.html"
            text = html.read_text(encoding="utf-8")
            self.assertTrue(html.exists())
            self.assertIn("识别问题待处理", text)
            self.assertIn("需要处理的问题", text)
            self.assertIn("文件大纲参考", text)
            self.assertIn("人工修正", text)
            self.assertIn("待处理问题", text)
            self.assertIn("导出确认意见", text)
            self.assertNotIn('class="source-anchor"', text)
            self.assertNotIn("来源位置：", text)
            self.assertNotIn("Context Asset Index Review", text)

    def test_build_review_pack_auto_passes_without_exceptions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            outputs = project_dir / "outputs"
            outputs.mkdir()
            files = {
                "02_document_profile.md": "# Document Profile｜示例会议\n\n| 字段 | 内容 |\n|---|---|\n| 文件类型 | 品牌会议资料 |\n",
                "03_marketing_semantic_transcript.md": "# Marketing Semantic Transcript｜示例会议\n\n## 1. 总体结构\n\n- 会议开场。\n- 品牌策略。\n- 下一步动作。\n\n## 2. 可读转述\n\n### 会议开场\n\n资料说明本次会议用于对齐品牌策略。\n",
                "06_risk_and_review_items.md": "# Risk and Review Items\n\n| Review ID | 类型 | 审核项 | 建议处理 |\n|---|---|---|---|\n",
            }
            for filename, text in files.items():
                (outputs / filename).write_text(text, encoding="utf-8")

            with redirect_stdout(StringIO()):
                build_review_pack(project_dir)

            text = (project_dir / "review" / "brand_review.html").read_text(encoding="utf-8")
            self.assertIn("自动通过，无需人工处理", text)
            self.assertIn("待处理问题：0", text)
            self.assertIn("这份文件当前没有识别异常需要人工处理", text)

    def test_build_review_pack_requires_key_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            (project_dir / "outputs").mkdir()

            with redirect_stdout(StringIO()):
                with self.assertRaises(SystemExit):
                    build_review_pack(project_dir)

    def test_apply_context_library_update_writes_entries_and_log(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            outputs.mkdir(parents=True)
            (outputs / "11_context_library_update_plan.md").write_text(
                "\n".join(
                    [
                        "# Context Library Update Plan",
                        "",
                        "## 2. New Context Entries",
                        "",
                        "| Entry ID | 建议归档位置 | 标题 | 内容摘要 | 来源资产 | 稳定性 | 写入建议 |",
                        "|---|---|---|---|---|---|---|",
                        "| LCE001 | brand | 夏季关键词 | 城市、清爽、轻便、日常。 | CA001 | 项目期有效 | 暂存 |",
                        "| LCE002 | project | 临时预算 | 一次性预算信息。 | CA002 | 项目期有效 | 不写入 |",
                        "",
                        "## 3. Existing Context Updates",
                        "",
                        "| 可能影响的已有条目 | 更新方式 | 新信息 | 冲突或风险 | 版本判断依据 |",
                        "|---|---|---|---|---|",
                        "| 待检索 | 补充 | 夏季关键词需要补充轻便表达。 | 可能与旧品牌口径不一致 | 来源文件修改时间较新 |",
                        "",
                        "## 4. Do Not Promote",
                        "",
                        "- 不把临时预算写入长期库。",
                        "",
                        "## 6. Retrieval Notes",
                        "",
                        "生成夏季活动方案时可以调用本资料。",
                    ]
                ),
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"

            with redirect_stdout(StringIO()):
                apply_context_library_update(project_dir, library_dir=library_dir)

            self.assertTrue((library_dir / "00_library_index.md").exists())
            self.assertTrue((library_dir / "evolution_log.md").exists())
            brand_entries = list((library_dir / "brand").glob("*.md"))
            project_entries = list((library_dir / "project").glob("*.md"))
            self.assertEqual(len(brand_entries), 1)
            self.assertEqual(project_entries, [])
            entry_text = brand_entries[0].read_text(encoding="utf-8")
            self.assertIn("# 夏季关键词", entry_text)
            self.assertIn("城市、清爽、轻便、日常。", entry_text)
            log_text = (library_dir / "evolution_log.md").read_text(encoding="utf-8")
            self.assertIn("demo_project", log_text)
            self.assertIn("LCE001", log_text)
            do_not_promote = (library_dir / "review_queue" / "do_not_promote.md").read_text(encoding="utf-8")
            self.assertIn("不把临时预算写入长期库", do_not_promote)
            self.assertTrue((library_dir / "review_queue" / "conflicts.md").exists())
            updates = (library_dir / "review_queue" / "updates.md").read_text(encoding="utf-8")
            self.assertIn("夏季关键词需要补充轻便表达", updates)
            self.assertIn("可能与旧品牌口径不一致", updates)
            self.assertIn("来源文件修改时间较新", updates)
            retrieval_notes = (library_dir / "retrieval_maps" / "source_packages.md").read_text(encoding="utf-8")
            self.assertIn("生成夏季活动方案时可以调用本资料", retrieval_notes)
            index_text = (library_dir / "00_library_index.md").read_text(encoding="utf-8")
            self.assertIn("| brand | 1 |", index_text)
            self.assertIn("| project | 0 |", index_text)
            self.assertIn("Do Not Promote Records: 1", index_text)
            self.assertIn("Existing Updates: 1", index_text)
            self.assertIn("Retrieval Note Batches: 1", index_text)

    def test_apply_context_library_update_queues_conflicts_without_overwriting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            outputs.mkdir(parents=True)
            (outputs / "11_context_library_update_plan.md").write_text(
                "\n".join(
                    [
                        "# Context Library Update Plan",
                        "",
                        "## 2. New Context Entries",
                        "",
                        "| Entry ID | 建议归档位置 | 标题 | 内容摘要 | 来源资产 | 稳定性 | 写入建议 |",
                        "|---|---|---|---|---|---|---|",
                        "| LCE009 | brand | 夏季关键词 | 新版本关键词摘要。 | CA009 | 项目期有效 | 写入 |",
                    ]
                ),
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            existing = library_dir / "brand" / "existing-summer.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("# 夏季关键词\n\n旧版本内容。\n", encoding="utf-8")

            with redirect_stdout(StringIO()):
                apply_context_library_update(project_dir, library_dir=library_dir)

            brand_entries = list((library_dir / "brand").glob("*.md"))
            self.assertEqual(brand_entries, [existing])
            self.assertIn("旧版本内容", existing.read_text(encoding="utf-8"))
            conflicts = library_dir / "review_queue" / "conflicts.md"
            self.assertTrue(conflicts.exists())
            conflict_text = conflicts.read_text(encoding="utf-8")
            self.assertIn("LCE009", conflict_text)
            self.assertIn("新版本关键词摘要", conflict_text)
            self.assertIn("brand/existing-summer.md", conflict_text)
            log_text = (library_dir / "evolution_log.md").read_text(encoding="utf-8")
            self.assertIn("No context entries applied", log_text)
            index_text = (library_dir / "00_library_index.md").read_text(encoding="utf-8")
            self.assertIn("Conflicts: 1", index_text)

    def test_apply_context_library_update_queues_source_version_groups_as_updates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            converted = project_dir / "converted_markdown"
            outputs.mkdir(parents=True)
            converted.mkdir()
            (outputs / "11_context_library_update_plan.md").write_text(
                "\n".join(
                    [
                        "# Context Library Update Plan",
                        "",
                        "## 2. New Context Entries",
                        "",
                        "| Entry ID | 建议归档位置 | 标题 | 内容摘要 | 来源资产 | 稳定性 | 写入建议 |",
                        "|---|---|---|---|---|---|---|",
                        "| LCE010 | project | 夏季策略复盘 | 资料存在多个版本，需要先复核。 | CA010 | 待验证 | 暂存 |",
                    ]
                ),
                encoding="utf-8",
            )
            (converted / "source_version_report.md").write_text(
                "\n".join(
                    [
                        "# Source Version Report",
                        "",
                        "## 版本线索总览",
                        "",
                        "- 来源文件数：2",
                        "- 疑似多版本组数：1",
                        "- 最新修改时间线索：优先作为版本判断依据，但不自动覆盖已有品牌知识。",
                        "",
                        "## 疑似多版本资料",
                        "",
                        "### summer_strategy",
                        "",
                        "- 最新修改时间线索：S002 / summer_strategy_v2.pdf / 2026-03-08T18:30:00+08:00",
                        "- 建议动作：进入更新/冲突复核队列；不自动覆盖旧知识。",
                        "",
                        "| 来源编号 | 原始文件 | 创建时间 | 修改时间 | 转写稿 | 外部来源 |",
                        "|---|---|---|---|---|---|",
                        "| S001 | summer_strategy_v1.pdf | 2026-01-01T09:00:00+08:00 | 2026-01-02T09:00:00+08:00 | source_transcripts/S001.md | ima / 示例库 |",
                        "| S002 | summer_strategy_v2.pdf | 2026-01-01T09:00:00+08:00 | 2026-03-08T18:30:00+08:00 | source_transcripts/S002.md | ima / 示例库 |",
                    ]
                ),
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"

            with redirect_stdout(StringIO()):
                apply_context_library_update(project_dir, library_dir=library_dir)

            updates = (library_dir / "review_queue" / "updates.md").read_text(encoding="utf-8")
            self.assertIn("疑似多版本资料：summer_strategy", updates)
            self.assertIn("summer_strategy_v2.pdf", updates)
            self.assertIn("不自动覆盖旧知识", updates)
            self.assertIn("S001", updates)
            self.assertIn("S002", updates)
            index_text = (library_dir / "00_library_index.md").read_text(encoding="utf-8")
            self.assertIn("Existing Updates: 1", index_text)

    def test_cli_apply_library_update_command(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            outputs.mkdir(parents=True)
            (outputs / "11_context_library_update_plan.md").write_text(
                "\n".join(
                    [
                        "# Context Library Update Plan",
                        "",
                        "## 2. New Context Entries",
                        "",
                        "| Entry ID | 建议归档位置 | 标题 | 内容摘要 | 来源资产 | 稳定性 | 写入建议 |",
                        "|---|---|---|---|---|---|---|",
                        "| LCE001 | language | 体验表达 | 使用体验型表达。 | CA009 | 待验证 | 写入 |",
                    ]
                ),
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "library"
            argv = sys.argv
            sys.argv = ["brand-skill", "apply-library-update", str(project_dir), "--library-dir", str(library_dir)]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            self.assertEqual(len(list((library_dir / "language").glob("*.md"))), 1)

    def test_build_library_report_creates_marketer_friendly_html(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            library_dir = Path(temp_dir) / "brand_context_library"
            (library_dir / "brand").mkdir(parents=True)
            (library_dir / "project").mkdir()
            (library_dir / "review_queue").mkdir()
            (library_dir / "retrieval_maps").mkdir()
            (library_dir / "brand" / "summer-keywords.md").write_text("# 夏季关键词\n", encoding="utf-8")
            (library_dir / "project" / "launch-plan.md").write_text("# 上市计划\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text(
                "# 旧知识更新队列\n\n## 2026-06-10T00:00:00Z｜demo\n\n### 待检索\n",
                encoding="utf-8",
            )
            (library_dir / "review_queue" / "conflicts.md").write_text(
                "# Context Library Conflict Queue\n\n## 2026-06-10T00:00:00Z｜demo\n",
                encoding="utf-8",
            )
            (library_dir / "retrieval_maps" / "source_packages.md").write_text(
                "# Source Package Retrieval Notes\n\n## 2026-06-10T00:00:00Z｜demo\n\n生成夏季活动方案时可以调用本资料。\n",
                encoding="utf-8",
            )
            (library_dir / "evolution_log.md").write_text(
                "# Context Evolution Log\n\n## 2026-06-10T00:00:00Z｜demo\n\n- LCE001: 夏季关键词 -> `brand/summer-keywords.md`\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_library_report(library_dir)

            report = library_dir / "library_report.html"
            text = report.read_text(encoding="utf-8")
            self.assertTrue(report.exists())
            self.assertIn("品牌知识库概览", text)
            self.assertIn("已沉淀 2 个知识条目", text)
            self.assertIn("待处理 2 项", text)
            self.assertIn("生成夏季活动方案时可以调用本资料", text)
            self.assertIn("夏季关键词", text)
            self.assertIn("Brand Context Map", text)
            self.assertIn('class="context-map"', text)
            self.assertIn('data-node-type="category"', text)
            self.assertIn('data-node-type="entry"', text)
            self.assertIn("Knowledge Explorer", text)
            self.assertIn("搜索知识条目", text)
            self.assertIn("条目详情", text)
            self.assertIn("window.__BRAND_CONTEXT_LIBRARY__", text)
            self.assertIn("function renderExplorer", text)
            self.assertIn("function selectEntry", text)
            self.assertIn("categoryFilter", text)
            self.assertIn("statusFilter", text)
            self.assertIn("searchInput", text)
            self.assertIn("addEventListener", text)
            self.assertIn("暂无摘要", text)
            self.assertNotIn("Source Anchor", text)
            self.assertNotIn("Risk Level", text)

    def test_build_library_report_uses_taxonomy_for_dynamic_categories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            library_dir = Path(temp_dir) / "brand_context_library"
            (library_dir / "channel_policy").mkdir(parents=True)
            (library_dir / "review_queue").mkdir()
            (library_dir / "retrieval_maps").mkdir()
            (library_dir / "taxonomy.md").write_text(
                "\n".join(
                    [
                        "# Knowledge Taxonomy",
                        "",
                        "| 分类 ID | 展示名称 | 说明 | 来源 | 状态 |",
                        "|---|---|---|---|---|",
                        "| channel_policy | 渠道政策 | 经销商、平台、渠道动作和政策 | AI 建议 | 待确认 |",
                    ]
                ),
                encoding="utf-8",
            )
            (library_dir / "channel_policy" / "dealer-policy.md").write_text(
                "# 经销商政策\n\n## 内容摘要\n\n用于沉淀渠道政策。\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_library_report(library_dir)

            text = (library_dir / "library_report.html").read_text(encoding="utf-8")
            self.assertIn("渠道政策", text)
            self.assertIn("AI 建议", text)
            self.assertIn("待确认", text)
            self.assertIn("经销商政策", text)
            self.assertNotIn("channel_policy</span>", text)

    def test_build_library_report_hides_empty_default_categories_without_taxonomy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            library_dir = Path(temp_dir) / "brand_context_library"
            (library_dir / "brand").mkdir(parents=True)
            (library_dir / "asset").mkdir()
            (library_dir / "review_queue").mkdir()
            (library_dir / "retrieval_maps").mkdir()
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")

            with redirect_stdout(StringIO()):
                build_library_report(library_dir)

            text = (library_dir / "library_report.html").read_text(encoding="utf-8")
            self.assertIn("品牌认知", text)
            self.assertIn('"id": "brand"', text)
            self.assertNotIn("素材资产", text)
            self.assertNotIn('"id": "asset"', text)

    def test_build_library_report_shows_empty_categories_declared_by_taxonomy(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            library_dir = Path(temp_dir) / "brand_context_library"
            (library_dir / "brand").mkdir(parents=True)
            (library_dir / "asset").mkdir()
            (library_dir / "review_queue").mkdir()
            (library_dir / "retrieval_maps").mkdir()
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "taxonomy.md").write_text(
                "\n".join(
                    [
                        "# Knowledge Taxonomy",
                        "",
                        "| 分类 ID | 展示名称 | 说明 | 来源 | 状态 |",
                        "|---|---|---|---|---|",
                        "| asset | 素材资产 | 图片、视频、脚本、视觉风格 | 用户确认 | 已启用 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_library_report(library_dir)

            text = (library_dir / "library_report.html").read_text(encoding="utf-8")
            self.assertIn("素材资产", text)
            self.assertIn('"id": "asset"', text)
            self.assertIn("用户确认", text)

    def test_build_library_report_marks_entry_review_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            library_dir = Path(temp_dir) / "brand_context_library"
            (library_dir / "brand").mkdir(parents=True)
            (library_dir / "language").mkdir()
            (library_dir / "review_queue").mkdir()
            (library_dir / "retrieval_maps").mkdir()
            (library_dir / "brand" / "summer-keywords.md").write_text(
                "# 夏季关键词\n\n## 内容摘要\n\n需要判断是否替换旧版本。\n",
                encoding="utf-8",
            )
            (library_dir / "language" / "experience-claims.md").write_text(
                "# 体验表达\n\n## 内容摘要\n\n需要补充新版表达边界。\n",
                encoding="utf-8",
            )
            (library_dir / "review_queue" / "conflicts.md").write_text(
                "\n".join(
                    [
                        "# Context Library Conflict Queue",
                        "",
                        "## 2026-06-10T00:00:00Z｜demo",
                        "",
                        "### LCE009｜夏季关键词",
                        "",
                        "- Existing Entry: `brand/summer-keywords.md`",
                    ]
                ),
                encoding="utf-8",
            )
            (library_dir / "review_queue" / "updates.md").write_text(
                "\n".join(
                    [
                        "# 旧知识更新队列",
                        "",
                        "## 2026-06-10T00:00:00Z｜demo",
                        "",
                        "### 体验表达",
                        "",
                        "- 更新方式：补充",
                        "- 版本判断依据：来源文件修改时间较新",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_library_report(library_dir)

            text = (library_dir / "library_report.html").read_text(encoding="utf-8")
            self.assertIn('"title": "夏季关键词"', text)
            self.assertIn('"status": "冲突"', text)
            self.assertIn('"reviewNote": "存在冲突待判断"', text)
            self.assertIn('"title": "体验表达"', text)
            self.assertIn('"status": "待更新"', text)
            self.assertIn('"reviewNote": "旧知识可能需要更新"', text)

    def test_build_library_report_shows_review_queue_details(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            library_dir = Path(temp_dir) / "brand_context_library"
            (library_dir / "brand").mkdir(parents=True)
            (library_dir / "review_queue").mkdir()
            (library_dir / "retrieval_maps").mkdir()
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text(
                "\n".join(
                    [
                        "# 旧知识更新队列",
                        "",
                        "## 2026-06-10T00:00:00Z｜demo",
                        "",
                        "### 疑似多版本资料：summer_strategy",
                        "",
                        "- 更新方式：版本复核",
                        "- 冲突或风险：同主题多版本资料并存；不自动覆盖旧知识。",
                        "- 版本判断依据：source_version_report.md / 最新修改时间线索",
                        "",
                        "#### 新信息",
                        "",
                        "最新修改时间线索：S002 / summer_strategy_v2.pdf / 2026-03-08T18:30:00+08:00",
                    ]
                ),
                encoding="utf-8",
            )
            (library_dir / "review_queue" / "conflicts.md").write_text(
                "\n".join(
                    [
                        "# Context Library Conflict Queue",
                        "",
                        "## 2026-06-10T00:00:00Z｜demo",
                        "",
                        "### LCE009｜夏季关键词",
                        "",
                        "- Existing Entry: `brand/summer-keywords.md`",
                        "- Write Recommendation: 写入",
                    ]
                ),
                encoding="utf-8",
            )
            (library_dir / "review_queue" / "do_not_promote.md").write_text(
                "# Do Not Promote Queue\n\n## 2026-06-10T00:00:00Z｜demo\n\n- 临时预算不进入长期库。\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_library_report(library_dir)

            text = (library_dir / "library_report.html").read_text(encoding="utf-8")
            self.assertIn("待处理事项", text)
            self.assertIn("旧知识待更新", text)
            self.assertIn("疑似多版本资料：summer_strategy", text)
            self.assertIn("summer_strategy_v2.pdf", text)
            self.assertIn("不自动覆盖旧知识", text)
            self.assertIn("冲突待判断", text)
            self.assertIn("LCE009｜夏季关键词", text)
            self.assertIn("brand/summer-keywords.md", text)
            self.assertIn("不进入长期库", text)
            self.assertIn("临时预算不进入长期库", text)

    def test_cli_build_library_report_command(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            library_dir = Path(temp_dir) / "brand_context_library"
            (library_dir / "brand").mkdir(parents=True)
            (library_dir / "review_queue").mkdir()
            (library_dir / "retrieval_maps").mkdir()
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            argv = sys.argv
            sys.argv = ["brand-skill", "build-library-report", str(library_dir)]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            self.assertTrue((library_dir / "library_report.html").exists())

    def test_verify_project_contract_passes_when_required_evidence_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            transcripts.mkdir(parents=True)
            outputs.mkdir(parents=True)
            required_outputs = [
                "02_document_profile.md",
                "03_marketing_semantic_transcript.md",
                "04_key_facts_and_claims.md",
                "05_strategy_and_execution_map.md",
                "06_risk_and_review_items.md",
                "10_context_asset_index.md",
                "11_context_library_update_plan.md",
            ]
            for filename in required_outputs:
                (outputs / filename).write_text(f"# {filename}\n", encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "# Source Conversion Report\n\n## 识别质量摘要\n\n- 总页数：1\n- 视觉/表格/小字限制：复杂版式需复核。\n- 人工复核建议：检查低置信度区域。\n\n| 原始文件创建时间 | 原始文件修改时间 | 低置信度区域 |\n|---|---|---|\n| 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n## 识别质量总览\n\n- 需要复核页数：0\n\n| 建议动作 |\n|---|\n| 继续后续语义编译 |\n",
                encoding="utf-8",
            )
            (converted / "source_version_report.md").write_text(
                "# Source Version Report\n\n## 版本线索总览\n\n- 疑似多版本组数：0\n- 最新修改时间线索：不自动覆盖已有品牌知识。\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            review_dir = project_dir / "review"
            review_dir.mkdir()
            (review_dir / "brand_review.html").write_text(
                "识别问题待处理 需要处理的问题 文件大纲参考 自动通过，无需人工处理",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                verify_project_contract(project_dir, library_dir=library_dir)

            self.assertIn("Contract verification passed", stdout.getvalue())

    def test_verify_project_contract_writes_pass_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            transcripts.mkdir(parents=True)
            outputs.mkdir(parents=True)
            for filename in [
                "02_document_profile.md",
                "03_marketing_semantic_transcript.md",
                "04_key_facts_and_claims.md",
                "05_strategy_and_execution_map.md",
                "06_risk_and_review_items.md",
                "10_context_asset_index.md",
                "11_context_library_update_plan.md",
            ]:
                (outputs / filename).write_text(f"# {filename}\n", encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "# Source Conversion Report\n\n## 识别质量摘要\n\n- 总页数：1\n- 视觉/表格/小字限制：复杂版式需复核。\n- 人工复核建议：检查低置信度区域。\n\n| 原始文件创建时间 | 原始文件修改时间 | 低置信度区域 |\n|---|---|---|\n| 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n## 识别质量总览\n\n- 需要复核页数：0\n\n| 建议动作 |\n|---|\n| 继续后续语义编译 |\n",
                encoding="utf-8",
            )
            (converted / "source_version_report.md").write_text(
                "# Source Version Report\n\n## 版本线索总览\n\n- 疑似多版本组数：0\n- 最新修改时间线索：不自动覆盖已有品牌知识。\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            review_dir = project_dir / "review"
            review_dir.mkdir()
            (review_dir / "brand_review.html").write_text(
                "识别问题待处理 需要处理的问题 文件大纲参考",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情",
                encoding="utf-8",
            )
            report_path = project_dir / "contract_verification_report.md"

            with redirect_stdout(StringIO()):
                verify_project_contract(project_dir, library_dir=library_dir, report_path=report_path)

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("# Contract Verification Report", report)
            self.assertIn("Status: passed", report)
            self.assertIn("Checked Evidence", report)
            self.assertIn("No issues found.", report)

    def test_verify_project_contract_writes_failure_report_before_exit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            project_dir.mkdir()
            report_path = project_dir / "contract_verification_report.md"

            with redirect_stdout(StringIO()):
                with self.assertRaises(SystemExit):
                    verify_project_contract(
                        project_dir,
                        library_dir=Path(temp_dir) / "missing_library",
                        report_path=report_path,
                    )

            report = report_path.read_text(encoding="utf-8")
            self.assertIn("Status: failed", report)
            self.assertIn("Missing outputs directory", report)
            self.assertIn("Missing context library", report)

    def test_cli_verify_contract_can_write_report(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            project_dir.mkdir()
            argv = sys.argv
            sys.argv = ["brand-skill", "verify-contract", str(project_dir), "--write-report"]
            try:
                with redirect_stdout(StringIO()):
                    with self.assertRaises(SystemExit):
                        cli_main()
            finally:
                sys.argv = argv

            report = project_dir / "contract_verification_report.md"
            self.assertTrue(report.exists())
            self.assertIn("Status: failed", report.read_text(encoding="utf-8"))

    def test_cli_demo_contract_runs_library_report_and_verification(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path("examples/anonymous_marketing_campaign")
            library_dir = Path(temp_dir) / "brand_context_library"
            report_path = project_dir / "contract_verification_report.md"
            if report_path.exists():
                report_path.unlink()
            argv = sys.argv
            sys.argv = ["brand-skill", "demo-contract", str(project_dir), "--library-dir", str(library_dir)]
            try:
                with redirect_stdout(StringIO()) as stdout:
                    cli_main()
            finally:
                sys.argv = argv

            output = stdout.getvalue()
            self.assertIn("Context library updated", output)
            self.assertIn("Library report generated", output)
            self.assertIn("Contract verification passed", output)
            self.assertTrue((library_dir / "library_report.html").exists())
            self.assertIn("Status: passed", report_path.read_text(encoding="utf-8"))
            report_path.unlink()

    def test_verify_project_contract_fails_without_exception_review_page(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            transcripts.mkdir(parents=True)
            outputs.mkdir(parents=True)
            for filename in [
                "02_document_profile.md",
                "03_marketing_semantic_transcript.md",
                "04_key_facts_and_claims.md",
                "05_strategy_and_execution_map.md",
                "06_risk_and_review_items.md",
                "10_context_asset_index.md",
                "11_context_library_update_plan.md",
            ]:
                (outputs / filename).write_text(f"# {filename}\n", encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "| 原始文件创建时间 | 原始文件修改时间 | 低置信度区域 |\n|---|---|---|\n| 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=library_dir)

            self.assertIn("Missing exception review page", stdout.getvalue())

    def test_verify_project_contract_fails_when_review_page_overexposes_backend_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            transcripts.mkdir(parents=True)
            outputs.mkdir(parents=True)
            for filename in [
                "02_document_profile.md",
                "03_marketing_semantic_transcript.md",
                "04_key_facts_and_claims.md",
                "05_strategy_and_execution_map.md",
                "06_risk_and_review_items.md",
                "10_context_asset_index.md",
                "11_context_library_update_plan.md",
            ]:
                (outputs / filename).write_text(f"# {filename}\n", encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "| 原始文件创建时间 | 原始文件修改时间 | 低置信度区域 |\n|---|---|---|\n| 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            review_dir = project_dir / "review"
            review_dir.mkdir()
            (review_dir / "brand_review.html").write_text(
                "Context Asset Index Review 来源位置：S001#page=1 class=\"source-anchor\"",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=library_dir)

            output = stdout.getvalue()
            self.assertIn("Review page missing exception-review marker", output)
            self.assertIn("Review page overexposes backend marker", output)

    def test_verify_project_contract_fails_with_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            (project_dir / "outputs").mkdir(parents=True)

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=Path(temp_dir) / "missing_library")

            output = stdout.getvalue()
            self.assertIn("Contract verification failed", output)
            self.assertIn("Missing required output", output)
            self.assertIn("Missing context library", output)

    def test_verify_project_contract_fails_without_source_quality_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            outputs = project_dir / "outputs"
            transcripts.mkdir(parents=True)
            outputs.mkdir(parents=True)
            for filename in [
                "02_document_profile.md",
                "03_marketing_semantic_transcript.md",
                "04_key_facts_and_claims.md",
                "05_strategy_and_execution_map.md",
                "06_risk_and_review_items.md",
                "10_context_asset_index.md",
                "11_context_library_update_plan.md",
            ]:
                (outputs / filename).write_text(f"# {filename}\n", encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "| 原始文件创建时间 | 原始文件修改时间 | 低置信度区域 |\n|---|---|---|\n| 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=Path(temp_dir) / "missing_library")

            self.assertIn("Source conversion report missing quality marker", stdout.getvalue())

    def test_cli_verify_contract_command_reports_missing_evidence(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            project_dir.mkdir()
            argv = sys.argv
            sys.argv = ["brand-skill", "verify-contract", str(project_dir)]
            try:
                with redirect_stdout(StringIO()) as stdout:
                    with self.assertRaises(SystemExit):
                        cli_main()
            finally:
                sys.argv = argv

            self.assertIn("Contract verification failed", stdout.getvalue())

    def test_verify_contract_fails_when_private_test_runs_are_tracked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            private_file = repo_dir / "_private_test_runs" / "sample.md"
            private_file.parent.mkdir()
            private_file.write_text("private fixture", encoding="utf-8")
            subprocess.run(["git", "add", str(private_file)], cwd=repo_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            project_dir = repo_dir / "demo_project"
            project_dir.mkdir()
            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=repo_dir / "missing_library", repo_dir=repo_dir)

            output = stdout.getvalue()
            self.assertIn("Tracked private test file", output)
            self.assertIn("_private_test_runs/sample.md", output)

    def test_verify_contract_fails_when_library_report_uses_remote_resources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            transcripts.mkdir(parents=True)
            outputs.mkdir(parents=True)
            for filename in [
                "02_document_profile.md",
                "03_marketing_semantic_transcript.md",
                "04_key_facts_and_claims.md",
                "05_strategy_and_execution_map.md",
                "06_risk_and_review_items.md",
                "10_context_asset_index.md",
                "11_context_library_update_plan.md",
            ]:
                (outputs / filename).write_text(f"# {filename}\n", encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "| 原始文件创建时间 | 原始文件修改时间 | 低置信度区域 |\n|---|---|---|\n| 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情 <script src=\"https://cdn.example.com/app.js\"></script>",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=library_dir)

            self.assertIn("Library report references remote resource", stdout.getvalue())

    def test_verify_contract_fails_when_library_report_overexposes_backend_markers(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            transcripts.mkdir(parents=True)
            outputs.mkdir(parents=True)
            for filename in [
                "02_document_profile.md",
                "03_marketing_semantic_transcript.md",
                "04_key_facts_and_claims.md",
                "05_strategy_and_execution_map.md",
                "06_risk_and_review_items.md",
                "10_context_asset_index.md",
                "11_context_library_update_plan.md",
            ]:
                (outputs / filename).write_text(f"# {filename}\n", encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "| 原始文件创建时间 | 原始文件修改时间 | 低置信度区域 |\n|---|---|---|\n| 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            review_dir = project_dir / "review"
            review_dir.mkdir()
            (review_dir / "brand_review.html").write_text(
                "识别问题待处理 需要处理的问题 文件大纲参考",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情 Source Anchor Risk Level 来源锚点 风险等级",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=library_dir)

            self.assertIn("Library report overexposes backend marker", stdout.getvalue())

    def test_verify_contract_scans_tracked_files_with_privacy_terms_env(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            leaked = repo_dir / "README.md"
            leaked.write_text("This file contains ACME_PRIVATE_MARKER.", encoding="utf-8")
            subprocess.run(["git", "add", str(leaked)], cwd=repo_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            project_dir = repo_dir / "demo_project"
            project_dir.mkdir()

            original = os.environ.get("BRAND_SKILL_PRIVACY_TERMS_REGEX")
            os.environ["BRAND_SKILL_PRIVACY_TERMS_REGEX"] = "ACME_PRIVATE_MARKER"
            try:
                with redirect_stdout(StringIO()) as stdout:
                    with self.assertRaises(SystemExit):
                        verify_project_contract(project_dir, library_dir=repo_dir / "missing_library", repo_dir=repo_dir)
            finally:
                if original is None:
                    os.environ.pop("BRAND_SKILL_PRIVACY_TERMS_REGEX", None)
                else:
                    os.environ["BRAND_SKILL_PRIVACY_TERMS_REGEX"] = original

            output = stdout.getvalue()
            self.assertIn("Privacy term match in tracked file", output)
            self.assertIn("README.md", output)

    def test_verify_contract_fails_when_outputs_claim_brand_confirmed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            outputs = project_dir / "outputs"
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            transcripts.mkdir(parents=True)
            outputs.mkdir(parents=True)
            required_outputs = [
                "02_document_profile.md",
                "03_marketing_semantic_transcript.md",
                "04_key_facts_and_claims.md",
                "05_strategy_and_execution_map.md",
                "06_risk_and_review_items.md",
                "10_context_asset_index.md",
                "11_context_library_update_plan.md",
            ]
            for filename in required_outputs:
                content = "# Evidence\n"
                if filename == "02_document_profile.md":
                    content += "\n| 字段 | 内容 | 信息状态 |\n|---|---|---|\n| 品牌口径 | 示例 | 已品牌确认 |\n"
                (outputs / filename).write_text(content, encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "| 原始文件创建时间 | 原始文件修改时间 | 低置信度区域 |\n|---|---|---|\n| 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=library_dir)

            output = stdout.getvalue()
            self.assertIn("Unapproved confirmed status in generated file", output)
            self.assertIn("outputs/02_document_profile.md", output)


if __name__ == "__main__":
    unittest.main()
