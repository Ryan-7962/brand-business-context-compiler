# PRD｜Brand Marketing Context Compiler

## 1. 一句话定位

Brand Marketing Context Compiler 是一组面向品牌 Marketing 团队的 **AI Skills / Workflow**：它把品牌方原本“给人看的”PDF、PPT、长图和方案文档，编译成 **AI 更容易理解、检索、引用、审核和二次派生的结构化品牌上下文知识库**。

第一阶段不是生成最终营销 brief，而是把资料先转成 AI 能看懂的完整结构化底稿，并进一步归档为品牌上下文资产。后续再由大模型根据具体任务派生 GEO brief、PDP brief、拍摄 brief、种草 brief、销售话术、活动复盘、投放总结、客服 FAQ 等。

## 2. 项目本质

本项目不是普通 PPT/PDF 总结工具，也不是“产品资料转述工具”。

它要解决的是：品牌 Marketing 资料原本是给人看的，常常分散在活动方案、广告公司提案、新品上市方案、销售策略、经销商大会 PPT、抖音爆品打法计划书、爆款视频营销总结、投放总结、品牌策略 PPT、产品培训资料里。AI 直接读取这些资料时，容易漏掉视觉页、误读图表、忽略执行逻辑、混淆策略和事实，或者把内部判断当成外发内容。

因此，本项目要做的不是一个单独的转述工具，而是一组“品牌上下文资产 Skills”：

```text
人类阅读型 Marketing 资料
  ↓
Source-to-Markdown 保真转述
  ↓
Document Profile 文件画像
  ↓
Marketing Semantic Transcript 营销语义转述
  ↓
Key Facts / Claims / Strategy / Execution / Risk
  ↓
AI-ready Marketing Brief Base
  ↓
Context Asset Index
  ↓
Context Library Update Plan
  ↓
Exception Review Queue 异常复核
  ↓
后续派生不同场景 brief
```

第一阶段的核心成品不是下游 brief，也不是产品知识卡，而是一组可供 AI 稳定理解、检索和复用的 **Brand Context Assets**。

更新后的项目目标见 `docs/project_goal.md`。本项目的长期方向是本地优先的 Brand / Business Context Compiler：把临时读文件升级为持续积累、可追溯、可复用的上下文系统。

## 2.1 Skill 组架构

| Skill | 作用 | 第一阶段是否默认启用 |
|---|---|---|
| Source Conversion Skill | 将 PDF / PPT / 长图 / 文档尽量保真转成 Markdown 中间稿 | 是 |
| Marketing Semantic Compiler Skill | 生成文件画像、语义转述、事实、策略、执行和风险底稿 | 是 |
| Context Asset Classifier Skill | 将内容归档为品牌、商品、素材、项目、话术、人设、网络、案例 8 类上下文资产 | 是 |
| Exception Review Queue Skill | 只在识别质量异常、图片/表格/小字无法稳定解析时生成复核队列 | 是 |
| Context Asset Indexer Skill | 输出可被后续派生 Skill 调用的 `10_context_asset_index.md` | 是 |
| Context Library Planner Skill | 输出 `11_context_library_update_plan.md`，说明本次资料如何并入长期品牌知识库 | 是 |
| Product Context Subskills | Product Knowledge、Claim Matrix、SKU Cards、User Language Map | 仅产品类资料启用 |
| Derived Brief Skills | GEO、PDP、拍摄、种草、销售、客服、投放复盘、案例复用 | 第二阶段 |

本项目吸收“Context Moat”的核心思路：模型可以更换，但品牌上下文需要在真实工作流中持续炼制。第一阶段先把资料转成可审核的上下文资产，后续再让这些资产成为派生内容和品牌 Agent 的燃料。

## 3. 支持的资料类型

第一阶段默认支持下列 Marketing 资料类型：

| 类型 | 示例 | 主要抽取重点 |
|---|---|---|
| 活动方案 | 大促活动、品牌 Campaign、节点营销方案 | 活动目标、策略主线、时间线、渠道、物料、风险 |
| 广告公司提案 | 创意提案、年度代理商方案、campaign pitch | 核心洞察、Big Idea、创意方向、执行建议 |
| 新品上市方案 | Launch plan、上市节奏、渠道打法 | 上市目标、人群、卖点、节奏、资源、风险 |
| 销售策略 | 销售推进、经销商大会、渠道策略 PPT | 销售目标、货盘、渠道、激励、组织动作 |
| 抖音爆品打法 | 抖音种草、直播、短视频打法计划 | 人群、内容模型、投放节奏、达人、转化指标 |
| 爆款视频复盘 | 爆款内容总结、素材复盘 | 内容结构、成功因素、数据表现、可复用模式 |
| 投放总结 | 媒体投放复盘、平台投放报告 | 投放目标、预算、素材、数据、复盘结论 |
| 品牌策略 | 年度品牌策略、品牌定位资料 | 定位、消费者洞察、品牌表达、策略边界 |
| 产品培训 | 产品培训稿、PDP、包装、功效报告 | 产品结构、卖点、claim、证据、适用范围 |

产品资料只是其中一种类型。只有资料类型明确为产品相关时，才启用 Product Knowledge、SKU Cards、Claim Matrix 等产品模块。

## 4. 第一阶段目标

第一阶段交付一个轻量可复用的 AI Skill / Workflow repo，跑通：

```text
Marketing 资料
  ↓
Source-to-Markdown 资料转写
  ↓
来源索引和转换报告
  ↓
Document Profile
  ↓
Marketing Semantic Transcript
  ↓
Key Facts and Claims
  ↓
Strategy and Execution Map
  ↓
Risk and Review Items
  ↓
AI-ready Marketing Brief Base
  ↓
Review Pack / Quality Check
  ↓
Context Asset Index
  ↓
Context Library Update Plan
```

第一阶段具体目标：

1. 定义标准输入目录结构，覆盖常见 Marketing 文件类型。
2. 定义 Source-to-Markdown 中间层，尽量保留原资料信息，并用 pymupdf4llm / MarkItDown / MinerU 等候选引擎做小样评估。
3. 定义 Document Profile，识别文件类型、目的、读者和业务阶段。
4. 定义 Marketing Semantic Transcript，不只做摘要，而是更完整的 AI-readable 转述。
5. 定义通用营销结构：事实、claim、策略、执行、指标、复盘、风险、待确认。
6. 提供 CLI 辅助骨架，用于初始化项目、生成模板、校验关键输出。
7. 提供 Exception Review Queue，只让用户处理识别异常，不让用户逐项确认正常资料。
8. 提供 Context Asset Index，将内容归档为可复用上下文资产。
9. 提供 Context Library Update Plan，让每次资料编译都能自然回流到长期品牌知识库。
10. 用本地私有测试样本验证 `product_training`、`brand_strategy` / `channel_strategy` 等资料类型；正式 demo 必须另做匿名化版本，不使用真实测试 PDF。

## 5. 第一阶段默认输出

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

### 5.1 Context Asset Index

`10_context_asset_index.md` 用于把一次资料编译结果沉淀为 8 类上下文资产：

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

### 5.2 产品资料可选模块

当 Document Profile 判断资料类型为产品培训、新品产品资料、PDP、包装文案或功效报告时，可以额外输出：

```text
outputs/<project_slug>/optional_product_module/
├── product_knowledge_base_internal.md
├── product_knowledge_base_public_safe.md
├── claim_matrix.md
├── sku_cards.md
└── user_language_map.md
```

### 5.3 长期品牌上下文库

`11_context_library_update_plan.md` 用于把一次资料编译结果并入长期品牌上下文库。推荐长期目录见 `docs/brand_context_library_architecture.md`：

- `brand/`
- `product/`
- `project/`
- `asset/`
- `language/`
- `persona/`
- `network/`
- `case/`
- `decision/`
- `retrieval_maps/`
- `evolution_log.md`

## 6. 第一阶段成功标准

第一阶段完成后，应满足：

- 任意一组品牌 Marketing PDF/PPT 能先转成尽量保真的 Markdown 中间稿。
- 中间稿保留页码/slide 编号、表格、图片占位、备注、低置信度区域和来源锚点。
- 能生成 source engine readiness / evaluation plan / evaluation results，用同一批低置信度页面评估 pymupdf4llm、Microsoft MarkItDown、MinerU 等候选引擎，而不是凭工具名直接替换默认链路。
- AI 能识别资料类型，而不是把所有资料都套成产品资料。
- AI 能生成完整的 Marketing Semantic Transcript，保留策略逻辑和执行逻辑。
- 关键事实、数据、claim、策略、执行动作、风险和待确认项能被拆清楚。
- 可复用内容能被归档为 Brand Context Assets，并明确可被哪些下游 Skill 调用。
- 每次资料编译都能产出长期知识库更新建议，区分“应写入长期库”“只暂存”“不应提升为长期知识”。
- 绝大多数资料默认自动通过，不要求用户逐项确认；只有低置信度页面、疑似漏读、表格错位、图片文字识别不清、关键业务词无法判断时才进入异常复核队列。
- 不存在资料缺失却被 AI 写成确定事实的问题。
- 内部策略、预算、投放数据、竞品攻击和未确认判断不会混入外发安全内容。
- 仓库内置 demo 和 Skill 发布包不包含真实客户资料；真实测试 PDF 只能保存在本地私有测试目录，若要写进正式样例必须改写为匿名化假数据。
- 换一种 Marketing 资料类型时，可以复用同一套目录、模板、prompt 和校验流程。

## 7. 第一阶段非目标

第一阶段明确不做：

- 企业级权限系统。
- 企业级 RAG 平台。
- 自动 OCR 全流程。
- 自动联网抓竞品资料。
- 自动发布内容。
- 自动 AI 搜索监控。
- 复杂模型 API 接入。
- 多租户 SaaS。
- 完整 GEO brief 自动生成。
- 完整 PDP brief 自动生成。
- 完整拍摄 brief / 种草 brief 自动生成。
- 完整销售话术、投放复盘或活动方案自动生成。

第一阶段可以生成本地静态异常复核 HTML，但它属于识别问题处理辅助，不是复杂 Web UI，也不是逐份文件确认页。

## 8. 核心设计原则

### D1. 先转述，再派生

第一阶段只解决“Marketing 资料 → AI-readable Marketing Semantic Markdown”。下游 GEO、PDP、拍摄、种草、客服、销售、投放、复盘等 brief 都基于底稿派生。

### D2. 先保真转写，再语义编译

Source-to-Markdown 资料转写层必须尽量保留原始资料的信息密度和来源锚点。不要在转写层提前做营销总结或删减。

转写层采用 adapter / evaluation-first 思路。`pymupdf4llm` 是当前 baseline；Microsoft MarkItDown 是多格式 Markdown 转换优先候选；MinerU 是复杂版式、OCR、表格和阅读顺序的高保真候选；DuanYan007/markitdown4j 作为 Java / PaddleOCR / 本地批量部署的后续候选。任何候选引擎都必须先通过小样证据证明能降低漏读和人工复核成本，再进入默认或可选实现。

### D3. 不强行产品化

活动方案、广告提案、投放总结、销售策略和经销商大会 PPT 不应被强行拆成 SKU、香型和产品 claim。产品模块只在产品类资料中启用。

### D4. 结构化不等于编造

AI 可以把资料重新组织成更清晰的结构，但必须区分：

| 状态 | 含义 |
|---|---|
| 已从来源资料提取 | 资料中明确出现，可追溯来源 |
| AI 结构化转述，待确认 | AI 将原资料转成更清楚的结构化表达，需人工复核 |
| AI 初步拟定，待品牌确认 | AI 根据资料合理推导，不能视为品牌最终确认 |
| 待补充 | 资料中没有，AI 也不能合理拟定，必须由品牌方补充 |
| 不适用 | 当前资料类型不涉及该字段 |
| 已品牌确认 | 品牌经理确认后，才能作为最高优先级依据 |

### D5. 人工审核采用异常驱动

本项目不是让 AI 自动替品牌做最终判断，但第一阶段也不应把所有资料都推给品牌经理逐项确认。默认流程是：先尽量提高 PDF / PPT / 图片识别质量，自动生成结构化 Markdown 知识库；只有识别质量异常、关键页缺失、表格错位、图片文字无法判断或关键业务词不确定时，才向用户发起人工复核。

### D6. 派生 brief 必须回到底稿

第二阶段所有派生 brief 都必须调用第一阶段底稿中的事实、策略、证据、风险和审核结论，不允许脱离底稿自由发挥。

### D7. 上下文资产必须可演进

一次资料编译不能假装拥有完整品牌知识。Context Asset Index 必须记录缺失信息、待确认决策、后续资料合并规则和审核要求，让品牌上下文在每次真实工作流中继续累积。

### D8. 真实测试资料不进入正式 Skill 包

开发过程中可使用真实品牌 PDF 做本地测试，但这些材料不是正式 demo。正式 Skill 包只能包含匿名化样例、合成数据或已获授权可公开的资料。若从真实测试 PDF 提炼方法论写进文档，必须删除品牌名、竞品名、SKU、价格、预算、销量、曝光、搜索增长、渠道激励等可识别信息。

## 9. 标准输入目录

```text
<project_dir>/
├── source/
│   ├── campaign_plan/
│   ├── agency_proposal/
│   ├── launch_plan/
│   ├── sales_strategy/
│   ├── dealer_conference/
│   ├── douyin_growth_plan/
│   ├── video_case_study/
│   ├── media_performance_review/
│   ├── brand_strategy/
│   ├── product_training/
│   ├── ecommerce_pdp/
│   ├── claim_reports/
│   ├── packaging_copy/
│   ├── competitor_sources/
│   └── historical_briefs/
├── brand_input/
├── converted_markdown/
├── outputs/
└── review/
```

## 10. Demo 定位

当前测试样本定位：

- `_private_test_runs/private_product_training_sample/`：产品培训资料本地私有测试样本，已加入 `.gitignore`，不属于正式内置 demo。
- `_private_test_runs/private_brand_bpm_sample/`：品牌 BPM 会议资料本地私有测试样本，已加入 `.gitignore`，不属于正式内置 demo；如果未来要放进 `examples/`，必须先改写为匿名化假数据。

后续正式 `examples/` 应补匿名化 demo，例如产品培训、活动方案、投放复盘或爆款视频总结。
