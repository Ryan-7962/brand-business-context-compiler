# Skill Spec｜Brand Context Skills Pack

## 1. Skill 名称

Brand Context Skills Pack / 品牌上下文资产 Skill 组

## 2. Skill 目标

把品牌方原本给人看的 Marketing 资料，编译成 AI 更容易理解、检索、引用、审核和复用的结构化 Brand Context Assets。

第一阶段只处理：

```text
Marketing PDF / PPT / 长图 / 文档
  ↓
Source-to-Markdown 保真转述
  ↓
Document Profile
  ↓
Marketing Semantic Transcript
  ↓
AI-ready Marketing Brief Base
  ↓
Context Asset Index
  ↓
Exception Review Queue
```

GEO brief、PDP brief、拍摄 brief、种草 brief、客服 FAQ、销售话术、活动复盘等属于第二阶段派生应用，不作为第一阶段主流程。

## 3. 输入

### 3.1 来源资料目录

```text
source/
├── campaign_plan/
├── agency_proposal/
├── launch_plan/
├── sales_strategy/
├── dealer_conference/
├── douyin_growth_plan/
├── video_case_study/
├── media_performance_review/
├── brand_strategy/
├── product_training/
├── ecommerce_pdp/
├── claim_reports/
├── packaging_copy/
├── competitor_sources/
└── historical_briefs/
```

### 3.2 品牌确认输入

第一阶段支持可选的品牌确认输入：

```text
brand_input/
└── review_decisions.json
```

如果没有确认输入，Skill 默认先自动生成结构化底稿和异常复核队列。只有识别质量异常的页面或问题需要用户处理；没有异常的资料直接进入知识库沉淀。

## 4. 第一阶段默认输出

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

## 5. 工作流

### Step 1. Source Inventory

读取来源文件，生成 `00_source_index.md`。记录：文件名、类型、来源、日期、包含信息、可信度、是否可外发引用、备注和限制。

### Step 2. Source-to-Markdown Conversion

将 PDF/PPT/PPTX/详情页/长图/包装文案等原始资料转成中间 Markdown，并生成 `01_source_conversion_report.md`。

要求：

- 保留页码 / slide 编号。
- 保留标题、阅读顺序、表格、图片/图表占位、speaker notes、角标、脚注。
- 转写层不做营销总结，不改写 claim。
- 解析不确定的位置标注 `低置信度，待人工复核`。

CLI：

```bash
brand-skill convert-source <project_dir> --engine pymupdf4llm
```

### Step 3. Document Profile

生成 `02_document_profile.md`，识别：

- 文件类型：活动方案 / 广告提案 / 新品上市 / 销售策略 / 经销商大会 / 投放总结 / 爆款视频复盘 / 产品培训 / 品牌策略 / 其他。
- 文件目的：提案、汇报、复盘、培训、预算申请、策略对齐、招商、销售推进等。
- 目标读者。
- 时间范围。
- 业务阶段。
- 资料可信度和限制。

### Step 4. Marketing Semantic Transcript

生成 `03_marketing_semantic_transcript.md`。

这一步是更完整、更可追溯的语义转述，不是短摘要。它应把原资料里的策略页、图表页、视觉页、执行页转成 AI 能理解的文字，并保留来源锚点。

### Step 5. Key Facts and Claims

生成 `04_key_facts_and_claims.md`，抽取：

- 明确事实。
- 数据和指标。
- 业务判断。
- 关键 claim / 传播主张。
- 证据来源。
- 不确定或待补充信息。

产品类 claim 需要额外记录适用范围。非产品资料则记录适用场景、渠道、时间、目标人群或活动范围。

### Step 6. Strategy and Execution Map

生成 `05_strategy_and_execution_map.md`，根据资料内容抽取：

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

没有的信息标注 `待补充` 或 `不适用`。

### Step 7. Risk and Review Items

生成 `06_risk_and_review_items.md`，列出：

- 事实缺口。
- 策略推断风险。
- 数据和口径风险。
- 竞品攻击风险。
- 平台合规风险。
- 医疗化 / 功效化风险。
- 内部信息外泄风险。
- 需要品牌经理确认的关键判断。

### Step 8. AI-ready Marketing Brief Base

生成 `07_ai_ready_marketing_brief_base.md`。

这是给后续大模型调用的营销语义底稿。它不直接生成某个 brief，而是把后续可复用的信息组织成稳定结构。

### Step 9. Exception Review Queue

生成 `08_review_pack.md`，并可进一步生成静态 HTML 异常复核页。

静态 HTML 面向使用者，必须是中文轻量异常队列。它不要求用户逐份确认完整内容，只在以下情况出现问题：

- 图片、图表、小字、角标、脚注无法稳定识别。
- 表格结构疑似错位。
- 某页疑似漏读或只抽取到少量文字。
- 会议背景、日期、参会方、决策结论等关键业务字段无法判断。
- 关键业务词、数据口径或归因不明确，影响后续知识库准确性。

HTML 不应展示后台 Context Asset 8 类分类、来源锚点、信息状态、风险等级或可复用状态。

### Step 10. Quality Check

生成 `09_quality_check_report.md`，检查事实、策略、数据、风险、来源锚点、内外边界、待确认和待补充事项。

### Step 11. Context Asset Index

生成 `10_context_asset_index.md`，将底稿中的可复用信息沉淀为 8 类上下文资产：

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

每个 Context Asset 必须记录来源锚点、信息状态、Review Priority、适用下游 Skill 和禁止/限制使用条件。

## 6. 核心规则

### R1. 不把所有资料强行产品化

只有资料类型明确为产品培训、新品产品资料、PDP、包装文案、功效报告时，才启用产品知识模块。

### R2. 先完整转述，再结构化判断

保真转述层不应提前删除信息或替品牌下结论。结构化判断必须和来源锚点绑定。

### R3. 缺失信息必须显式标注

资料中没有、AI 也不能合理拟定的信息必须写为 `待补充`。当前资料类型不涉及的字段写为 `不适用`。

### R4. 人工审核只处理异常

AI 可以结构化、提取和初步归纳，但不能替代品牌经理确认策略、预算、主推方向、外发 claim、竞品表达和合规边界。第一阶段的人工介入不应变成逐项确认，而应只处理识别异常和关键不确定点。

### R5. 内外分层

内部策略、预算、竞品打法、供应商要求、投放数据和未确认判断不得进入外发安全内容。

### R5.1 真实测试资料不进入正式 Skill 包

开发测试可以使用真实 PDF，但这些 PDF 和由其生成的真实品牌数据不属于正式 Skill 交付物。写入仓库内置 demo、Skill 文档、公开示例或发布包之前，必须删除或改写：

- 真实品牌名、竞品名、产品线、SKU。
- 价格、预算、销量、曝光、搜索增长、ROI、转化率、渠道激励。
- 渠道、经销商、KA、供应商、负责人和内部执行细节。
- 可反推出客户商业策略的表格、截图和原始 PDF。

正式 examples 应使用匿名化假数据或授权资料。

### R6. 派生 brief 必须回到底稿

第二阶段所有 GEO、PDP、拍摄、种草、客服、销售、复盘等 brief 都必须调用第一阶段底稿中的事实、策略、证据、风险和审核结论。

### R7. 不把上下文资产伪装成品牌确认知识

Context Asset Index 可以记录 AI 结构化判断，但必须标注 `AI 结构化转述，待确认` 或 `AI 初步拟定，待品牌确认`。没有决策背景、素材表现、投放数据或品牌确认时，必须写 `待补充`。

## 7. 人工审核位

默认不要求人工逐项审核。只有以下内容进入人工复核：

- Source Conversion Report 标为低置信度的页面。
- Marketing Semantic Transcript 中标为无法稳定识别的图片、表格、小字或视觉页。
- Risk and Review Items 中属于识别质量、表格错位、漏读、关键业务字段不明确的问题。
- 内置 demo 是否为匿名化样例，未混入真实测试 PDF 的品牌信息和商业数据。

## 8. 输出风格

- 使用结构化 Markdown。
- 标题层级清晰。
- 每页/每 slide 尽量保留来源锚点。
- 尽可能完整转述，不只写摘要。
- 关键判断标注来源和信息状态。
- 不确定内容标注低置信度或待人工复核。
