# Brand Context Skills Pack

将品牌方“给人看的”Marketing 资料，例如活动方案、广告公司提案、新品上市方案、销售策略、经销商大会 PPT、抖音爆品打法计划书、爆款视频复盘、投放总结、产品培训资料、品牌策略 PPT，编译为 **AI 更容易理解、检索、引用、审核和复用的结构化 Brand Context Assets**。

本项目第一阶段不是做复杂平台，也不是直接生成 GEO / PDP / 拍摄 / 种草 brief，而是沉淀一组可被 Codex / Claude / ChatGPT 等 AI 代理稳定执行的 Skills：

1. 先把 PDF / PPT / 长图 / 文档尽量保真地转成 Markdown。
2. 再识别资料类型、文件目的、目标读者、业务阶段和关键信息。
3. 将资料完整转述成 AI-readable Marketing Semantic Transcript。
4. 抽取关键事实、claim、策略、执行动作、风险和待确认项。
5. 生成 Context Asset Index，把资料沉淀为可复用的品牌上下文资产。
6. 生成 Review Pack，帮助品牌经理集中确认关键判断。

## Skill 组结构

| Skill | 第一阶段职责 |
|---|---|
| Source Conversion Skill | 将 PDF / PPT / 长图 / 文档尽量保真转为 Markdown 中间稿 |
| Marketing Semantic Compiler Skill | 生成文件画像、完整语义转述、事实、策略、执行和风险底稿 |
| Context Asset Classifier Skill | 将底稿归入品牌、商品、素材、项目、话术、人设、网络、案例 8 类上下文资产 |
| Review Pack Skill | 输出 Markdown 和静态 HTML 审核页，让品牌经理集中确认 |
| Context Asset Indexer Skill | 输出 `10_context_asset_index.md`，作为后续派生 Skill 的调用索引 |

第二阶段再开发 Derived Brief Skills，例如 GEO、PDP、拍摄、种草、销售、客服、投放复盘、案例复用等。

产品培训资料、PDP、包装文案和功效报告仍然支持，但它们只是 Marketing 文件的一类。SKU Cards、Product Knowledge Base、Claim Matrix 属于产品资料可选模块，不再是全局默认输出。

## 核心原则

- 不是“总结 PPT”，而是“品牌 Marketing 资料 AI 语义编译”。
- 先做 Source-to-Markdown 保真转述，再做 Marketing 语义结构化。
- 第一阶段先生成 AI-readable 营销语义底稿，后续再派生不同场景 brief。
- 不把所有资料强行套成产品项、SKU 或香型。
- 资料里没有的信息必须标注 `待补充` / `待确认` / `不适用`。
- 内部策略、未确认判断、平台风险、竞品攻击、敏感数据必须在审核层明确暴露。
- 仓库内置 demo / Skill 发布包不得包含真实测试 PDF 中的品牌名、竞品名、价格、预算、销量、渠道激励和平台数据；真实客户资料只作为本地私有测试材料使用。
- 产品类 claim 仍需证据和适用范围，但只在产品资料模块启用。

详见 [docs/test_fixture_privacy_rules.md](/Users/ryan/AI%20相关/产品资料转%20MD/brand-ai-product-knowledge-skill_handoff/docs/test_fixture_privacy_rules.md)。

## 第一阶段默认产物

```text
outputs/<project_slug>/
├── 00_source_index.md
├── 01_source_conversion_report.md
├── 02_document_profile.md
├── 03_marketing_semantic_transcript.md
├── 04_key_facts_and_claims.md
├── 05_strategy_and_execution_map.md
├── 06_risk_and_review_items.md
├── 07_ai_ready_marketing_brief_base.md
├── 08_review_pack.md
├── 09_quality_check_report.md
└── 10_context_asset_index.md
```

产品资料可选模块可输出：

```text
outputs/<project_slug>/optional_product_module/
├── product_knowledge_base_internal.md
├── product_knowledge_base_public_safe.md
├── claim_matrix.md
├── sku_cards.md
└── user_language_map.md
```

第二阶段派生产物可预留在：

```text
outputs/<project_slug>/derived_briefs/
├── geo_brief.md
├── pdp_brief.md
├── shooting_brief.md
├── seeding_brief.md
├── customer_service_faq.md
├── sales_enablement_brief.md
├── campaign_recap_brief.md
└── competitor_battlecard.md
```

## 信息状态

关键字段应标注信息状态：

| 状态 | 含义 |
|---|---|
| 已从来源资料提取 | 资料中明确出现，可追溯来源 |
| AI 结构化转述，待确认 | AI 将原资料转成更清楚的结构化表达，需人工复核 |
| AI 初步拟定，待品牌确认 | AI 根据资料合理推导，不能视为品牌最终确认 |
| 待补充 | 资料中没有，AI 也不能合理拟定，必须由品牌方补充 |
| 不适用 | 当前资料类型不涉及该字段 |
| 已品牌确认 | 品牌经理确认后，才能作为最高优先级依据 |

## CLI 第一版

```bash
brand-skill init <project_name>
brand-skill validate-input <project_dir>
brand-skill convert-source <project_dir> --engine pymupdf4llm
brand-skill scaffold-output <project_dir>
brand-skill build-prompt-pack <project_dir>
brand-skill build-review-pack <project_dir>
```

产品资料可选校验：

```bash
brand-skill check-brand-lock <project_dir>
brand-skill check-claim-matrix <project_dir>
```

`convert-source` 当前支持默认轻量引擎 `pymupdf4llm`。`mineru` 作为高保真 optional engine 已预留架构，但第一版不强制安装。

## 目录说明

- `00_Codex_开发总提示词.md`：可直接复制给 Codex 的完整开发提示词。
- `01_PRD_Brand_Product_Knowledge_Compiler.md`：当前保留原文件名，但内容已按 Brand Context Skills Pack 重写。
- `02_Skill_Spec.md`：Skill 工作流与规则。
- `prompts/`：各步骤可复用提示词。
- `schemas/`：每类输出的 Markdown Schema。
- `_private_test_runs/private_product_training_sample/`：本地私有产品培训测试样本，已加入 `.gitignore`，不属于正式 Skill 内置 demo。
- `_private_test_runs/private_brand_bpm_sample/`：本地私有品牌 BPM 测试样本，已加入 `.gitignore`，不属于正式 Skill 内置 demo。
- `examples/`：正式匿名化 demo 目录，后续只放虚构品牌、合成数据或已授权公开资料。
- `docs/source_converter_strategy.md`：资料转写层策略，包含 MinerU 等高保真解析项目可吸收经验。
- `discussion_context/`：本次对话沉淀的开发背景与关键讨论摘录。
