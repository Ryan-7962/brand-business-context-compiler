# Brand Marketing Context Compiler

将品牌方“给人看的”Marketing 资料，例如活动方案、广告公司提案、新品上市方案、销售策略、经销商大会 PPT、抖音爆品打法计划书、爆款视频复盘、投放总结、产品培训资料、品牌策略 PPT，编译为 **AI 更容易理解、检索、引用、审核和复用的结构化品牌上下文知识库**。

本项目第一阶段不是做复杂平台，也不是直接生成 GEO / PDP / 拍摄 / 种草 brief，而是沉淀一组可被 Codex / Claude / ChatGPT 等 AI 代理稳定执行的 Skills：

1. 先把 PDF / PPT / 长图 / 文档尽量保真地转成 Markdown。
2. 再识别资料类型、文件目的、目标读者、业务阶段和关键信息。
3. 将资料完整转述成 AI-readable Marketing Semantic Transcript。
4. 抽取关键事实、claim、策略、执行动作、风险和待确认项。
5. 生成 Context Asset Index，把资料沉淀为可复用的品牌上下文资产。
6. 生成 Context Library Update Plan，说明本次资料如何并入长期品牌知识库。
7. 生成 Exception Review Queue，只在识别异常时请用户修正。

## Skill 组结构

| Skill | 第一阶段职责 |
|---|---|
| Source Conversion Skill | 将 PDF / PPT / 长图 / 文档尽量保真转为 Markdown 中间稿 |
| Marketing Semantic Compiler Skill | 生成文件画像、完整语义转述、事实、策略、执行和风险底稿 |
| Context Asset Classifier Skill | 将底稿归入品牌、商品、素材、项目、话术、人设、网络、案例 8 类上下文资产 |
| Exception Review Queue Skill | 输出 Markdown 和静态 HTML 异常队列，只处理识别问题 |
| Context Asset Indexer Skill | 输出 `10_context_asset_index.md`，作为后续派生 Skill 的调用索引 |
| Context Library Planner Skill | 输出 `11_context_library_update_plan.md`，说明如何更新长期品牌知识库 |

第二阶段再开发 Derived Brief Skills，例如 GEO、PDP、拍摄、种草、销售、客服、投放复盘、案例复用等。

产品培训资料、PDP、包装文案和功效报告仍然支持，但它们只是 Marketing 文件的一类。SKU Cards、Product Knowledge Base、Claim Matrix 属于产品资料可选模块，不再是全局默认输出。

## 核心原则

- 不是“总结 PPT”，而是“品牌 Marketing 资料 AI 语义编译”。
- 先做 Source-to-Markdown 保真转述，再做 Marketing 语义结构化。
- 第一阶段先生成 AI-readable 营销语义底稿，后续再派生不同场景 brief。
- 不把所有资料强行套成产品项、SKU 或香型。
- 资料里没有的信息必须标注 `待补充` / `待确认` / `不适用`。
- 默认自动转写和入库，不让用户逐份确认；只有图片/表格/小字识别异常、疑似漏读或关键业务字段不确定时才进入人工复核。
- 内部策略、未确认判断、平台风险、竞品攻击、敏感数据必须在后台质量层明确暴露，但不应默认塞进给用户的确认页。
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
├── 10_context_asset_index.md
└── 11_context_library_update_plan.md
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
brand-skill import-ima-media _private_test_runs/<run_name> --media-id <ima_media_id> --title <file_name>
brand-skill convert-source <project_dir> --engine pymupdf4llm
brand-skill build-source-quality-report <project_dir>
brand-skill build-source-version-report <project_dir>
brand-skill build-source-facts <project_dir>
brand-skill compile-outputs <project_dir>
brand-skill scaffold-output <project_dir>
brand-skill build-prompt-pack <project_dir>
brand-skill build-review-pack <project_dir>
brand-skill apply-library-update <project_dir> --library-dir <brand_context_library_dir>
brand-skill build-library-report <brand_context_library_dir>
brand-skill verify-contract <project_dir> --library-dir <brand_context_library_dir> --write-report
brand-skill demo-contract <project_dir> --library-dir <brand_context_library_dir>
```

## 最小使用路径

```text
1. 把 PDF / PPTX / Markdown / TXT / DOCX 源稿放入 source/；PPT 旧格式 / 长图可先转成 PDF 或后续接入高保真转换器
2. 运行 source conversion，生成带页码和低置信度标记的 Markdown
3. 运行 build-source-quality-report，生成识别质量报告，定位需要 OCR / MinerU / 人工复核的页面
4. 运行 build-source-version-report，生成版本线索报告，定位同主题多版本资料
5. 运行 build-source-facts，生成只基于来源原文的事实候选层
6. 运行 compile-outputs，先生成 00-11 结构化输出底稿
7. 如需更高质量表达，再用 Prompt Bundle 或模型在底稿基础上精修
8. 查看 review/brand_review.html，只处理识别异常
9. 运行 apply-library-update，把可沉淀内容写入 brand_context_library/
10. 运行 build-library-report，生成一页中文知识库概览
11. 运行 verify-contract --write-report，检查当前产物是否满足项目执行准则里的核心证据，并留下本地验证报告
12. 后续写 GEO / PDP / 种草 / 销售 / 复盘 brief 时，从长期库调用上下文
```

本地验收 demo 可用一条命令跑完入库、知识库报告页和 contract 验证：

```bash
brand-skill demo-contract examples/anonymous_marketing_campaign --library-dir /tmp/bmcc_contract_demo
```

长期库会持续维护：

- `00_library_index.md`：知识库首页和统计。
- `library_report.html`：给 marketer 快速查看的中文知识库概览页。
- `evolution_log.md`：每次入库记录。
- `review_queue/conflicts.md`：疑似重复或冲突条目。
- `review_queue/updates.md`：可能需要更新旧知识的条目。
- `review_queue/do_not_promote.md`：不应提升为长期知识的临时信息。
- `retrieval_maps/source_packages.md`：每份资料未来适合在哪些任务中调用。

`build-library-report` 会生成 `library_report.html`，作为 Brand Context Map 使用：上方展示知识地图，下方提供搜索、筛选和条目详情。分类默认参考内置 Brand Marketing 分类；如果长期库中存在 `taxonomy.md`，则优先使用用户或 AI 确认过的动态分类。报告页会把冲突、旧知识更新和疑似多版本资料整理成中文待处理事项，保留“建议动作”和“最新修改时间线索”，但不把后台报告文件名铺给使用者。

`verify-contract` 会检查 `docs/project_success_contract.md` 中定义的核心证据，例如 source conversion 识别质量摘要、source quality report、source version report、关键 outputs、异常复核页、长期库条目、review queue、retrieval map、Brand Context Map、私有测试目录未被追踪、报告页离线静态约束，以及生成产物不得冒充 `已品牌确认`。异常复核页只应提示识别问题和文件大纲，不应退回到后台 Context Asset 全量审核页；知识库报告页也不应把 Source Anchor、Risk Level、后台报告文件名等质量标记铺到用户界面。若存在疑似多版本资料，报告页必须展示中文待处理事项、建议动作和最新修改时间线索。加上 `--write-report` 后会在项目根目录生成 `contract_verification_report.md`，用于保留本轮通过 / 失败证据。它用于每轮开发后的本地门禁，不替代人工业务判断。

`demo-contract` 是给本地开发和匿名 demo 验收用的便捷命令，会依次执行 `build-source-quality-report`、`build-source-version-report`、`compile-outputs --keep-existing`、`apply-library-update`、`build-library-report` 和 `verify-contract --write-report`。

如果需要在本机扫描私有测试关键词，可临时设置 `BRAND_SKILL_PRIVACY_TERMS_REGEX` 后再运行 `verify-contract`。不要把真实关键词写入仓库文件。

产品资料可选校验：

```bash
brand-skill check-brand-lock <project_dir>
brand-skill check-claim-matrix <project_dir>
```

`convert-source` 当前支持默认轻量引擎 `pymupdf4llm`：PDF 会生成逐页转写和页面截图；PPTX / Markdown / TXT / DOCX 源稿会作为文档类资料进入同一套 source transcript / conversion report 流程。PPTX 轻量路径只抽取 slide 文本，不保留完整版式、图片、图表、动画和备注。多个源文件一起导入时，Source ID 会按 `source/` 下的相对路径稳定分配，避免因为文件类型不同导致引用编号漂移。

`mineru` 作为高保真 optional engine 已预留架构，但第一版不强制安装。MinerU 适合后续增强 PDF / PPTX / DOCX / XLSX / 图片 / 扫描件的版面、表格、图片、OCR 和阅读顺序识别；当前本项目只在本地提示官方 CLI 入口，例如 `mineru -p <input_path> -o <output_path> -b pipeline`，不会默认上传真实品牌资料或把 MinerU 设为必需依赖。

如需判断本机是否具备 MinerU 小样评估条件，可先运行：

```bash
brand-skill check-mineru <project_dir>
brand-skill plan-mineru-eval <project_dir> --max-pages 5
```

该命令会生成 `converted_markdown/mineru_readiness_report.md`，记录是否检测到 MinerU CLI、CLI 路径、版本输出和下一步建议。它只做本地 readiness 检查，不会读取或上传品牌资料，也不代表 `convert-source --engine mineru` 已经完成真实高保真转写接入。

`plan-mineru-eval` 会读取 `converted_markdown/source_quality_report.md`，自动挑选最多 5 个最适合做 MinerU 对比的小样页面，并生成 `converted_markdown/mineru_eval_plan.md`。它只生成本地评估计划，不运行 MinerU，也不上传真实品牌资料。

如果 `source/` 中存在当前不支持的文件类型，`convert-source` 会停止并列出文件路径，不会静默跳过。这是为了避免品牌资料漏转后仍被误认为已经完整入库。

`convert-source` 会记录原始文件创建时间和修改时间。若多份品牌资料内容冲突，默认把修改时间更新的文件作为版本判断线索，但不会自动覆盖关键品牌口径；相关内容应进入冲突队列或旧知识更新队列。

`build-source-version-report` 会读取 `converted_markdown/conversion_report.md`，生成 `converted_markdown/source_version_report.md`。它会基于文件名和原始文件修改时间归并疑似同主题多版本资料，能处理 `v2`、`final`、`final0729`、`copy`、日期和 hash 类常见后缀，提示最新修改时间线索，并明确这些线索只用于复核，不自动覆盖长期知识。

`apply-library-update` 会读取 `source_version_report.md` 中的疑似多版本组，并追加到 `brand_context_library/review_queue/updates.md`，方便后续人工判断是补充、修正、替换还是暂不处理。

如果资料来自 ima 或其他私有知识库，可在 `source/source_manifest.json` 中记录外部来源。该文件只保存追溯线索，不参与转写：

```json
{
  "sources": [
    {
      "path": "brand_content/sample.pdf",
      "source_platform": "ima",
      "knowledge_base": "示例品牌知识库",
      "knowledge_path": "品牌内容 / sample.pdf",
      "media_id": "media_sample_001",
      "imported_at": "2026-06-11T00:00:00Z"
    }
  ]
}
```

这些字段会写入 source transcript 和 conversion report，方便后续追溯到私有资料源。真实 ima 文件仍只能放在 `_private_test_runs/` 做本地测试，不进入正式 demo 或 Skill 发布包。

也可以用私有导入命令自动完成下载和 manifest 生成：

```bash
brand-skill import-ima-media _private_test_runs/<run_name> \
  --media-id <ima_media_id> \
  --title <file_name.pdf> \
  --knowledge-base <private_kb_name> \
  --knowledge-path <private_kb_path>
```

该命令只允许写入 `_private_test_runs/`，会把文件保存到 `source/ima_imports/`，并生成 `source/source_manifest.json`。之后可继续运行 `convert-source` 和 `build-source-facts`。

`build-source-facts` 会读取 `converted_markdown/source_transcripts/`，生成 `converted_markdown/source_facts/`。这一步只抽取来源中已经出现的文字证据，保留 Source Anchor、章节上下文、表格行和低置信度说明；它不做品牌确认、不做外发安全判断，也不补写资料中没有的信息。

`build-source-quality-report` 会读取 source transcripts，生成 `converted_markdown/source_quality_report.md`。它汇总总页数、需要复核页数、低文字量页面、含图片/图形页面和低置信度说明，并给出 OCR / MinerU / 人工复核等建议动作。

`compile-outputs` 会读取 `source_facts/`、source transcripts、source quality report 和 source version report，生成 00-11 结构化 Markdown 初稿。它会把表格行保留为“表格结构信息”和 `structured_table` 资产，避免表格资料被压平成普通摘要。它是本地确定性底稿编译器，不调用模型，不做品牌确认，不补写来源资料没有的信息；后续可以再用 Prompt Bundle 或模型精修表达。

## 目录说明

- `00_Codex_开发总提示词.md`：可直接复制给 Codex 的完整开发提示词。
- `01_PRD_Brand_Product_Knowledge_Compiler.md`：当前保留原文件名，但内容已按 Brand Marketing Context Compiler 重写。
- `02_Skill_Spec.md`：Skill 工作流与规则。
- `prompts/`：各步骤可复用提示词。
- `schemas/`：每类输出的 Markdown Schema。
- `_private_test_runs/private_product_training_sample/`：本地私有产品培训测试样本，已加入 `.gitignore`，不属于正式 Skill 内置 demo。
- `_private_test_runs/private_brand_bpm_sample/`：本地私有品牌 BPM 测试样本，已加入 `.gitignore`，不属于正式 Skill 内置 demo。
- `examples/`：正式匿名化 demo 目录，后续只放虚构品牌、合成数据或已授权公开资料。
- `docs/source_converter_strategy.md`：资料转写层策略，包含 MinerU 等高保真解析项目可吸收经验。
- `docs/brand_context_library_architecture.md`：长期品牌上下文知识库结构。
- `docs/project_success_contract.md`：项目执行准则，定义最终目标、验证证据、限制条件、操作边界、下一步判断规则和阻塞报告格式。
- `discussion_context/`：本次对话沉淀的开发背景与关键讨论摘录。
