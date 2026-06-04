# Codex 第一轮开发任务清单

第一轮目标：先跑通“Marketing 资料 → AI-readable Markdown 营销语义底稿 → Brand Context Assets”的 Skill 组 / Workflow。不要把完整 GEO / PDP / 拍摄 / 种草 / 销售 / 复盘 brief 作为第一轮主交付。

请 Codex 按以下顺序开发：

1. 阅读 `00_Codex_开发总提示词.md`、`01_PRD_Brand_Product_Knowledge_Compiler.md`、`02_Skill_Spec.md`。
2. 按新版 PRD 补齐 repo 结构，第一阶段输出聚焦通用 Marketing 语义底稿闭环。
3. 创建或整理 Python package：`src/brand_skill/`。
4. 实现 CLI 命令：
   - `brand-skill init <project_name>`
   - `brand-skill validate-input <project_dir>`
   - `brand-skill convert-source <project_dir> --engine pymupdf4llm`
   - `brand-skill scaffold-output <project_dir>`
   - `brand-skill build-prompt-pack <project_dir>`
   - `brand-skill build-review-pack <project_dir>`
5. 实现 Source-to-Markdown baseline：
   - 遍历 `source/` 下 PDF。
   - 生成 `converted_markdown/source_transcripts/`。
   - 生成 `converted_markdown/assets/` 页面截图。
   - 生成 `converted_markdown/conversion_report.md`。
   - MinerU 暂作为 optional adapter，不阻塞第一版。
6. 根据 `schemas/` 生成第一阶段默认模板文件：
   - `00_source_index.md`
   - `01_source_conversion_report.md`
   - `02_document_profile.md`
   - `03_marketing_semantic_transcript.md`
   - `04_key_facts_and_claims.md`
   - `05_strategy_and_execution_map.md`
   - `06_risk_and_review_items.md`
   - `07_ai_ready_marketing_brief_base.md`
   - `08_review_pack.md`
   - `09_quality_check_report.md`
   - `10_context_asset_index.md`
7. 写 Document Profile 信息状态说明：
   - `已从来源资料提取`
   - `AI 结构化转述，待确认`
   - `AI 初步拟定，待品牌确认`
   - `待补充`
   - `不适用`
   - `已品牌确认`
8. 写 Marketing Semantic Transcript 的转述规则，强调完整转述、来源锚点、低置信度区域。
9. 写 Risk and Review Items 的基础校验思路。
10. 写 Context Asset Index 规则，按品牌、商品、素材、项目、话术、人设、网络、案例 8 类上下文资产归档。
11. 写真实测试资料处理规则：测试 PDF 可用于本地开发，但不能原样进入正式 Skill 内置 demo；如要写入 `examples/`，必须改写为匿名化假数据。
12. 示例品牌真实资料仅作为本地私有测试样本，不作为正式内置 demo，不让其定义全局默认结构。
13. 写 `docs/user_guide_for_brand_marketers.md`，用非技术语言说明品牌经理如何审核 Marketing 语义底稿和上下文资产。
14. 产品资料可选模块保留：
    - `brand-skill check-brand-lock <project_dir>`
    - `brand-skill check-claim-matrix <project_dir>`

第一轮不要接模型 API，不要做复杂 Web UI，不要做企业级 RAG，不要做完整派生 brief 自动生成。
