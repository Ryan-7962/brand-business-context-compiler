import tempfile
import unittest
import warnings
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

from brand_skill.cli import main as cli_main
from brand_skill.library_report import build_library_report
from brand_skill.library_writer import apply_context_library_update
from brand_skill.review_pack import build_review_pack
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
            self.assertIn("pymupdf4llm", report_text)

    def test_convert_source_marks_mineru_as_optional(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with redirect_stdout(StringIO()):
                with self.assertRaises(SystemExit):
                    convert_source(Path(temp_dir), engine="mineru")

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


if __name__ == "__main__":
    unittest.main()
