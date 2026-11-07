# 品牌资料转 MD 与 AI 复用助手

Brand Business Context Compiler · WorkBuddy / Codex / Claude Agent Skill

将品牌方案、产品培训、竞品分析、分镜与复盘等 PPTX、PDF、DOCX 资料整理为详细、可追溯的 Markdown，保留业务事实、表格关系、来源位置和待核对内容，供后续 AI 生成 Brief、回答产品问题和开展竞品分析时复用。

作者已在个人实际工作中完成试用，并于 2026 年 11 月 6 日完成一份 55 页营销提案的直接读取与 Skill 转译对照。项目的重点是逐页覆盖检查、来源追溯、异常披露与资料复用。

## 可以用来做什么

- **整理品牌资料**：把方案、培训和复盘资料编译成详细中文 MD，保留关键数字、适用条件、策略和执行信息。
- **处理图文与表格**：结合宿主 Agent 的文字、视觉或 OCR 能力，整理竞品表、图表和分镜中的文字与关系。
- **核对来源**：使用真实页码或 slide 锚点定位原件，记录仍未读清的位置及资料自身缺失的信息。
- **复用业务上下文**：将整理后的 MD 提供给 Agent，继续生成 Brief、FAQ、竞品对比或专题分析，需要持续积累时再建立 Wiki。

## 2026-11-06 实际资料对照

本次对照使用一份 55 页营销提案。直接读取侧先统计全文件原生文字，再由独立 Agent 对 6 个代表页看图整理。Skill 侧已有全量 55 页 MD 成品。以下结果来自作者提供的本地对照报告及指标文件，原始业务资料与详细测试记录在本地保存。

| 检查项 | 直接读取侧 | Skill 转译侧 |
|---|---|---|
| 页级交付记录 | 指定抽检 6 页中，5 页形成章节，1 页缺失 | 55 页连续章节、55 个来源锚点 |
| 共同覆盖的 5 页核心数字与文案 | 本次对照未发现冲突 | 本次对照未发现冲突 |
| 竞品表 | 分为多张表 | 整理为一行一款的 7 款竞品对照 |
| 未读清内容披露 | 抽样结果中 6 处 | 全量成品中 15 处，标明具体位置 |
| 后续使用 | 从原件或抽样回答继续整理 | 可基于带来源的 MD 检索、引用及派生内容 |

本次样本验证了 Skill 的页级覆盖记录、规整结构和异常披露。直接读取侧的深读范围为 6 页，Skill 成品范围为 55 页，两侧范围不同。55 个锚点表示页级结构覆盖，全文语义准确率、处理速度和时间收益需要另行测量。直接读取采用原生文字统计与独立 Agent 看图组合，PDF 专用工具在本文件上曾因缺少本地 OCR 引擎失败。

## 同事如何开始

1. 下载[同事试用版](https://github.com/Ryan-7962/brand-business-context-compiler/releases/tag/v0.2.0-pilot.3)中的 Skill ZIP 与 `START_HERE_ZH.md`。
2. 按[中文使用说明](docs/work_buddy_handoff_guide.md)安装到 WorkBuddy，准备一份可用于测试的资料。
3. 发送任务，要求详细整理正文、保留来源并标出真实读取缺口。
4. 核对结果后，将 MD 用于新的业务任务，继续生成 Brief、问答或竞品分析。

可按以下方式描述任务，并结合所用版本支持的流程执行。

```text
请调用 brand-business-context-compiler Skill，整理我提供的品牌资料。
保留关键数字、适用条件、表格关系及真实来源位置，结合页面图片处理图文内容。
交付详细中文 Markdown，并标出仍未读清、来源冲突或资料未提供的信息。
```

读取与视觉处理依赖所用 Agent 的工具能力。上述 11 月对照属于作者实际使用记录，GitHub 同事试用包为独立版本，安装与使用方式以该包说明为准。

## 开发与兼容模块

| Skill | 第一阶段职责 |
|---|---|
| Source Conversion Skill | 将 PDF / PPT / 长图 / 文档尽量保真转为 Markdown 中间稿 |
| Marketing Semantic Compiler Skill | 生成文件画像、完整语义转述、事实、策略、执行和风险底稿 |
| Context Asset Classifier Skill | 将底稿归入建议分类，例如 brand / product / project / asset / language / persona / network / case / decision；真实项目可由模型和业务语境调整 |
| Exception Review Queue Skill | 输出 Markdown 和静态 HTML 异常队列，只处理识别问题 |
| Context Asset Indexer Skill | 输出 `10_context_asset_index.md`，作为后续派生 Skill 的调用索引 |
| Context Library Planner Skill | 输出 `11_context_library_update_plan.md`，说明如何更新长期品牌知识库 |

第二阶段再开发 Derived Brief Skills，例如 GEO、PDP、拍摄、种草、销售、客服、投放复盘、案例复用等。

产品培训资料、PDP、包装文案和功效报告仍然支持，但它们只是 Marketing 文件的一类。SKU Cards、Product Knowledge Base、Claim Matrix 属于产品资料可选模块，不再是全局默认输出。

## 核心原则

- 保留品牌资料的业务语义、数字条件和可追溯来源。
- 先做 Source-to-Markdown 保真转述，再做 Marketing 语义结构化。
- 第一阶段先生成 AI-readable 营销语义底稿，后续再派生不同场景 brief。
- 不把所有资料强行套成产品项、SKU 或香型。
- 资料里没有的信息必须标注 `待补充` / `待确认` / `不适用`。
- 默认自动转写、索引和入库，不让用户逐份确认；只有文件大纲跑偏、页面/slide 漏读、图片/表格/小字/OCR 识别异常、版本冲突或资料本身缺信息时才进入人工复核。
- 报告页只说明本次读了什么、索引大纲是什么、哪些地方没读清楚、需要用什么方式弥补；不要求用户检查所有后台事实表。
- 内部策略、未确认判断、平台风险、竞品攻击、敏感数据必须在后台质量层明确暴露，但不应默认塞进给用户的确认页。
- 仓库内置 demo / Skill 发布包不得包含真实测试 PDF 中的品牌名、竞品名、价格、预算、销量、渠道激励和平台数据；真实客户资料只作为本地私有测试材料使用。
- 产品类 claim 仍需证据和适用范围，但只在产品资料模块启用。

详见 [docs/test_fixture_privacy_rules.md](docs/test_fixture_privacy_rules.md)。

## 完整流程产物

```text
outputs/
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

产品资料模块属于可选扩展，不是第一阶段默认产物。遇到产品培训、PDP、包装文案、功效报告或 claim 审核资料时，可按需输出：

```text
outputs/optional_product_module/
├── product_knowledge_base_internal.md
├── product_knowledge_base_public_safe.md
├── claim_matrix.md
├── sku_cards.md
└── user_language_map.md
```

GEO / PDP / 拍摄 / 种草 / 销售 / 客服 / 复盘 / 竞品分析等派生产出属于第二阶段。第一阶段只保证 Structured Wiki 能告诉后续 Agent 应该读取哪些资料和来源事实。

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

## 推荐使用路径

需要迁移到另一台 Windows / macOS 电脑，或导入 WorkBuddy 时，直接查看 [换电脑安装与测试](docs/cross_platform_test_guide.md)。

需要持续建库时，可使用 Agent-neutral Wiki 的五步流程：

1. 初始化项目，并将 PDF / PPTX / DOCX / Markdown / TXT 等资料放入 `source/`：

   ```bash
   brand-skill init <project_dir>
   ```

2. 准备可追溯的确定性证据：

   ```bash
   brand-skill prepare-wiki <project_dir>
   ```

3. 让 Codex、WorkBuddy 或其他活动 Agent 阅读每份 prepared transcript 和 evidence file，按 [SKILL.md](SKILL.md) 使用仓库内的 `prompts/10_compile_agent_neutral_wiki.md` 与 `schemas/agent_neutral_wiki.schema.md` 写入 `wiki/`；WorkBuddy ZIP 中这两个文件位于 `references/`。
4. 生成给使用者查看的 Wiki 报告：

   ```bash
   brand-skill build-wiki-report <project_dir>
   ```

5. 检查 Wiki 的文件结构、覆盖率、来源锚点和未解决占位项：

   ```bash
   brand-skill verify-wiki <project_dir>
   ```

WorkBuddy 没有 CLI 时，应使用同一 Skill 中的本地读文件能力完成第 3 步，并把每个未读文件或页面如实记录在 `wiki/uncertainties.md`。实际 WorkBuddy 导入和调用的待办证据见 [docs/workbuddy_validation_checklist.md](docs/workbuddy_validation_checklist.md)。

## Legacy Compatibility

`brand-skill run-phase1` 保留为旧项目兼容路径，不是新项目的推荐流程。它的历史命令与 00-11 输出契约仍可供既有项目继续使用；新 Wiki 工作流不展开这套旧命令矩阵。

当前阶段的收敛与验收文档：

- [docs/phase1_completion_audit.md](docs/phase1_completion_audit.md)：第一阶段完成度和证据缺口。
- [docs/agent_workstream_split.md](docs/agent_workstream_split.md)：45 个可分派 Agent 子板块。
- [docs/ponytail_simplification_audit.md](docs/ponytail_simplification_audit.md)：哪些能力保留、延后或移出第一阶段。
- [docs/source_reading_quality_playbook.md](docs/source_reading_quality_playbook.md)：PDF / PPT / 长图读取质量验收。
- [docs/quality_sampling_protocol.md](docs/quality_sampling_protocol.md)：90% 读取准确性抽样证据协议。
- [docs/manual_validation_sop.md](docs/manual_validation_sop.md)：人工原页抽样验收的一页执行单。

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

`verify-contract` 会检查 `docs/project_success_contract.md` 中定义的核心证据，例如 source conversion 识别质量摘要、source quality report、source version report、关键 outputs、异常复核页、长期库条目、review queue、retrieval map、Brand Context Map、私有测试目录未被追踪、报告页离线静态约束，以及生成产物不得冒充 `已品牌确认`。异常复核页只应提示识别问题和文件大纲，不应退回到后台 Context Asset 全量审核页；知识库报告页也不应把 Source Anchor、Risk Level、后台报告文件名等质量标记铺到用户界面。若存在疑似多版本资料，报告页必须展示中文待处理事项、建议动作和最新修改时间线索。加上 `--write-report` 后会在项目根目录生成 `contract_verification_report.md`，用于保留本轮通过 / 失败证据；其中 `Quality sampling evidence` 只说明人工抽样证据状态，`pending; no 90% evidence` 不能当成 90% 准确率证明。它用于每轮开发后的本地门禁，不替代人工业务判断。

`demo-contract` 是给本地开发和匿名 demo 验收用的便捷命令，会依次执行 `build-source-quality-report`、`build-source-version-report`、刷新结构化 outputs、`build-review-pack`、`apply-library-update`、`build-library-report`、`build-value-benchmark` 和 `verify-contract --write-report`。

`build-value-benchmark` 会生成 `evaluation/direct_vs_skill_benchmark.md`，用于对比“直接把 PDF/PPT 发给 AI”和“先经 Skill 转写、抽 facts、编译、入库后再回答”的差异。它也会在缺少 `evaluation/quality_sampling_log.md` 时生成抽样日志，把总页数、需复核页数、source facts 数和建议抽样页写清楚；如果日志已存在，会保留人工回填结果。未完成原页核对前，这份日志只作为抽样计划，不能宣称 90% 准确率。

如果私有测试目录里有 `evaluation/agent_ab_packet.md`，真实 Agent 对照优先复制其中的 A/B 提示词；没有这份入口包时，再使用 `direct_vs_skill_benchmark.md` 中的通用提示词。

如果私有测试目录里有 `evaluation/human_validation_packet.md` 或 `evaluation/human_validation_packet.html`，人工抽样优先从这份入口包开始，再把结果回填到 `quality_sampling_log.md`；HTML 入口包如提供“生成回填摘要”，可先复制摘要再补 facts 结论。

如果需要在本机扫描私有测试关键词，可临时设置 `BRAND_SKILL_PRIVACY_TERMS_REGEX` 后再运行 `verify-contract`。不要把真实关键词写入仓库文件。

产品资料可选校验只在产品 claim 场景启用，不属于推荐的 Wiki 流程：

```bash
brand-skill check-brand-lock <project_dir>
brand-skill check-claim-matrix <project_dir>
```

`convert-source` 当前支持默认轻量引擎 `pymupdf4llm`：PDF 会生成逐页转写和页面截图；PPTX / Markdown / TXT / DOCX 源稿会作为文档类资料进入同一套 source transcript / conversion report 流程。PPTX 轻量路径只抽取 slide 文本，不保留完整版式、图片、图表、动画和备注。多个源文件一起导入时，Source ID 会按 `source/` 下的相对路径稳定分配，避免因为文件类型不同导致引用编号漂移。

`markitdown` 作为多格式 Markdown 转换候选已接入可选 adapter，但尚未设为默认引擎。安装后可运行 `brand-skill convert-source <project_dir> --engine markitdown`；如果本地未安装，CLI 会提示使用 `.venv/bin/python -m pip install 'markitdown[all]'`。它只属于 Source-to-Markdown 层，不能替代 Context Asset Index、Library Update Plan、版本冲突处理和长期知识库。

MarkItDown 输出会进入同一套 `source_transcripts/` 和 `conversion_report.md` 格式，但它不保证稳定页码 / slide 边界，也不等于高保真 OCR。用于真实品牌资料时，应继续结合 `source_quality_report.md` 和 `source_engine_eval_plan.md` 抽样检查图片、表格、小字、阅读顺序和关键品牌口径。

`mineru` 作为高保真 optional engine 已预留架构，但第一版不强制安装。MinerU 适合后续增强 PDF / PPTX / DOCX / XLSX / 图片 / 扫描件的版面、表格、图片、OCR 和阅读顺序识别；当前本项目只在本地提示官方 CLI 入口，例如 `mineru -p <input_path> -o <output_path> -b pipeline`，不会默认上传真实品牌资料或把 MinerU 设为必需依赖。

如需统一检查候选 source engines，可运行：

```bash
brand-skill check-source-engines <project_dir>
brand-skill plan-source-engine-eval <project_dir> --max-pages 5
brand-skill scaffold-source-engine-eval-results <project_dir>
```

`check-source-engines` 会生成 `converted_markdown/source_engine_readiness_report.md`，记录当前本机是否检测到 MarkItDown / MinerU CLI，并明确这些工具只是转写候选，不是品牌知识编译器本体。

`plan-source-engine-eval` 会读取 `converted_markdown/source_quality_report.md`，生成 `converted_markdown/source_engine_eval_plan.md`，用于选择最多 5 个高价值小样，对比 pymupdf4llm baseline、MarkItDown 和 MinerU 在文字覆盖率、表格、图片/图表、阅读顺序、Markdown 可读性、部署复杂度和隐私风险上的差异。

`scaffold-source-engine-eval-results` 会读取 `source_engine_eval_plan.md`，生成 `converted_markdown/source_engine_eval_results.md`。该文件只记录候选引擎小样对比证据，不是品牌确认；在没有真实小样证据前，默认判断仍保持 `pymupdf4llm` baseline。

MinerU 单独 readiness / eval 命令仍可作为本地调试入口保留，但 README 不再把它列为第一阶段默认路径。真实验收优先使用通用 source engine eval；只有连续出现图片、表格、小字或扫描件读取缺口时，再做 MinerU 小样对比。

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

`build-source-quality-report` 会读取 source transcripts，生成 `converted_markdown/source_quality_report.md`。它汇总总页数、Agent 重点检查候选、低文字量页面、含图片/图形页面、表格页和低置信度说明。候选页不自动等于人工异常：Agent 应先检查转写稿和页面截图，仍无法判断时才写入 `wiki/uncertainties.md`。`表格数` 只统计原文区中的 Markdown 表格，避免把转写器生成的图片元数据表误判为原资料表格。

`compile-outputs` 会读取 `source_facts/`、source transcripts、source quality report 和 source version report，生成 00-11 结构化 Markdown 初稿。它会把表格行保留为“表格结构信息”和 `structured_table` 资产，避免表格资料被压平成普通摘要。它是本地确定性底稿编译器，不调用模型，不做品牌确认，不补写来源资料没有的信息；后续可以再用 Prompt Bundle 或模型精修表达。

## 目录说明

- `00_Codex_开发总提示词.md`：可直接复制给 Codex 的完整开发提示词。
- `SKILL.md`：AI Agent 使用本项目时的技能入口和第一阶段执行规则。
- `01_PRD_Brand_Product_Knowledge_Compiler.md`：当前保留原文件名，但内容已按 Brand Marketing Context Compiler 重写。
- `02_Skill_Spec.md`：Skill 工作流与规则。
- `prompts/`：各步骤可复用提示词。
- `schemas/`：每类输出的 Markdown Schema。
- `_private_test_runs/private_product_training_sample/`：本地私有产品培训测试样本，已加入 `.gitignore`，不属于正式 Skill 内置 demo。
- `_private_test_runs/private_brand_bpm_sample/`：本地私有品牌 BPM 测试样本，已加入 `.gitignore`，不属于正式 Skill 内置 demo。
- `examples/`：正式匿名化 demo 目录，后续只放虚构品牌、合成数据或已授权公开资料。
- `docs/source_converter_strategy.md`：资料转写层策略，包含 MinerU 等高保真解析项目可吸收经验。
- `docs/project_goal.md`：更新后的项目目标、价值边界、Source Engine 策略和第一阶段验收标准。
- `docs/brand_context_library_architecture.md`：长期品牌上下文知识库结构。
- `docs/work_buddy_handoff_guide.md`：把 Structured Wiki 交给 Work Buddy / Agent 使用的复制式提示词和读取顺序。
- `docs/project_success_contract.md`：项目执行准则，定义最终目标、验证证据、限制条件、操作边界、下一步判断规则和阻塞报告格式。
- `discussion_context/`：本次对话沉淀的开发背景与关键讨论摘录。
