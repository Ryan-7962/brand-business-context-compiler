# Codex 开发总提示词｜Brand Context Skills Pack

你是一个资深 AI 产品架构师、品牌营销知识工程师、Marketing 资料语义编译工程师。请基于本仓库内容，开发一个名为 **Brand Context Skills Pack** 的轻量级 Skill 组 / Workflow 项目。

## 1. 项目目标

本项目的目标不是做普通 PPT/PDF 总结，也不是把资料强行整理成产品项、SKU 或香型结构。

它要把品牌方原本“给人看的”Marketing 资料，例如活动方案、广告公司提案、新品上市方案、销售策略、经销商大会 PPT、抖音爆品打法计划书、爆款视频营销总结、投放总结、品牌策略 PPT、产品培训资料，编译成 **AI 更容易理解、检索、引用、审核和二次派生的结构化 Brand Context Assets**。

核心流程：

```text
Marketing PDF / PPT / 长图 / 文档
  ↓
Source-to-Markdown 保真转述
  ↓
Document Profile
  ↓
Marketing Semantic Transcript
  ↓
Key Facts / Claims / Strategy / Execution / Risk
  ↓
AI-ready Marketing Brief Base
  ↓
Context Asset Index
  ↓
Review Pack
```

产品培训资料、PDP、包装文案和功效报告仍然支持，但只是 Marketing 文件的一类。Product Knowledge Base、Claim Matrix、SKU Cards 是可选产品模块，不是默认主流程。

## 2. 第一阶段目标

第一阶段只解决：

```text
Marketing 资料 → AI-readable Marketing Semantic Markdown
```

第一阶段不要做：

- 复杂 Web UI。
- 企业级 RAG。
- 模型 API 接入。
- 自动发布。
- 完整 GEO / PDP / 拍摄 / 种草 / 销售 / 复盘 brief 自动生成。

第一阶段必须做：

1. Source-to-Markdown 保真转述。
2. Document Profile 文件画像。
3. Marketing Semantic Transcript 完整语义转述。
4. Key Facts and Claims。
5. Strategy and Execution Map。
6. Risk and Review Items。
7. AI-ready Marketing Brief Base。
8. Review Pack。
9. Quality Check。
10. Context Asset Index。

## 3. 默认输出结构

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

产品资料可选模块：

```text
outputs/<project_slug>/optional_product_module/
├── product_knowledge_base_internal.md
├── product_knowledge_base_public_safe.md
├── claim_matrix.md
├── sku_cards.md
└── user_language_map.md
```

## 4. 信息状态

所有关键字段必须使用以下状态之一：

| 状态 | 含义 |
|---|---|
| 已从来源资料提取 | 资料中明确出现，可追溯来源 |
| AI 结构化转述，待确认 | AI 将原资料转成更清楚的结构化表达，需人工复核 |
| AI 初步拟定，待品牌确认 | AI 根据资料合理推导，不能视为品牌最终确认 |
| 待补充 | 资料中没有，AI 也不能合理拟定，必须由品牌方补充 |
| 不适用 | 当前资料类型不涉及该字段 |
| 已品牌确认 | 品牌经理确认后，才能作为最高优先级依据 |

## 5. Source-to-Markdown 规则

资料转写层必须尽量保留原始信息，不做营销总结，不改写 claim。

要求：

- 每页 PDF 或每张 slide 保留明确边界。
- 保留页码 / slide 编号。
- 保留标题层级、阅读顺序、正文、表格、图片/图表占位、speaker notes、页脚、角标、小字。
- 复杂表格或视觉页无法可靠还原时，保留截图路径并标注低置信度。
- 每个重要事实尽量保留来源锚点，例如 `S001#page=24`。
- 转写失败、OCR 不确定、图表难读区域必须标注 `低置信度，待人工复核`。

MinerU 可作为 optional high-fidelity engine，不替代本项目的 Marketing 语义编译层。

## 6. Marketing 语义编译规则

不要把所有资料强行产品化。请先识别资料类型，再决定抽取结构。

通用抽取字段：

- 文件类型。
- 文件目的。
- 目标读者。
- 时间范围。
- 业务阶段。
- 业务背景。
- 核心目标。
- 核心洞察。
- 目标人群。
- 策略主线。
- Big Idea / campaign idea。
- 渠道和触点。
- 内容资产。
- 节奏和时间线。
- 预算 / 资源 / 货盘 / 组织分工。
- 数据指标。
- 复盘结论。
- 下一步动作。
- 风险和待确认项。

当前资料没有的信息写 `待补充` 或 `不适用`，不得硬编。

## 7. 人工审核规则

以下内容必须进入审核：

- AI 判断出的文件类型是否正确。
- AI 转述是否遗漏关键页。
- 关键事实和数据是否准确。
- 策略主线是否被误读。
- 内部信息是否可能外泄。
- 竞品表达是否有攻击风险。
- 平台合规、医疗化、功效化风险。
- 哪些内容可用于后续派生 brief。
- 哪些内容能进入 Context Asset Index，哪些还只是待确认上下文。
- 真实测试 PDF 是否仅用于本地测试，未写入正式内置 demo 或 Skill 发布包。

## 7.1 Brand Context Asset 规则

第一阶段必须沉淀 `10_context_asset_index.md`，按 8 类上下文资产归档：

| 上下文类型 | 说明 |
|---|---|
| 品牌上下文 | 品牌定位、品牌资产、语气、战略边界、品牌角色 |
| 商品上下文 | 产品、SKU、卖点、claim、证据、适用范围 |
| 素材上下文 | 图片、视频、脚本、视觉元素、素材表现、可复用素材结构 |
| 项目上下文 | 项目目标、阶段、时间线、预算、渠道、执行任务、责任分工 |
| 话术上下文 | 对内培训话术、对外表达、销售话术、客服话术、禁用表达 |
| 人设上下文 | 达人/KOL/主播/品牌人格/目标人群画像和表达方式 |
| 网络上下文 | 平台环境、搜索语境、社媒语境、竞品舆情、用户评论网络 |
| 案例上下文 | 成功/失败案例、复盘结论、可迁移打法、不可复用条件 |

每个 Context Asset 必须有来源锚点、信息状态、Review Priority、适用下游 Skill、禁止/限制使用条件。缺失的决策背景、素材表现、投放数据、品牌确认结论必须写 `待补充`。

## 7.2 真实测试资料处理规则

开发过程中可以使用真实品牌 PDF 测试解析、转写、审核页和 Context Asset Index。但这些真实 PDF 和由其生成的真实品牌信息不是正式 Skill 内容。

如果要把测试结果写入正式 `examples/`、README、PRD、Skill Spec、prompt 示例或发布包，必须删除真实品牌名、竞品名、SKU、价格、预算、销量、曝光、搜索增长、渠道激励、供应商和内部执行数据，改写为匿名化假数据。

## 8. CLI 第一版

必须实现或保留：

```bash
brand-skill init <project_name>
brand-skill validate-input <project_dir>
brand-skill convert-source <project_dir> --engine pymupdf4llm
brand-skill scaffold-output <project_dir>
brand-skill build-prompt-pack <project_dir>
```

产品资料可选模块可保留：

```bash
brand-skill check-brand-lock <project_dir>
brand-skill check-claim-matrix <project_dir>
```

## 9. Demo 说明

当前示例产品训练资料和示例品牌策略资料只作为本地私有测试样本，不属于正式 Skill 内置 demo。它们可以用于验证产品资料、品牌策略和渠道策略资料类型，但不能反向定义整个 Skill，也不能原样写入发布包。

后续应补非产品 demo，例如：

- 活动方案 / 新品上市方案。
- 投放复盘 / 爆款视频营销总结。

## 10. 第一轮验收

第一轮至少验证：

1. `scaffold-output` 生成通用 Marketing 语义底稿默认文件。
2. `build-prompt-pack` 只包含第一阶段 Marketing 语义编译 prompt，不包含第二阶段派生 brief prompt，也不默认包含产品可选模块 prompt。
3. `convert-source` 能处理真实 PDF 并保留页码、截图和 conversion report。
4. `10_context_asset_index.md` 能进入 scaffold、prompt bundle、review HTML 和本地私有测试样本。
5. 旧产品资料校验器作为 optional module 保留，不影响默认主流程。
