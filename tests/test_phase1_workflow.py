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
from brand_skill.contract_verifier import (
    _check_value_benchmark,
    _retrieval_map_issues,
    _source_page_coverage_issues,
    _source_quality_anchor_coverage_issues,
    verify_project_contract,
)
from brand_skill.library_report import build_library_report
from brand_skill.library_writer import apply_context_library_update
from brand_skill.ima_importer import import_ima_media
from brand_skill.output_compiler import compile_structured_outputs
from brand_skill.review_pack import build_review_pack
from brand_skill.mineru_adapter import check_mineru_readiness, plan_mineru_evaluation, scaffold_mineru_evaluation_results
from brand_skill.value_benchmark import build_value_benchmark
from brand_skill.source_quality import build_source_quality_report
from brand_skill.source_facts import build_source_facts
from brand_skill.source_engine_eval import check_source_engines, plan_source_engine_evaluation, scaffold_source_engine_evaluation_results
from brand_skill.source_versions import build_source_version_report
from brand_skill.source_converter import convert_source
from brand_skill.validators import (
    check_brand_lock_sheet_draft,
    check_claim_matrix,
    check_public_safe_text,
)
from brand_skill.workflow import OUTPUT_FILES, build_prompt_pack, init_project, scaffold_output


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

    def _write_source_engine_reports(self, project_dir: Path) -> None:
        converted = project_dir / "converted_markdown"
        converted.mkdir(parents=True, exist_ok=True)
        (converted / "source_engine_readiness_report.md").write_text(
            "# Source Engine Readiness Report\n\n"
            "- Microsoft MarkItDown / MinerU 都只是 Source-to-Markdown 候选引擎。\n\n"
            "| Engine | 状态 |\n"
            "|---|---|\n"
            "| pymupdf4llm | 内置默认 |\n"
            "| markitdown | Microsoft MarkItDown 候选 |\n"
            "| mineru | MinerU 候选 |\n",
            encoding="utf-8",
        )
        (converted / "source_engine_eval_plan.md").write_text(
            "# Source Engine Evaluation Plan\n\n"
            "- Baseline：pymupdf4llm。\n"
            "- 候选：MarkItDown / MinerU。\n"
            "- 隐私：真实品牌资料只在私有目录评估。\n\n"
            "| 维度 | pymupdf4llm baseline | MarkItDown | MinerU |\n"
            "|---|---|---|---|\n"
            "| 文字覆盖率 | 待记录 | 待记录 | 待记录 |\n",
            encoding="utf-8",
        )
        (converted / "source_engine_eval_results.md").write_text(
            "# Source Engine Evaluation Results\n\n"
            "- Baseline：pymupdf4llm。\n"
            "- 候选：MarkItDown / MinerU。\n"
            "- 隐私：真实品牌资料只在私有目录评估。\n\n"
            "| Source Anchor | pymupdf4llm baseline 观测 | 是否调整默认链路 |\n"
            "|---|---|---|\n"
            "| S001#page=1 | baseline 可观测证据 | 否，待证据 |\n",
            encoding="utf-8",
        )

    def _quality_sampling_log_text(self) -> str:
        return (
            "# Quality Sampling Log\n\n"
            "| 当前结论 | 未形成 90% 页面级 / 事实级准确率证据 |\n\n"
            "## Page Sampling Plan\n\n"
            "| sample_id | source_anchor | sampled_reason | source_state | accuracy_result | correction_needed |\n"
            "|---|---|---|---|---|---|\n"
            "| QS001 | S001#page=1 | 抽样 | 待回看原页 | 待抽样 | 人工抽样 |\n\n"
            "## Pass Rate\n\n"
            "| 指标 | 数值 |\n"
            "|---|---:|\n"
            "| 页面级通过率 | 未形成证据 |\n\n"
            "- 未完成原页核对前，不得声明 90% 准确率。\n"
        )

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

    def test_init_project_guide_uses_current_output_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"

            with redirect_stdout(StringIO()):
                init_project(project_dir)

            guide = (project_dir / "brand_input" / "README.md").read_text(encoding="utf-8")
            self.assertIn("outputs/08_review_pack.md", guide)
            self.assertIn("review/brand_review.html", guide)
            self.assertNotIn("outputs/<project_slug>", guide)

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

    def test_source_page_coverage_detects_missing_transcript_anchors(self) -> None:
        report_text = (
            "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n"
            "| S001 | demo.pdf | 2026 | 2026 | 2026 | transcript.md | pymupdf4llm | PDF | 否 | 1-3 |\n"
        )
        transcript_text = "Source Anchor：S001#page=1\nSource Anchor：S001#page=2\n"

        self.assertEqual(
            _source_page_coverage_issues(report_text, transcript_text),
            ["Source page coverage mismatch: S001 expected 3, transcript anchors 2"],
        )

    def test_source_quality_anchor_coverage_detects_missing_quality_rows(self) -> None:
        transcript_text = "Source Anchor：S001#page=1\nSource Anchor：S001#page=2\n"
        quality_text = (
            "# Source Quality Report\n\n"
            "## 全部页面读取状态\n\n"
            "| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 读取状态 | 低置信度说明 |\n"
            "|---|---|---|---|---|---|---|---|\n"
            "| S001#page=1 | demo.pdf | 120 | 0 | 0 | 0 | 可进入后续编译 | 无明显低置信度 |\n"
        )

        self.assertEqual(
            _source_quality_anchor_coverage_issues(quality_text, transcript_text),
            ["Source quality coverage missing anchors: S001#page=2"],
        )

    def test_retrieval_map_requires_source_fact_and_transcript_paths(self) -> None:
        retrieval_text = (
            "# Source Package Retrieval Notes\n\n"
            "| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n"
            "|---|---|---|---|\n"
            "| Campaign brief | outputs/10_context_asset_index.md | outputs/10_context_asset_index.md | outputs/03_marketing_semantic_transcript.md |\n"
        )

        self.assertEqual(
            _retrieval_map_issues(retrieval_text),
            [
                "Library retrieval map missing source facts path: converted_markdown/source_facts/",
                "Library retrieval map missing transcript path: converted_markdown/source_transcripts/",
            ],
        )

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
            self.assertIn("转写时间", report_text)
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

    def test_convert_source_splits_markdown_slide_headings_into_page_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "campaign_plan"
            source_dir.mkdir(parents=True)
            (source_dir / "slides.md").write_text(
                "# 匿名活动方案\n\n"
                "> 本文件为虚构源材料。\n\n"
                "## Slide 1｜项目背景\n\n"
                "建立夏季品牌联想。\n\n"
                "## Slide 2｜触点规划\n\n"
                "- 线下体验。\n"
                "- 社媒内容。\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")

            transcript = project_dir / "converted_markdown" / "source_transcripts" / "S001_campaign_plan.md"
            report = project_dir / "converted_markdown" / "conversion_report.md"
            transcript_text = transcript.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")
            self.assertIn("Source Anchor：S001#page=1", transcript_text)
            self.assertIn("Source Section：Slide 1｜项目背景", transcript_text)
            self.assertIn("Source Anchor：S001#page=2", transcript_text)
            self.assertIn("Source Section：Slide 2｜触点规划", transcript_text)
            self.assertIn("本文件为虚构源材料", transcript_text)
            self.assertIn("| S001 | slides.md |", report_text)
            self.assertIn(" | 1-2 | ", report_text)

    def test_convert_source_removes_stale_transcripts_before_rewriting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "campaign"
            transcripts_dir = project_dir / "converted_markdown" / "source_transcripts"
            source_dir.mkdir(parents=True)
            transcripts_dir.mkdir(parents=True)
            (source_dir / "brief.md").write_text("# Brief\n\n活动重点。", encoding="utf-8")
            (transcripts_dir / "S999_old_source.md").write_text("stale", encoding="utf-8")

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="pymupdf4llm")

            self.assertFalse((transcripts_dir / "S999_old_source.md").exists())
            self.assertTrue((transcripts_dir / "S001_campaign.md").exists())

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

    def test_build_source_facts_removes_stale_fact_files_before_rewriting(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            transcripts_dir = project_dir / "converted_markdown" / "source_transcripts"
            facts_dir = project_dir / "converted_markdown" / "source_facts"
            transcripts_dir.mkdir(parents=True)
            facts_dir.mkdir(parents=True)
            (facts_dir / "S999_old_source_facts.md").write_text("stale", encoding="utf-8")
            (transcripts_dir / "S001_demo.md").write_text(
                "# Source Transcript｜demo.md\n\n"
                "## Source Metadata\n- Source ID：S001\n\n"
                "## Page 1\n- Source Anchor：S001#page=1\n\n"
                "### Text\n活动重点。\n\n"
                "### Low Confidence / Need Review\n- 无明显低置信度\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_source_facts(project_dir)

            self.assertFalse((facts_dir / "S999_old_source_facts.md").exists())
            self.assertTrue((facts_dir / "S001_demo_source_facts.md").exists())

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

    def test_convert_source_explains_legacy_ppt_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source"
            source_dir.mkdir(parents=True)
            (source_dir / "brand_training.ppt").write_bytes(b"legacy-ppt")

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    convert_source(project_dir, engine="pymupdf4llm")

            output = stdout.getvalue()
            self.assertIn("brand_training.ppt", output)
            self.assertIn("旧版 PPT 请先转成 PPTX 或 PDF", output)
            self.assertFalse((project_dir / "converted_markdown" / "conversion_report.md").exists())

    def test_convert_source_markitdown_adapter_accepts_html_source(self) -> None:
        class FakeMarkItDownResult:
            text_content = "# 活动复盘\n\n核心内容：渠道打法和投放总结。"

        class FakeMarkItDown:
            def __init__(self) -> None:
                self.paths = []

            def convert(self, path: str):
                self.paths.append(path)
                return FakeMarkItDownResult()

        fake_converter = FakeMarkItDown()

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "campaign"
            source_dir.mkdir(parents=True)
            (source_dir / "recap.html").write_text(
                "<html><body><h1>活动复盘</h1><p>核心内容：渠道打法和投放总结。</p></body></html>",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                convert_source(project_dir, engine="markitdown", markitdown_factory=lambda: fake_converter)

            transcript = project_dir / "converted_markdown" / "source_transcripts" / "S001_campaign.md"
            report = project_dir / "converted_markdown" / "conversion_report.md"
            transcript_text = transcript.read_text(encoding="utf-8")
            report_text = report.read_text(encoding="utf-8")
            self.assertEqual(fake_converter.paths, [str(source_dir / "recap.html")])
            self.assertIn("文件类型：HTML", transcript_text)
            self.assertIn("转写引擎：markitdown", transcript_text)
            self.assertIn("Source Anchor：S001#page=1", transcript_text)
            self.assertIn("渠道打法和投放总结", transcript_text)
            self.assertIn("MarkItDown 输出未保留稳定页码/slide 边界", transcript_text)
            self.assertIn("markitdown", report_text)
            self.assertIn("Microsoft MarkItDown 本地 Markdown 转换", report_text)

    def test_convert_source_markitdown_fails_with_install_hint_when_missing(self) -> None:
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "markitdown":
                raise ImportError("No module named 'markitdown'")
            return real_import(name, *args, **kwargs)

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            source_dir = project_dir / "source" / "campaign"
            source_dir.mkdir(parents=True)
            (source_dir / "brief.md").write_text("# Brief\n", encoding="utf-8")

            builtins.__import__ = fake_import
            try:
                with redirect_stdout(StringIO()) as stdout:
                    with self.assertRaises(SystemExit):
                        convert_source(project_dir, engine="markitdown")
            finally:
                builtins.__import__ = real_import

            output = stdout.getvalue()
            self.assertIn("MarkItDown is an optional source converter", output)
            self.assertIn("pip install 'markitdown[all]'", output)

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

    def test_check_source_engines_records_markitdown_and_mineru_candidates(self) -> None:
        class FakeResult:
            returncode = 0
            stdout = "tool version\n"
            stderr = ""

        calls = []

        def fake_which(name):
            if name == "markitdown":
                return "/usr/local/bin/markitdown"
            if name == "mineru":
                return None
            return None

        def fake_runner(command, **_kwargs):
            calls.append(command)
            return FakeResult()

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            with redirect_stdout(StringIO()):
                report_path = check_source_engines(project_dir, which=fake_which, runner=fake_runner)

            report_text = report_path.read_text(encoding="utf-8")
            self.assertEqual(calls, [["/usr/local/bin/markitdown", "--version"]])
            self.assertIn("# Source Engine Readiness Report", report_text)
            self.assertIn("pymupdf4llm", report_text)
            self.assertIn("markitdown", report_text)
            self.assertIn("mineru", report_text)
            self.assertIn("Microsoft MarkItDown", report_text)
            self.assertIn("未检测到 CLI", report_text)
            self.assertIn("不上传真实品牌资料", report_text)

    def test_check_source_engines_does_not_rewrite_unchanged_report_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            with redirect_stdout(StringIO()):
                report_path = check_source_engines(project_dir, which=lambda _name: None)
            original = report_path.read_text(encoding="utf-8")

            with redirect_stdout(StringIO()):
                check_source_engines(project_dir, which=lambda _name: None)

            self.assertEqual(report_path.read_text(encoding="utf-8"), original)

    def test_plan_source_engine_evaluation_creates_multiengine_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "source_quality_report.md").write_text(
                "\n".join(
                    [
                        "# Source Quality Report",
                        "",
                        "| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 |",
                        "|---|---|---|---|---|---|---|---|",
                        "| S001#page=1 | deck.pptx | 20 | 待复核 | 待复核 | 待复核 | PPTX 轻量路径未保留版式 | MinerU / 原 PPT 人工复核 |",
                        "| S002#page=3 | report.pdf | 80 | 0 | 0 | 1 | 表格结构需复核 | MinerU / 人工复核 |",
                        "| S003#page=1 | clean.pdf | 120 | 0 | 0 | 0 | 无明显低置信度 | 继续后续编译 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                report_path = plan_source_engine_evaluation(project_dir, max_pages=2)

            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("# Source Engine Evaluation Plan", report_text)
            self.assertIn("Microsoft MarkItDown", report_text)
            self.assertIn("MinerU", report_text)
            self.assertIn("pymupdf4llm baseline", report_text)
            self.assertIn("可抽取文字数", report_text)
            self.assertIn("表格数", report_text)
            self.assertIn("| S001#page=1 | deck.pptx", report_text)
            self.assertIn("MarkItDown / pymupdf4llm baseline", report_text)
            self.assertIn("| S002#page=3 | report.pdf", report_text)
            self.assertIn("真实品牌资料只能在 `_private_test_runs/`", report_text)

    def test_cli_plan_source_engine_eval_command_writes_plan(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n| Source Anchor | 原始文件 | 低置信度说明 | 建议动作 |\n|---|---|---|---|\n| S001#page=2 | sample.pdf | 可抽取文字较少 | OCR / MinerU / 人工复核 |\n",
                encoding="utf-8",
            )
            argv = sys.argv
            sys.argv = ["brand-skill", "plan-source-engine-eval", str(project_dir), "--max-pages", "1"]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            report_path = project_dir / "converted_markdown" / "source_engine_eval_plan.md"
            self.assertTrue(report_path.exists())
            self.assertIn("Source Engine Evaluation Plan", report_path.read_text(encoding="utf-8"))

    def test_scaffold_source_engine_evaluation_results_uses_plan_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "source_engine_eval_plan.md").write_text(
                "\n".join(
                    [
                        "# Source Engine Evaluation Plan",
                        "",
                        "## 建议小样",
                        "",
                        "| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 | 推荐对比引擎 |",
                        "|---|---|---|---|---|---|---|---|---|",
                        "| S001#page=1 | deck.pptx | 20 | 待复核 | 待复核 | 待复核 | PPTX 轻量路径未保留版式 | 原 PPT 人工复核 | MarkItDown / pymupdf4llm baseline |",
                        "| S002#page=3 | report.pdf | 80 | 0 | 0 | 1 | 表格结构需复核 | MinerU / 人工复核 | MinerU / MarkItDown / pymupdf4llm baseline |",
                        "",
                        "## 对比记录模板",
                        "",
                        "| 维度 | pymupdf4llm baseline | MarkItDown | MinerU | 是否改善后续知识编译 |",
                        "|---|---|---|---|---|",
                        "| 文字覆盖率 | 待记录 | 待记录 | 待记录 | 待判断 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                report_path = scaffold_source_engine_evaluation_results(project_dir)

            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("# Source Engine Evaluation Results", report_text)
            self.assertIn("真实品牌资料只能在 `_private_test_runs/`", report_text)
            self.assertIn("pymupdf4llm baseline 观测", report_text)
            self.assertIn("| S001#page=1 | deck.pptx | MarkItDown / pymupdf4llm baseline | 文字数 20；图片 待复核；图形 待复核；表格 待复核；低置信度：PPTX 轻量路径未保留版式；建议：原 PPT 人工复核 | 待填写 | 待填写 | 待判断 | 否，待证据 |", report_text)
            self.assertIn("| S002#page=3 | report.pdf | MinerU / MarkItDown / pymupdf4llm baseline | 文字数 80；图片 0；图形 0；表格 1；低置信度：表格结构需复核；建议：MinerU / 人工复核 | 待填写 | 待填写 | 待判断 | 否，待证据 |", report_text)
            self.assertNotIn("| 文字覆盖率 | 待记录", report_text)
            self.assertIn("是否调整默认链路", report_text)
            self.assertIn("隐私和外部服务风险", report_text)

    def test_cli_scaffold_source_engine_eval_results_command_writes_results(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "source_engine_eval_plan.md").write_text(
                "# Source Engine Evaluation Plan\n\n| Source Anchor | 原始文件 | 低置信度说明 | 建议动作 | 推荐对比引擎 |\n|---|---|---|---|---|\n| S001#page=1 | sample.html | 多格式输入 | 人工复核 | MarkItDown / pymupdf4llm baseline |\n",
                encoding="utf-8",
            )
            argv = sys.argv
            sys.argv = ["brand-skill", "scaffold-source-engine-eval-results", str(project_dir)]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            report_path = converted / "source_engine_eval_results.md"
            report_text = report_path.read_text(encoding="utf-8")
            self.assertTrue(report_path.exists())
            self.assertIn("Source Engine Evaluation Results", report_text)
            self.assertIn("sample.html", report_text)
            self.assertIn("MarkItDown / pymupdf4llm baseline", report_text)

    def test_plan_mineru_evaluation_selects_high_value_quality_pages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "source_quality_report.md").write_text(
                "\n".join(
                    [
                        "# Source Quality Report",
                        "",
                        "## 需要复核的页面",
                        "",
                        "| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 低置信度说明 | 建议动作 |",
                        "|---|---|---|---|---|---|---|",
                        "| S001#page=1 | sample.pdf | 120 | 0 | 0 | 无明显低置信度 | 继续后续编译 |",
                        "| S001#page=2 | sample.pdf | 8 | 3 | 2 | 可抽取文字较少；含图片/视觉信息 | OCR / MinerU / 人工复核 |",
                        "| S001#page=3 | sample.pdf | 80 | 0 | 0 | 表格结构需复核 | MinerU / 人工复核 |",
                        "| S002#page=1 | deck.pptx | 20 | 待复核 | 待复核 | PPTX 轻量路径未保留版式 | MinerU / 原 PPT 人工复核 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                report_path = plan_mineru_evaluation(project_dir, max_pages=2)

            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("# MinerU Evaluation Plan", report_text)
            self.assertIn("Baseline：pymupdf4llm", report_text)
            self.assertIn("真实品牌资料只能放在 `_private_test_runs/`", report_text)
            self.assertIn("| S001#page=2 | sample.pdf | 可抽取文字较少；含图片/视觉信息 | OCR / MinerU / 人工复核 |", report_text)
            self.assertIn("| S001#page=3 | sample.pdf | 表格结构需复核 | MinerU / 人工复核 |", report_text)
            self.assertNotIn("S002#page=1", report_text)
            self.assertIn("OCR 完整度", report_text)
            self.assertIn("表格还原", report_text)

    def test_cli_plan_mineru_eval_command_writes_evaluation_plan(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 低置信度说明 | 建议动作 |\n|---|---|---|---|---|---|---|\n| S001#page=2 | sample.pdf | 8 | 3 | 2 | 可抽取文字较少 | OCR / MinerU / 人工复核 |\n",
                encoding="utf-8",
            )
            argv = sys.argv
            sys.argv = ["brand-skill", "plan-mineru-eval", str(project_dir), "--max-pages", "1"]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            self.assertTrue((converted / "mineru_eval_plan.md").exists())

    def test_scaffold_mineru_evaluation_results_uses_plan_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "mineru_eval_plan.md").write_text(
                "\n".join(
                    [
                        "# MinerU Evaluation Plan",
                        "",
                        "## 建议对比页面",
                        "",
                        "| Source Anchor | 原始文件 | 低置信度说明 | 建议动作 |",
                        "|---|---|---|---|",
                        "| S001#page=2 | sample.pdf | 可抽取文字较少；含图片/视觉信息 | OCR / MinerU / 人工复核 |",
                        "| S001#page=3 | sample.pdf | 表格结构需复核 | MinerU / 人工复核 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                report_path = scaffold_mineru_evaluation_results(project_dir)

            report_text = report_path.read_text(encoding="utf-8")
            self.assertIn("# MinerU Evaluation Results", report_text)
            self.assertIn("Baseline：pymupdf4llm", report_text)
            self.assertIn("真实品牌资料只能放在 `_private_test_runs/`", report_text)
            self.assertIn("不得把本评估结果写成品牌确认", report_text)
            self.assertIn("| S001#page=2 | sample.pdf | 可抽取文字较少；含图片/视觉信息 | 待填写 | 待填写 | 待填写 | 待判断 |", report_text)
            self.assertIn("| S001#page=3 | sample.pdf | 表格结构需复核 | 待填写 | 待填写 | 待填写 | 待判断 |", report_text)
            self.assertIn("## 接入判断", report_text)
            self.assertIn("| OCR 完整度 | 待判断 | 待填写 | 待定 |", report_text)
            self.assertIn("只有当 MinerU 在关键页明显优于 baseline", report_text)

    def test_scaffold_mineru_evaluation_results_fails_without_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)

            stdout = StringIO()
            with redirect_stdout(stdout):
                with self.assertRaises(SystemExit):
                    scaffold_mineru_evaluation_results(project_dir)

            self.assertIn("Missing MinerU evaluation plan", stdout.getvalue())

    def test_cli_scaffold_mineru_eval_results_command_writes_results_template(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "mineru_eval_plan.md").write_text(
                "# MinerU Evaluation Plan\n\n| Source Anchor | 原始文件 | 低置信度说明 | 建议动作 |\n|---|---|---|---|\n| S001#page=2 | sample.pdf | 可抽取文字较少 | OCR / MinerU / 人工复核 |\n",
                encoding="utf-8",
            )
            argv = sys.argv
            sys.argv = ["brand-skill", "scaffold-mineru-eval-results", str(project_dir)]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            self.assertTrue((converted / "mineru_eval_results.md").exists())

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

    def test_build_value_benchmark_creates_direct_pdf_vs_skill_scorecard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "demo_project"
            converted = project_dir / "converted_markdown"
            facts_dir = converted / "source_facts"
            outputs = project_dir / "outputs"
            review_dir = project_dir / "review"
            facts_dir.mkdir(parents=True)
            outputs.mkdir(parents=True)
            review_dir.mkdir(parents=True)
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n- 总页数：2\n- 需要复核页数：1\n\n| Source Anchor | 原始文件 | 低置信度说明 | 建议动作 |\n|---|---|---|---|\n| S001#page=2 | sample.pdf | 表格结构需复核 | MinerU / 人工复核 |\n",
                encoding="utf-8",
            )
            (converted / "source_version_report.md").write_text(
                "# Source Version Report\n\n- 疑似多版本组数：1\n- 最新修改时间线索：S002 / sample_final.pdf / 2026-01-02\n",
                encoding="utf-8",
            )
            (facts_dir / "S001_source_facts.md").write_text(
                "# Source Facts\n\n| Fact ID | Source Anchor | Fact Candidate | 信息状态 | 低置信度说明 |\n|---|---|---|---|---|\n| SF001-001 | S001#page=1 | 活动目标是提升品牌声量。 | 已从来源资料提取 | 无明显低置信度 |\n",
                encoding="utf-8",
            )
            for filename in ["00_source_index.md", "02_document_profile.md", "03_marketing_semantic_transcript.md", "10_context_asset_index.md", "11_context_library_update_plan.md"]:
                (outputs / filename).write_text(f"# {filename}\n", encoding="utf-8")
            (review_dir / "brand_review.html").write_text("<html>EXCEPTION_REVIEW</html>", encoding="utf-8")
            library_dir = Path(temp_dir) / "brand_context_library"
            library_dir.mkdir()
            (library_dir / "project").mkdir()
            (library_dir / "retrieval_maps").mkdir()
            (library_dir / "project" / "launch-plan.md").write_text("# 上市计划\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text("<html>品牌知识库概览</html>", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text(
                "# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| GEO brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_source_facts.md | converted_markdown/source_transcripts/S001.md |\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                report_path = build_value_benchmark(project_dir, library_dir=library_dir)

            report_text = report_path.read_text(encoding="utf-8")
            answer_record = project_dir / "evaluation" / "ab_answer_record.md"
            answer_text = answer_record.read_text(encoding="utf-8")
            sampling_log = project_dir / "evaluation" / "quality_sampling_log.md"
            sampling_text = sampling_log.read_text(encoding="utf-8")
            self.assertIn("# Direct PDF/PPT vs Skill Benchmark", report_text)
            self.assertIn("直接把原始 PDF/PPT 发给 AI", report_text)
            self.assertIn("先经 Skill 转写、抽 facts、编译、入库后再回答", report_text)
            self.assertIn("这个资料大概讲什么？", report_text)
            self.assertIn("哪些事实来自原文，来源在哪里？", report_text)
            self.assertIn("来源转写质量报告：存在", report_text)
            self.assertIn("事实候选数：1", report_text)
            self.assertIn("结构化输出文件数：5", report_text)
            self.assertIn("知识库报告页：存在", report_text)
            self.assertIn("## 当前可自动验证的 Skill 价值", report_text)
            self.assertIn("页面覆盖证据：source_quality_report.md 记录总页数 2，需要复核页数 1", report_text)
            self.assertIn("来源追溯证据：source_facts 中有 1 条事实候选", report_text)
            self.assertIn("长期沉淀证据：brand_context_library 中有 1 个 Markdown 知识条目", report_text)
            self.assertIn("后续复用证据：retrieval map 中有 1 条读取建议", report_text)
            self.assertIn("## Skill 链路证据路径", report_text)
            self.assertIn("Source Index：outputs/00_source_index.md", report_text)
            self.assertIn("Retrieval Map：brand_context_library/retrieval_maps/source_packages.md", report_text)
            self.assertNotIn(temp_dir, report_text)
            self.assertIn("## 质量抽样候选", report_text)
            self.assertIn("| S001#page=2 | sample.pdf | 表格结构需复核 | MinerU / 人工复核 | 待抽样 |", report_text)
            self.assertIn("## 最小 A/B 执行记录", report_text)
            self.assertTrue(answer_record.exists())
            self.assertIn("A/B 答案记录文件 | evaluation/ab_answer_record.md", report_text)
            self.assertIn("| 最终判断 | 待判断：直接读更好 / Skill 更好 / 差异不明显 |", report_text)
            self.assertIn("| 覆盖率 | 待记录 | 待记录 | 待判断 |", report_text)
            self.assertIn("这份 benchmark 不证明 Skill 一定更好", report_text)
            self.assertIn("## A/B 评估提示词", report_text)
            self.assertIn("### A. 直接读 PDF/PPT 的提示词", report_text)
            self.assertIn("请只基于我上传的原始 PDF/PPT/文档回答", report_text)
            self.assertIn("### B. Skill 链路回答提示词", report_text)
            self.assertIn("请优先基于 source_facts、outputs 和 brand_context_library 回答", report_text)
            self.assertIn("## 答案记录模板", report_text)
            self.assertIn("| 问题 | 直接读 PDF/PPT 答案摘要 | Skill 链路答案摘要 | 差异 | 证据 |", report_text)
            self.assertIn("# A/B Answer Record", answer_text)
            self.assertIn("| 问题 | 直接读原始资料答案摘要 | Structured Wiki 答案摘要 | 胜出方 | 证据 |", answer_text)
            self.assertIn("没有实际跑过就保持 `待粘贴` / `待评分`", answer_text)
            self.assertTrue(sampling_log.exists())
            self.assertIn("# Quality Sampling Log", sampling_text)
            self.assertIn("| 总页数 | 2 |", sampling_text)
            self.assertIn("| 需要复核页数 | 1 |", sampling_text)
            self.assertIn("| 建议最小抽样页数 | 6 |", sampling_text)
            self.assertIn(
                "| QS001 | S001#page=2 | 表格结构需复核 | 待回看原页 | 待抽样 | 人工抽样 / 换引擎小样 |",
                sampling_text,
            )
            self.assertIn("至少人工核对 6 页抽样页面", sampling_text)
            self.assertIn("未完成原页核对前，不得声明 90% 准确率。", sampling_text)

    def test_cli_build_value_benchmark_command_writes_report(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir(parents=True)
            (converted / "source_quality_report.md").write_text("# Source Quality Report\n", encoding="utf-8")
            (converted / "source_version_report.md").write_text("# Source Version Report\n", encoding="utf-8")
            argv = sys.argv
            sys.argv = ["brand-skill", "build-value-benchmark", str(project_dir)]
            try:
                with redirect_stdout(StringIO()):
                    cli_main()
            finally:
                sys.argv = argv

            self.assertTrue((project_dir / "evaluation" / "direct_vs_skill_benchmark.md").exists())
            self.assertTrue((project_dir / "evaluation" / "quality_sampling_log.md").exists())

    def test_value_benchmark_contract_fails_for_empty_quality_sampling_log(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            evaluation_dir = project_dir / "evaluation"
            evaluation_dir.mkdir()
            (evaluation_dir / "direct_vs_skill_benchmark.md").write_text(
                "# Direct PDF/PPT vs Skill Benchmark\n\n固定问题集\n对比评分表\nA/B 评估提示词\n直接读 PDF/PPT 的提示词\nSkill 链路回答提示词\n答案记录模板\nA/B 答案记录文件\nSkill 链路证据路径\nSource Index\nContext Asset Index\nLibrary Update Plan\nRetrieval Map\n覆盖率\n来源追溯\n长期知识沉淀\n",
                encoding="utf-8",
            )
            (evaluation_dir / "ab_answer_record.md").write_text("# A/B Answer Record\n", encoding="utf-8")
            (evaluation_dir / "quality_sampling_log.md").write_text("# Quality Sampling Log\n", encoding="utf-8")

            issues: list[str] = []
            _check_value_benchmark(project_dir, issues)

            self.assertIn("Quality sampling log missing marker: Page Sampling Plan", issues)
            self.assertIn("Quality sampling log missing marker: Pass Rate", issues)
            self.assertIn(
                "Quality sampling log missing marker: 未形成 90% 页面级 / 事实级准确率证据",
                issues,
            )

    def test_build_value_benchmark_uses_stable_external_library_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "project"
            converted = project_dir / "converted_markdown"
            outputs = project_dir / "outputs"
            converted.mkdir(parents=True)
            outputs.mkdir(parents=True)
            (converted / "source_quality_report.md").write_text("# Source Quality Report\n", encoding="utf-8")
            first_library = Path(temp_dir) / "first_temp_library"
            second_library = Path(temp_dir) / "second_temp_library"
            for library_dir in [first_library, second_library]:
                (library_dir / "retrieval_maps").mkdir(parents=True)
                (library_dir / "library_report.html").write_text("<html></html>", encoding="utf-8")
                (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Retrieval\n", encoding="utf-8")

            with redirect_stdout(StringIO()):
                first_report = build_value_benchmark(project_dir, library_dir=first_library).read_text(encoding="utf-8")
                second_report = build_value_benchmark(project_dir, library_dir=second_library).read_text(encoding="utf-8")

            self.assertEqual(first_report, second_report)
            self.assertIn("Library Report：brand_context_library/library_report.html", first_report)
            self.assertIn("Retrieval Map：brand_context_library/retrieval_maps/source_packages.md", first_report)
            self.assertNotIn("first_temp_library", first_report)
            self.assertNotIn("second_temp_library", first_report)

    def test_cli_run_phase1_executes_full_local_loop_from_source(self) -> None:
        import sys

        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "phase1_project"
            source_dir = project_dir / "source" / "meeting"
            source_dir.mkdir(parents=True)
            (source_dir / "sample.md").write_text(
                "# 品牌月会\n\n- 本月重点是渠道复盘。\n- 下月需要补充投放数据。\n",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            argv = sys.argv
            sys.argv = [
                "brand-skill",
                "run-phase1",
                str(project_dir),
                "--library-dir",
                str(library_dir),
            ]
            try:
                with redirect_stdout(StringIO()) as stdout:
                    cli_main()
            finally:
                sys.argv = argv

            output = stdout.getvalue()
            self.assertIn("Phase 1 workflow completed", output)
            self.assertTrue((project_dir / "converted_markdown" / "source_transcripts").exists())
            self.assertTrue((project_dir / "converted_markdown" / "source_facts").exists())
            self.assertTrue((project_dir / "outputs" / "03_marketing_semantic_transcript.md").exists())
            self.assertTrue((project_dir / "review" / "brand_review.html").exists())
            self.assertTrue((library_dir / "library_report.html").exists())
            self.assertTrue((project_dir / "evaluation" / "direct_vs_skill_benchmark.md").exists())
            quality_sampling = (project_dir / "evaluation" / "quality_sampling_log.md").read_text(encoding="utf-8")
            self.assertIn("Page Sampling Plan", quality_sampling)
            self.assertIn("未完成原页核对前，不得声明 90% 准确率", quality_sampling)
            source_index = (project_dir / "outputs" / "00_source_index.md").read_text(encoding="utf-8")
            self.assertIn("内容概述", source_index)
            self.assertIn("本月重点是渠道复盘", source_index)
            retrieval_map = (library_dir / "retrieval_maps" / "source_packages.md").read_text(encoding="utf-8")
            self.assertIn("| 使用场景 | 优先读取 | 精读文件 | 回看原文 |", retrieval_map)
            benchmark = (project_dir / "evaluation" / "direct_vs_skill_benchmark.md").read_text(encoding="utf-8")
            self.assertIn("## Skill 链路证据路径", benchmark)
            self.assertIn("Retrieval Map：brand_context_library/retrieval_maps/source_packages.md", benchmark)
            self.assertIn("Status: passed", (project_dir / "contract_verification_report.md").read_text(encoding="utf-8"))

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
                        "## Page 3",
                        "- Source Anchor：S001#page=3",
                        "- Page Screenshot：../assets/S001/page_03.png",
                        "- Extracted text chars：120",
                        "- Embedded images detected：0",
                        "- Vector drawings detected：0",
                        "",
                        "### Text",
                        "| 渠道 | 预算 | 负责人 |",
                        "|---|---|---|",
                        "| 抖音 | 待补充 | 待确认 |",
                        "",
                        "### Low Confidence / Need Review",
                        "- 无明显低置信度。",
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
            self.assertIn("- 总页数：3", report_text)
            self.assertIn("- 需要复核页数：2", report_text)
            self.assertIn("## 全部页面读取状态", report_text)
            self.assertIn("| S001#page=1 | sample.pdf | 120 | 0 | 0 | 0 | 可进入后续编译 | 无明显低置信度。 |", report_text)
            self.assertIn("| S001#page=2 | sample.pdf | 8 | 3 | 2 | 0 | 需要复核 | 可抽取文字较少；含图片/视觉信息 |", report_text)
            self.assertIn("| S001#page=2 | sample.pdf | 8 | 3 | 2 | 0 | 可抽取文字较少；含图片/视觉信息 | OCR / MinerU / 人工复核 |", report_text)
            self.assertIn("| S001#page=3 | sample.pdf | 120 | 0 | 0 | 1 | 无明显低置信度。 | MinerU / MarkItDown / 人工复核 |", report_text)
            self.assertIn("优先处理含图片、低文字量、表格、小字或 OCR 不确定页面", report_text)

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
                        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 | 外部来源 |",
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
                        "| S001 | category_plan_final0729_a1b2c3d4.pdf | 2026-07-29T09:00:00+08:00 | 2026-07-29T18:00:00+08:00 | 2026-07-29T18:30:00+08:00 | source_transcripts/S001.md | pymupdf4llm | PDF | no | pages 1-20 | 待复核 | 截图 | 待复核 | 无明显低置信度 | 否 | ima / 示例库 |",
                        "| S002 | category plan final 0801 copy.pdf | 2026-08-01T09:00:00+08:00 | 2026-08-01T18:00:00+08:00 | 2026-08-01T18:30:00+08:00 | source_transcripts/S002.md | pymupdf4llm | PDF | no | pages 1-22 | 待复核 | 截图 | 待复核 | 无明显低置信度 | 否 | ima / 示例库 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_source_version_report(project_dir)

            report_text = (converted / "source_version_report.md").read_text(encoding="utf-8")
            self.assertIn("疑似多版本组数：1", report_text)
            self.assertIn("### category_plan", report_text)
            self.assertIn("S002 / category plan final 0801 copy.pdf / 2026-08-01T18:00:00+08:00", report_text)
            self.assertIn("category_plan_final0729_a1b2c3d4.pdf", report_text)

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
            source_index = (outputs / "00_source_index.md").read_text(encoding="utf-8")
            self.assertIn("campaign.md", source_index)
            self.assertIn("内容概述", source_index)
            self.assertIn("品牌希望建立城市清爽的活动联想", source_index)
            self.assertIn("converted_markdown/source_facts/S001_source_facts.md", source_index)
            self.assertIn("品牌希望建立城市清爽", (outputs / "03_marketing_semantic_transcript.md").read_text(encoding="utf-8"))
            self.assertIn("SF001-001", (outputs / "04_key_facts_and_claims.md").read_text(encoding="utf-8"))
            self.assertIn("S001#page=2", (outputs / "06_risk_and_review_items.md").read_text(encoding="utf-8"))
            self.assertIn("CA001", (outputs / "10_context_asset_index.md").read_text(encoding="utf-8"))
            plan = (outputs / "11_context_library_update_plan.md").read_text(encoding="utf-8")
            self.assertIn("LCE001", plan)
            self.assertIn("| 使用场景 | 优先读取 | 精读文件 | 回看原文 |", plan)
            self.assertIn("outputs/10_context_asset_index.md", plan)

    def test_compile_structured_outputs_collapses_source_index_by_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            facts = converted / "source_facts"
            facts.mkdir(parents=True)
            (converted / "conversion_report.md").write_text(
                "\n".join(
                    [
                        "# Source Conversion Report",
                        "",
                        "## Source Files",
                        "",
                        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 | 外部来源 |",
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
                        "| S001 | deck.pdf | 2026-01-01T09:00:00+08:00 | 2026-01-02T09:00:00+08:00 | converted_markdown/source_transcripts/S001_deck.md | pymupdf4llm | 文本解析 | 否 | 1 | 待复核 | 是 | 待复核 | 含图片 | 人工复核 | 本地 source/ |",
                        "| S001 | deck.pdf | 2026-01-01T09:00:00+08:00 | 2026-01-02T09:00:00+08:00 | converted_markdown/source_transcripts/S001_deck.md | pymupdf4llm | 文本解析 | 否 | 2 | 待复核 | 是 | 待复核 | 含图片 | 人工复核 | 本地 source/ |",
                        "| S002 | training.pdf | 2026-01-03T09:00:00+08:00 | 2026-01-04T09:00:00+08:00 | converted_markdown/source_transcripts/S002_training.md | pymupdf4llm | 文本解析 | 否 | 1 | 待复核 | 是 | 待复核 | 含图片 | 人工复核 | 本地 source/ |",
                    ]
                ),
                encoding="utf-8",
            )
            (facts / "S001_deck_source_facts.md").write_text(
                "\n".join(
                    [
                        "# Source Facts",
                        "",
                        "| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |",
                        "|---|---|---|---|---|",
                        "| SF001-001 | S001#page=1 | -----START OF PICTURE----- | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-002 | S001#page=2 | 品牌会议资料提出渠道复盘和后续动作。 | 已从来源资料提取 | 无明显低置信度。 |",
                    ]
                ),
                encoding="utf-8",
            )
            (facts / "S002_training_source_facts.md").write_text(
                "# Source Facts\n\n| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |\n|---|---|---|---|---|\n| SF002-001 | S002#page=1 | 产品培训资料说明核心卖点。 | 已从来源资料提取 | 无明显低置信度。 |\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                compile_structured_outputs(project_dir)

            source_index = (project_dir / "outputs" / "00_source_index.md").read_text(encoding="utf-8")
            plan = (project_dir / "outputs" / "11_context_library_update_plan.md").read_text(encoding="utf-8")
            self.assertEqual(source_index.count("| S001 | deck.pdf |"), 1)
            self.assertEqual(source_index.count("| S002 | training.pdf |"), 1)
            self.assertIn("| S001 | deck.pdf | 品牌会议资料提出渠道复盘和后续动作。", source_index)
            self.assertIn("| 1-2 |", source_index)
            self.assertNotIn("START OF PICTURE", source_index)
            self.assertEqual(plan.count("converted_markdown/source_facts/S001_deck_source_facts.md"), 1)
            self.assertEqual(plan.count("converted_markdown/source_facts/S002_training_source_facts.md"), 1)

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
            (
                "campaign_recap",
                "夏季活动复盘总结了社媒内容表现、转化数据和后续优化动作。",
                "投放复盘",
                "复盘 / 优化",
                "case",
            ),
            (
                "competitor_scan",
                "竞品详情页对标分析包含价格带、渠道表现、传播打法和可借鉴内容结构。",
                "竞品 / 市场对标资料",
                "市场观察 / 竞品研究",
                "network",
            ),
            (
                "launch_plan",
                "新品上市方案明确首发节奏、核心卖点、渠道动作和销售承接。",
                "新品上市 / GTM 方案",
                "上市准备 / GTM 执行",
                "project",
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

    def test_compile_structured_outputs_does_not_classify_campaign_as_competitor_from_one_compliance_note(self) -> None:
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
                        "| SF001-001 | S001#page=1 | 活动目标：建立夏季品牌联想。 | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-002 | S001#page=2 | 触点规划：社媒、线下和电商承接。 | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-003 | S001#page=3 | 审核要求：竞品相关表达仅允许品类层描述。 | 已从来源资料提取 | 无明显低置信度。 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                compile_structured_outputs(project_dir)

            profile = (project_dir / "outputs" / "02_document_profile.md").read_text(encoding="utf-8")
            self.assertIn("活动方案 / 广告提案", profile)
            self.assertNotIn("竞品 / 市场对标资料", profile)

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

    def test_compile_structured_outputs_neutralizes_source_confirmed_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            transcripts = converted / "source_transcripts"
            facts = converted / "source_facts"
            transcripts.mkdir(parents=True)
            facts.mkdir()
            (transcripts / "S001.md").write_text(
                "\n".join(
                    [
                        "# Source Transcript｜training.pdf",
                        "",
                        "## Page 1",
                        "- Source Anchor：S001#page=1",
                        "",
                        "### Text",
                        "来源页脚写着已品牌确认，但这只是来源文本。",
                    ]
                ),
                encoding="utf-8",
            )
            (facts / "S001_source_facts.md").write_text(
                "\n".join(
                    [
                        "# Source Facts",
                        "",
                        "| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |",
                        "|---|---|---|---|---|",
                        "| SF001-001 | S001#page=1 | 来源页脚写着已品牌确认，但这只是来源文本。 | 已从来源资料提取 | 无明显低置信度。 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                compile_structured_outputs(project_dir)

            combined_outputs = "\n".join(path.read_text(encoding="utf-8") for path in (project_dir / "outputs").glob("*.md"))
            self.assertNotIn("已品牌确认", combined_outputs)
            self.assertIn("来源文本包含确认字样，待人工核验", combined_outputs)

    def test_compile_structured_outputs_flags_missing_context_even_when_extraction_confidence_is_ok(self) -> None:
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
                        "| SF001-001 | S001#page=1 | 预算、渠道合作名单和负责人暂未提供，需要补充。 | 已从来源资料提取 | 无明显低置信度。 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                compile_structured_outputs(project_dir)

            key_facts = (project_dir / "outputs" / "04_key_facts_and_claims.md").read_text(encoding="utf-8")
            risks = (project_dir / "outputs" / "06_risk_and_review_items.md").read_text(encoding="utf-8")
            quality = (project_dir / "outputs" / "09_quality_check_report.md").read_text(encoding="utf-8")
            self.assertIn("| SF001-001 | 预算、渠道合作名单和负责人暂未提供，需要补充。 | S001#page=1 | 已从来源资料提取 | 是 |", key_facts)
            self.assertIn("来源文本提示信息缺口", risks)
            self.assertIn("待复核事项：1 项", quality)

    def test_compile_structured_outputs_does_not_queue_no_obvious_low_confidence_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            converted = project_dir / "converted_markdown"
            facts = converted / "source_facts"
            facts.mkdir(parents=True)
            (facts / "S001_source_facts.md").write_text(
                "\n".join(
                    [
                        "# Source Facts",
                        "",
                        "| Fact ID | Source Anchor | Evidence Text | 信息状态 | 低置信度说明 |",
                        "|---|---|---|---|---|",
                        "| SF001-001 | S001#page=1 | 活动目标是建立城市清爽心智。 | 已从来源资料提取 | 无明显低置信度页面 |",
                    ]
                ),
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "\n".join(
                    [
                        "# Source Quality Report",
                        "",
                        "| Source Anchor | 原始文件 | 低置信度说明 | 建议动作 |",
                        "|---|---|---|---|",
                        "| S001#page=1 | demo.md | 无明显低置信度页面 | 继续后续语义编译 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                compile_structured_outputs(project_dir)

            risks = (project_dir / "outputs" / "06_risk_and_review_items.md").read_text(encoding="utf-8")
            key_facts = (project_dir / "outputs" / "04_key_facts_and_claims.md").read_text(encoding="utf-8")
            self.assertIn("| SF001-001 | 活动目标是建立城市清爽心智。 | S001#page=1 | 已从来源资料提取 | 否 |", key_facts)
            self.assertNotIn("无明显低置信度页面 | 中", risks)
            self.assertIn("暂无明显风险", risks)

    def test_compile_structured_outputs_does_not_promote_pdf_artifacts_to_library(self) -> None:
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
                        "| SF001-001 | S001#page=1 | -----START OF PICTURE----- | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-002 | S001#page=1 | _private_test_runs/private_brand_bpm_sample/source/brand_strategy/demo.pdf | 已从来源资料提取 | 无明显低置信度。 |",
                        "| SF001-003 | S001#page=2 | 品牌年度会议资料提出渠道复盘和下一步动作。 | 已从来源资料提取 | 无明显低置信度。 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                compile_structured_outputs(project_dir)

            assets = (project_dir / "outputs" / "10_context_asset_index.md").read_text(encoding="utf-8")
            plan = (project_dir / "outputs" / "11_context_library_update_plan.md").read_text(encoding="utf-8")
            self.assertIn("品牌年度会议资料提出渠道复盘", assets)
            self.assertIn("品牌年度会议资料提出渠道复盘", plan)
            self.assertNotIn("START OF PICTURE", assets)
            self.assertNotIn("_private_test_runs", assets)
            self.assertNotIn("START OF PICTURE", plan)
            self.assertNotIn("_private_test_runs", plan)

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
            converted = project_dir / "converted_markdown"
            converted.mkdir()
            (converted / "conversion_report.md").write_text(
                "\n".join(
                    [
                        "# Source Conversion Report",
                        "",
                        "## Source Files",
                        "",
                        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 | 外部来源 |",
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
                        "| S001 | campaign.pdf | 2026-01-01T00:00:00Z | 2026-01-02T00:00:00Z | 2026-01-03T00:00:00Z | converted_markdown/source_transcripts/S001_campaign.md | pymupdf4llm | PDF 文本解析 | 否 | 1-18 | 中 | 部分 | 部分 | 第 9 页小字需复核 | 是 | 本地 source/ |",
                    ]
                ),
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "\n".join(
                    [
                        "# Source Quality Report",
                        "",
                        "## 识别质量总览",
                        "",
                        "- 总页数：18",
                        "- 需要复核页数：1",
                        "",
                        "## 需要复核的页面",
                        "",
                        "| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 |",
                        "|---|---|---|---|---|---|---|---|",
                        "| S001#page=9 | campaign.pdf | 30 | 1 | 0 | 0 | 第 9 页小字没有读清楚 | 重新提供截图或启用 OCR |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_review_pack(project_dir)

            html = project_dir / "review" / "brand_review.html"
            text = html.read_text(encoding="utf-8")
            self.assertTrue(html.exists())
            self.assertIn("内容读取报告", text)
            self.assertIn("读取覆盖状态", text)
            self.assertIn("总页数：18", text)
            self.assertIn("campaign.pdf", text)
            self.assertIn("1-18", text)
            self.assertIn("converted_markdown/source_facts/S001_campaign_source_facts.md", text)
            self.assertIn("重新提供截图或启用 OCR", text)
            self.assertIn("整个文件概述", text)
            self.assertIn("需要处理的问题", text)
            self.assertIn("文件大纲参考", text)
            self.assertIn("人工修正", text)
            self.assertIn("待处理问题", text)
            self.assertIn("导出修正意见", text)
            self.assertNotIn("确认意见", text)
            self.assertNotIn("review-controls", text)
            self.assertNotIn("setDecision", text)
            self.assertNotIn('class="source-anchor"', text)
            self.assertNotIn("来源位置：", text)
            self.assertNotIn("Context Asset Index Review", text)

    def test_build_review_pack_collapses_multi_page_source_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            self._write_minimum_marketing_outputs(project_dir)
            converted = project_dir / "converted_markdown"
            converted.mkdir()
            (converted / "conversion_report.md").write_text(
                "\n".join(
                    [
                        "# Source Conversion Report",
                        "",
                        "## Source Files",
                        "",
                        "| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 | 外部来源 |",
                        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
                        "| S001 | deck.pdf | 2026-01-01T00:00:00Z | 2026-01-02T00:00:00Z | 2026-01-03T00:00:00Z | converted_markdown/source_transcripts/S001_deck.md | pymupdf4llm | PDF 文本解析 | 否 | 1 | 中 | 部分 | 部分 | 小字需复核 | 是 | 本地 source/ |",
                        "| S001 | deck.pdf | 2026-01-01T00:00:00Z | 2026-01-02T00:00:00Z | 2026-01-03T00:00:00Z | converted_markdown/source_transcripts/S001_deck.md | pymupdf4llm | PDF 文本解析 | 否 | 2 | 中 | 部分 | 部分 | 小字需复核 | 是 | 本地 source/ |",
                        "| S002 | training.pdf | 2026-01-01T00:00:00Z | 2026-01-02T00:00:00Z | 2026-01-03T00:00:00Z | converted_markdown/source_transcripts/S002_training.md | pymupdf4llm | PDF 文本解析 | 否 | 1 | 中 | 部分 | 部分 | 图片需复核 | 是 | 本地 source/ |",
                    ]
                ),
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "\n".join(
                    [
                        "# Source Quality Report",
                        "",
                        "## 识别质量总览",
                        "",
                        "- 总页数：3",
                        "- 需要复核页数：3",
                        "",
                        "## 需要复核的页面",
                        "",
                        "| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 |",
                        "|---|---|---|---|---|---|---|---|",
                        "| S001#page=1 | deck.pdf | 30 | 1 | 0 | 0 | 小字没有读清楚 | 重新提供截图或启用 OCR |",
                        "| S001#page=2 | deck.pdf | 20 | 1 | 0 | 0 | 小字没有读清楚 | 重新提供截图或启用 OCR |",
                        "| S002#page=1 | training.pdf | 10 | 2 | 0 | 0 | 图片中文字需要复核 | MinerU / MarkItDown / 人工复核 |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_review_pack(project_dir)

            text = (project_dir / "review" / "brand_review.html").read_text(encoding="utf-8")
            self.assertIn("读取覆盖状态：读了哪些文件、每份大概讲什么", text)
            self.assertIn("文件大纲参考：识别出来的索引大纲", text)
            self.assertIn("需要处理的问题：哪些内容没读清", text)
            self.assertEqual(text.count("converted_markdown/source_facts/S001_deck_source_facts.md"), 1)
            self.assertEqual(text.count("converted_markdown/source_facts/S002_training_source_facts.md"), 1)
            self.assertIn("deck.pdf：2 页需要复核，页码 1-2", text)
            self.assertIn("training.pdf：1 页需要复核，页码 1", text)

    def test_build_review_pack_shows_missing_context_without_backend_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            outputs = project_dir / "outputs"
            outputs.mkdir()
            files = {
                "02_document_profile.md": "# Document Profile｜示例活动\n\n## 1. 文件定位\n\n这是一份活动方案资料。\n",
                "03_marketing_semantic_transcript.md": "# Marketing Semantic Transcript｜示例活动\n\n## Page / Slide 1\n\n### 原页核心内容转述\n\n## Slide 1｜活动背景\n\n建立夏季品牌联想。\n\n## Page / Slide 2\n\n### 原页核心内容转述\n\n## Slide 2｜目标人群\n\n资料没有提供定量消费者调研，需要品牌经理补充。\n",
                "06_risk_and_review_items.md": "# Risk and Review Items\n\n| Review ID | 审核项 | 风险等级 | 来源锚点 | 建议 |\n|---|---|---|---|---|\n| R001 | 来源文本提示信息缺口：Slide 2｜目标人群：资料没有提供定量消费者调研，需要品牌经理补充。 | 中 | S001#page=2 | 人工复核 / 补充业务信息 |\n| R002 | 来源文本提示信息缺口：Slide 3｜审核要求：预算、人员分工、渠道合作名单暂未提供。 | 中 | S001#page=3 | 人工复核 / 补充业务信息 |\n",
            }
            for filename, text in files.items():
                (outputs / filename).write_text(text, encoding="utf-8")

            with redirect_stdout(StringIO()):
                build_review_pack(project_dir)

            text = (project_dir / "review" / "brand_review.html").read_text(encoding="utf-8")
            self.assertIn("需要人工处理", text)
            self.assertIn("待处理问题：2", text)
            self.assertIn("资料没有提供定量消费者调研", text)
            self.assertIn("预算、人员分工、渠道合作名单暂未提供", text)
            self.assertIn("活动背景", text)
            self.assertNotIn("Review ID", text)
            self.assertNotIn("来源锚点", text)
            self.assertNotIn("风险等级", text)
            self.assertNotIn("Source Anchor", text)
            self.assertNotIn("Risk Level", text)
            self.assertNotIn('class="source-anchor"', text)
            self.assertNotIn("review-controls", text)

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

    def test_apply_context_library_update_skips_identical_reimport(self) -> None:
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
            with redirect_stdout(StringIO()) as stdout:
                apply_context_library_update(project_dir, library_dir=library_dir)

            self.assertIn("Entries applied: 0", stdout.getvalue())
            self.assertIn("Entries skipped: 1", stdout.getvalue())
            self.assertIn("Conflicts queued: 0", stdout.getvalue())
            index_text = (library_dir / "00_library_index.md").read_text(encoding="utf-8")
            self.assertIn("Conflicts: 0", index_text)
            self.assertIn("Existing Updates: 1", index_text)
            self.assertIn("Do Not Promote Records: 1", index_text)
            self.assertIn("Retrieval Note Batches: 1", index_text)
            self.assertEqual(len(list((library_dir / "brand").glob("*.md"))), 1)
            self.assertEqual((library_dir / "evolution_log.md").read_text(encoding="utf-8").count("demo_project"), 1)

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
            self.assertIn("知识库地图", text)
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

    def test_build_library_report_turns_retrieval_map_into_agent_reading_advice(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            library_dir = Path(temp_dir) / "brand_context_library"
            (library_dir / "project").mkdir(parents=True)
            (library_dir / "review_queue").mkdir()
            (library_dir / "retrieval_maps").mkdir()
            (library_dir / "project" / "launch-plan.md").write_text("# 上市计划\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text(
                "\n".join(
                    [
                        "# Source Package Retrieval Notes",
                        "",
                        "| 使用场景 | 优先读取 | 精读文件 | 回看原文 |",
                        "|---|---|---|---|",
                        "| GEO / PDP / 种草 brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_source_facts.md | converted_markdown/source_transcripts/S001.md |",
                        "| 销售 / 复盘 brief | outputs/07_ai_ready_marketing_brief_base.md | outputs/05_strategy_and_execution_map.md | converted_markdown/source_transcripts/S002.md |",
                    ]
                ),
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()):
                build_library_report(library_dir)

            text = (library_dir / "library_report.html").read_text(encoding="utf-8")
            self.assertIn("做 GEO / PDP / 种草 / 拍摄 / 销售 / 复盘等任务时", text)
            self.assertIn("使用场景：GEO / PDP / 种草 brief", text)
            self.assertIn("优先读取：outputs/10_context_asset_index.md", text)
            self.assertIn("精读文件：converted_markdown/source_facts/S001_source_facts.md", text)
            self.assertIn("回看原文：converted_markdown/source_transcripts/S001.md", text)
            self.assertIn("按任务找资料", text)
            self.assertIn("<strong>GEO</strong>先读 outputs/10_context_asset_index.md", text)
            self.assertIn("<strong>PDP</strong>先读 outputs/10_context_asset_index.md", text)
            self.assertIn("<strong>种草</strong>先读 outputs/10_context_asset_index.md", text)
            self.assertIn("<strong>销售</strong>先读 outputs/07_ai_ready_marketing_brief_base.md", text)
            self.assertIn("<strong>复盘</strong>先读 outputs/07_ai_ready_marketing_brief_base.md", text)

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
            self.assertIn("建议动作：版本复核", text)
            self.assertIn("最新修改时间线索：S002 / summer_strategy_v2.pdf / 2026-03-08T18:30:00+08:00", text)
            self.assertNotIn("source_version_report.md", text)
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
            files = {
                "00_source_index.md": "# Source Index\n\n| Source ID | 文件名 | 内容概述 | 转写 Markdown | Source Facts |\n|---|---|---|---|---|\n| S001 | demo.pdf | 活动方案提出提升品牌声量 | converted_markdown/source_transcripts/S001_demo.md | converted_markdown/source_facts/S001_demo_source_facts.md |\n",
                "02_document_profile.md": "# Document Profile\n\n| 字段 | 内容 | 信息状态 | 待确认 |\n|---|---|---|---|\n| 文件类型 | 活动方案 | AI 结构化转述，待确认 | 是 |\n| 文件目的 | 对齐传播策略 | AI 结构化转述，待确认 | 是 |\n",
                "03_marketing_semantic_transcript.md": "# Marketing Semantic Transcript\n\n## Page / Slide 1\n\n- Source Anchor：S001#page=1\n\n### 原页核心内容转述\n\n活动方案提出提升品牌声量。\n",
                "04_key_facts_and_claims.md": "# Key Facts\n\n| Fact ID | 事实 | 信息状态 | 待确认 |\n|---|---|---|---|\n| SF001 | 活动目标为提升品牌声量 | 已从来源资料提取 | 否 |\n",
                "05_strategy_and_execution_map.md": "# Strategy and Execution Map\n\n## 自动识别的大纲\n\n- 活动目标\n",
                "06_risk_and_review_items.md": "# Risk and Review Items\n\n| Review ID | 审核项 | 建议 |\n|---|---|---|\n| R000 | 暂无明显风险 | 继续后续编译 |\n",
                "10_context_asset_index.md": "# Context Asset Index\n\n| Asset ID | 可复用资产 | 适用场景 | 信息状态 |\n|---|---|---|---|\n| CA001 | 活动目标为提升品牌声量 | Campaign brief | 已从来源资料提取 |\n",
                "11_context_library_update_plan.md": "# Context Library Update Plan\n\n## 2. New Context Entries\n\n| Entry ID | 标题 |\n|---|---|\n| LCE001 | 活动目标 |\n\n## 4. Do Not Promote\n\n- 不提升待确认内容。\n\n## 6. Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n",
            }
            for filename, content in files.items():
                (outputs / filename).write_text(content, encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "# Source Conversion Report\n\n## 识别质量摘要\n\n- 总页数：1\n- 视觉/表格/小字限制：复杂版式需复核。\n- 人工复核建议：检查低置信度区域。\n\n| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n## 识别质量总览\n\n- 总页数：1\n- 需要复核页数：0\n- 复核原则：优先处理含图片、低文字量、表格、小字或 OCR 不确定页面；关键品牌口径和关键数字必须回到原始页面确认。\n\n## 全部页面读取状态\n\n| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 读取状态 | 低置信度说明 |\n|---|---|---|---|---|---|---|---|\n| S001#page=1 | demo.pdf | 120 | 0 | 0 | 0 | 可进入后续编译 | 无明显低置信度 |\n\n## 需要复核的页面\n\n| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 |\n|---|---|---|---|---|---|---|---|\n| - | - | - | - | - | - | 无明显低置信度页面 | 继续后续语义编译 |\n",
                encoding="utf-8",
            )
            (converted / "source_version_report.md").write_text(
                "# Source Version Report\n\n## 版本线索总览\n\n- 疑似多版本组数：0\n- 最新修改时间线索：不自动覆盖已有品牌知识。\n",
                encoding="utf-8",
            )
            self._write_source_engine_reports(project_dir)
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            review_dir = project_dir / "review"
            review_dir.mkdir()
            (review_dir / "brand_review.html").write_text(
                "内容读取报告 读取覆盖状态 整个文件概述 需要处理的问题 文件大纲参考 自动通过，无需人工处理",
                encoding="utf-8",
            )
            evaluation_dir = project_dir / "evaluation"
            evaluation_dir.mkdir()
            (evaluation_dir / "direct_vs_skill_benchmark.md").write_text(
                "# Direct PDF/PPT vs Skill Benchmark\n\n## 固定问题集\n\n## 对比评分表\n\n## A/B 评估提示词\n\n### A. 直接读 PDF/PPT 的提示词\n\n### B. Skill 链路回答提示词\n\n## 答案记录模板\n\nA/B 答案记录文件：evaluation/ab_answer_record.md\n\n## Skill 链路证据路径\n\n- Source Index：outputs/00_source_index.md\n- Context Asset Index：outputs/10_context_asset_index.md\n- Library Update Plan：outputs/11_context_library_update_plan.md\n- Retrieval Map：brand_context_library/retrieval_maps/source_packages.md\n\n覆盖率 来源追溯 长期知识沉淀\n",
                encoding="utf-8",
            )
            (evaluation_dir / "ab_answer_record.md").write_text("# A/B Answer Record\n", encoding="utf-8")
            (evaluation_dir / "quality_sampling_log.md").write_text(self._quality_sampling_log_text(), encoding="utf-8")
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n", encoding="utf-8")
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
            files = {
                "00_source_index.md": "# Source Index\n\n| Source ID | 文件名 | 内容概述 | 转写 Markdown | Source Facts |\n|---|---|---|---|---|\n| S001 | demo.pdf | 活动方案提出提升品牌声量 | converted_markdown/source_transcripts/S001_demo.md | converted_markdown/source_facts/S001_demo_source_facts.md |\n",
                "02_document_profile.md": "# Document Profile\n\n| 字段 | 内容 | 信息状态 | 待确认 |\n|---|---|---|---|\n| 文件类型 | 活动方案 | AI 结构化转述，待确认 | 是 |\n| 文件目的 | 对齐传播策略 | AI 结构化转述，待确认 | 是 |\n",
                "03_marketing_semantic_transcript.md": "# Marketing Semantic Transcript\n\n## Page / Slide 1\n\n- Source Anchor：S001#page=1\n\n### 原页核心内容转述\n\n活动方案提出提升品牌声量。\n",
                "04_key_facts_and_claims.md": "# Key Facts\n\n| Fact ID | 事实 | 信息状态 | 待确认 |\n|---|---|---|---|\n| SF001 | 活动目标为提升品牌声量 | 已从来源资料提取 | 否 |\n",
                "05_strategy_and_execution_map.md": "# Strategy and Execution Map\n\n## 自动识别的大纲\n\n- 活动目标\n",
                "06_risk_and_review_items.md": "# Risk and Review Items\n\n| Review ID | 审核项 | 建议 |\n|---|---|---|\n| R000 | 暂无明显风险 | 继续后续编译 |\n",
                "10_context_asset_index.md": "# Context Asset Index\n\n| Asset ID | 可复用资产 | 适用场景 | 信息状态 |\n|---|---|---|---|\n| CA001 | 活动目标为提升品牌声量 | Campaign brief | 已从来源资料提取 |\n",
                "11_context_library_update_plan.md": "# Context Library Update Plan\n\n## 2. New Context Entries\n\n| Entry ID | 标题 |\n|---|---|\n| LCE001 | 活动目标 |\n\n## 4. Do Not Promote\n\n- 不提升待确认内容。\n\n## 6. Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n",
            }
            for filename, content in files.items():
                (outputs / filename).write_text(content, encoding="utf-8")
            (converted / "conversion_report.md").write_text(
                "# Source Conversion Report\n\n## 识别质量摘要\n\n- 总页数：1\n- 视觉/表格/小字限制：复杂版式需复核。\n- 人工复核建议：检查低置信度区域。\n\n| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n## 识别质量总览\n\n- 总页数：1\n- 需要复核页数：0\n- 复核原则：优先处理含图片、低文字量、表格、小字或 OCR 不确定页面；关键品牌口径和关键数字必须回到原始页面确认。\n\n## 全部页面读取状态\n\n| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 读取状态 | 低置信度说明 |\n|---|---|---|---|---|---|---|---|\n| S001#page=1 | demo.pdf | 120 | 0 | 0 | 0 | 可进入后续编译 | 无明显低置信度 |\n\n## 需要复核的页面\n\n| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 |\n|---|---|---|---|---|---|---|---|\n| - | - | - | - | - | - | 无明显低置信度页面 | 继续后续语义编译 |\n",
                encoding="utf-8",
            )
            (converted / "source_version_report.md").write_text(
                "# Source Version Report\n\n## 版本线索总览\n\n- 疑似多版本组数：0\n- 最新修改时间线索：不自动覆盖已有品牌知识。\n",
                encoding="utf-8",
            )
            self._write_source_engine_reports(project_dir)
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            review_dir = project_dir / "review"
            review_dir.mkdir()
            (review_dir / "brand_review.html").write_text(
                "内容读取报告 读取覆盖状态 整个文件概述 需要处理的问题 文件大纲参考",
                encoding="utf-8",
            )
            evaluation_dir = project_dir / "evaluation"
            evaluation_dir.mkdir()
            (evaluation_dir / "direct_vs_skill_benchmark.md").write_text(
                "# Direct PDF/PPT vs Skill Benchmark\n\n## 固定问题集\n\n## 对比评分表\n\n## A/B 评估提示词\n\n### A. 直接读 PDF/PPT 的提示词\n\n### B. Skill 链路回答提示词\n\n## 答案记录模板\n\nA/B 答案记录文件：evaluation/ab_answer_record.md\n\n## Skill 链路证据路径\n\n- Source Index：outputs/00_source_index.md\n- Context Asset Index：outputs/10_context_asset_index.md\n- Library Update Plan：outputs/11_context_library_update_plan.md\n- Retrieval Map：brand_context_library/retrieval_maps/source_packages.md\n\n覆盖率 来源追溯 长期知识沉淀\n",
                encoding="utf-8",
            )
            (evaluation_dir / "ab_answer_record.md").write_text("# A/B Answer Record\n", encoding="utf-8")
            (evaluation_dir / "quality_sampling_log.md").write_text(self._quality_sampling_log_text(), encoding="utf-8")
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n", encoding="utf-8")
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

    def test_verify_project_contract_fails_without_source_engine_evidence(self) -> None:
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
                "# Source Conversion Report\n\n## 识别质量摘要\n\n- 总页数：1\n- 视觉/表格/小字限制：复杂版式需复核。\n- 人工复核建议：检查低置信度区域。\n\n| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n## 识别质量总览\n\n- 总页数：1\n- 需要复核页数：0\n- 复核原则：优先处理含图片、低文字量、表格、小字或 OCR 不确定页面；关键品牌口径和关键数字必须回到原始页面确认。\n\n| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 |\n|---|---|---|---|---|---|---|---|\n| - | - | - | - | - | - | 无明显低置信度页面 | 继续后续语义编译 |\n",
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

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=Path(temp_dir) / "missing_library")

            output = stdout.getvalue()
            self.assertIn("Missing source engine readiness report", output)
            self.assertIn("Missing source engine evaluation plan", output)
            self.assertIn("Missing source engine evaluation results", output)

    def test_verify_project_contract_fails_without_skill_entrypoint_when_repo_is_known(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "repo"
            project_dir = repo_dir / "demo_project"
            repo_dir.mkdir()
            project_dir.mkdir()

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(
                        project_dir,
                        library_dir=repo_dir / "missing_library",
                        repo_dir=repo_dir,
                    )

            output = stdout.getvalue()
            self.assertIn("Missing skill package entrypoint: SKILL.md", output)

    def test_verify_project_contract_accepts_current_skill_entrypoint(self) -> None:
        repo_dir = Path(__file__).resolve().parents[1]
        skill_text = (repo_dir / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: brand-business-context-compiler", skill_text)
        self.assertIn("brand-skill run-phase1", skill_text)
        self.assertIn("source_engine_eval_results.md", skill_text)
        self.assertIn("_private_test_runs/", skill_text)

    def test_verify_project_contract_fails_without_prompt_schema_package_when_repo_is_known(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir) / "repo"
            project_dir = repo_dir / "demo_project"
            repo_dir.mkdir()
            project_dir.mkdir()
            (repo_dir / "SKILL.md").write_text(
                "---\nname: brand-business-context-compiler\ndescription: Use when testing.\n---\n"
                "brand-skill run-phase1\nSource Conversion Engines\nsource_engine_eval_results.md\n"
                "review/brand_review.html\nlibrary_report.html\n_private_test_runs/\nDo not\n",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(
                        project_dir,
                        library_dir=repo_dir / "missing_library",
                        repo_dir=repo_dir,
                    )

            output = stdout.getvalue()
            self.assertIn("Missing prompt package bundle: prompt_bundle.md", output)
            self.assertIn("Missing required Phase 1 prompt", output)
            self.assertIn("Missing required core schema", output)

    def test_verify_project_contract_accepts_current_prompt_schema_package(self) -> None:
        repo_dir = Path(__file__).resolve().parents[1]

        self.assertTrue((repo_dir / "prompt_bundle.md").exists())
        self.assertTrue((repo_dir / "prompts" / "00_source_to_markdown_conversion.md").exists())
        self.assertTrue((repo_dir / "prompts" / "09_generate_context_library_update_plan.md").exists())
        self.assertTrue((repo_dir / "schemas" / "source_conversion_report.schema.md").exists())
        self.assertTrue((repo_dir / "schemas" / "context_library_update_plan.schema.md").exists())

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
            self.assertIn("Review pack created", output)
            self.assertIn("Context library updated", output)
            self.assertIn("Library report generated", output)
            self.assertIn("Contract verification passed", output)
            self.assertTrue((library_dir / "library_report.html").exists())
            self.assertTrue((project_dir / "evaluation" / "direct_vs_skill_benchmark.md").exists())
            source_index = (project_dir / "outputs" / "00_source_index.md").read_text(encoding="utf-8")
            self.assertIn("转写 Markdown", source_index)
            self.assertIn("Source Facts", source_index)
            self.assertIn("converted_markdown/source_facts/S001_campaign_plan_source_facts.md", source_index)
            self.assertIn("Status: passed", report_path.read_text(encoding="utf-8"))
            report_path.unlink()

    def test_verify_project_contract_fails_without_value_benchmark(self) -> None:
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
                "# Source Conversion Report\n\n## 识别质量摘要\n\n- 总页数：2\n- 视觉/表格/小字限制：复杂版式需复核。\n- 人工复核建议：检查低置信度区域。\n\n| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n## 识别质量总览\n\n- 总页数：1\n- 需要复核页数：0\n- 复核原则：优先处理含图片、低文字量、表格、小字或 OCR 不确定页面；关键品牌口径和关键数字必须回到原始页面确认。\n\n| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 |\n|---|---|---|---|---|---|---|---|\n| - | - | - | - | - | - | 无明显低置信度页面 | 继续后续语义编译 |\n",
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
                "内容读取报告 读取覆盖状态 整个文件概述 需要处理的问题 文件大纲参考",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=library_dir)

            output = stdout.getvalue()
            self.assertIn("Missing value benchmark", output)
            self.assertIn("Missing required output: outputs/00_source_index.md", output)
            self.assertIn("Structured output missing marker in outputs/11_context_library_update_plan.md: 优先读取", output)
            self.assertIn("Source total page mismatch: conversion_report.md=2, source_quality_report.md=1", output)

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
                "| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
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
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n", encoding="utf-8")
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
                "| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            review_dir = project_dir / "review"
            review_dir.mkdir()
            (review_dir / "brand_review.html").write_text(
                "Context Asset Index Review Review ID Source Anchor 来源位置：S001#page=1 来源锚点 风险等级 class=\"source-anchor\"",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n", encoding="utf-8")
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
                "| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
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

    def test_verify_contract_fails_when_public_source_manifest_is_tracked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_dir = Path(temp_dir)
            subprocess.run(["git", "init"], cwd=repo_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            manifest = repo_dir / "examples" / "demo" / "source" / "source_manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text('{"sources":[{"source_platform":"ima","media_id":"private_media"}]}', encoding="utf-8")
            subprocess.run(["git", "add", str(manifest)], cwd=repo_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            project_dir = repo_dir / "demo_project"
            project_dir.mkdir()
            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=repo_dir / "missing_library", repo_dir=repo_dir)

            output = stdout.getvalue()
            self.assertIn("Tracked public source manifest", output)
            self.assertIn("examples/demo/source/source_manifest.json", output)

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
                "| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
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
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n", encoding="utf-8")
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
                "| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            review_dir = project_dir / "review"
            review_dir.mkdir()
            (review_dir / "brand_review.html").write_text(
                "内容读取报告 读取覆盖状态 整个文件概述 需要处理的问题 文件大纲参考",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text("# 旧知识更新队列\n", encoding="utf-8")
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情 Source Anchor Risk Level 来源锚点 风险等级",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=library_dir)

            self.assertIn("Library report overexposes backend marker", stdout.getvalue())

    def test_verify_contract_fails_when_library_report_exposes_version_backend_file(self) -> None:
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
                "# Source Conversion Report\n\n## 识别质量摘要\n\n- 总页数：1\n- 视觉/表格/小字限制：复杂版式需复核。\n- 人工复核建议：检查低置信度区域。\n\n| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
                encoding="utf-8",
            )
            (converted / "source_quality_report.md").write_text(
                "# Source Quality Report\n\n## 识别质量总览\n\n- 总页数：1\n- 需要复核页数：0\n- 复核原则：优先处理含图片、低文字量、表格、小字或 OCR 不确定页面；关键品牌口径和关键数字必须回到原始页面确认。\n\n| Source Anchor | 原始文件 | 可抽取文字数 | 图片数 | 图形数 | 表格数 | 低置信度说明 | 建议动作 |\n|---|---|---|---|---|---|---|---|\n| - | - | - | - | - | - | 无明显低置信度页面 | 继续后续语义编译 |\n",
                encoding="utf-8",
            )
            (converted / "source_version_report.md").write_text(
                "# Source Version Report\n\n## 版本线索总览\n\n- 疑似多版本组数：1\n- 最新修改时间线索：不自动覆盖已有品牌知识。\n",
                encoding="utf-8",
            )
            (transcripts / "S001_demo.md").write_text(
                "Source Anchor：S001#page=1\nPage Screenshot：../assets/S001/page_01.png\n低置信度\n",
                encoding="utf-8",
            )
            review_dir = project_dir / "review"
            review_dir.mkdir()
            (review_dir / "brand_review.html").write_text(
                "内容读取报告 读取覆盖状态 整个文件概述 需要处理的问题 文件大纲参考",
                encoding="utf-8",
            )
            library_dir = Path(temp_dir) / "brand_context_library"
            for dirname in ["brand", "review_queue", "retrieval_maps"]:
                (library_dir / dirname).mkdir(parents=True, exist_ok=True)
            (library_dir / "brand" / "brand-tone.md").write_text("# 品牌语气\n", encoding="utf-8")
            (library_dir / "review_queue" / "conflicts.md").write_text("# Context Library Conflict Queue\n", encoding="utf-8")
            (library_dir / "review_queue" / "updates.md").write_text(
                "# 旧知识更新队列\n\n## 2026-06-10T00:00:00Z｜demo\n\n### 疑似多版本资料：summer_strategy\n\n- 更新方式：版本复核\n- 版本判断依据：source_version_report.md / 最新修改时间线索\n",
                encoding="utf-8",
            )
            (library_dir / "review_queue" / "do_not_promote.md").write_text("# Do Not Promote Queue\n", encoding="utf-8")
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n", encoding="utf-8")
            (library_dir / "library_report.html").write_text(
                "Brand Context Map Knowledge Explorer categoryFilter statusFilter 条目详情 待处理事项 source_version_report.md",
                encoding="utf-8",
            )

            with redirect_stdout(StringIO()) as stdout:
                with self.assertRaises(SystemExit):
                    verify_project_contract(project_dir, library_dir=library_dir)

            output = stdout.getvalue()
            self.assertIn("Library report exposes backend report file", output)
            self.assertIn("Library report missing version-review marker", output)

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
                "| 原始文件创建时间 | 原始文件修改时间 | 转写时间 | 低置信度区域 |\n|---|---|---|---|\n| 2026 | 2026 | 2026 | 无 |\n",
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
            (library_dir / "retrieval_maps" / "source_packages.md").write_text("# Source Package Retrieval Notes\n\n| 使用场景 | 优先读取 | 精读文件 | 回看原文 |\n|---|---|---|---|\n| Campaign brief | outputs/10_context_asset_index.md | converted_markdown/source_facts/S001_demo_source_facts.md | converted_markdown/source_transcripts/S001_demo.md |\n", encoding="utf-8")
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
