# 用户指南｜品牌经理如何使用 Brand Context Skills Pack

## 1. 这个 Skill 组先帮你做什么

第一阶段不直接生成完整 GEO brief、产品详情页 brief、拍摄 brief、种草 brief、销售话术或投放复盘。

它先把品牌 Marketing 资料转成 AI 能看懂、可检索、可引用、可审核、可复用的 Markdown 底稿，并沉淀为 Brand Context Assets。资料可以是活动方案、广告公司提案、新品上市方案、销售策略、经销商大会 PPT、抖音爆品打法计划书、爆款视频复盘、投放总结、品牌策略 PPT、产品培训资料、电商详情页或包装文案。

## 2. 先准备原始资料

把已有资料放入 `source/`：

- `campaign_plan/`：活动方案。
- `agency_proposal/`：广告公司提案。
- `launch_plan/`：新品上市方案。
- `sales_strategy/`：销售策略。
- `dealer_conference/`：经销商大会资料。
- `douyin_growth_plan/`：抖音爆品打法计划。
- `video_case_study/`：爆款视频复盘。
- `media_performance_review/`：投放总结。
- `brand_strategy/`：品牌策略资料。
- `product_training/`：产品培训资料。
- `ecommerce_pdp/`：电商详情页资料。
- `claim_reports/`：检测报告或消费者实证。

资料不需要一开始就完美。Skill 会把缺失信息标成 `待补充`。

## 3. 第一阶段默认看哪些文件

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

如果只想先审核重点，可以从本地网页 `review/brand_review.html` 开始。它不要求品牌经理理解后台资产分类，只集中确认两件事：

- 这份 PDF / PPT 输出内容的大概结构、核心观点、核心内容是否和原资料一致。
- AI 没识别清楚或不确定的点，哪些需要你矫正、补充或删除。

## 4. 品牌经理重点审核什么

请重点确认：

- 文件整体概述是否符合原资料。
- 页面 / 章节结构是否有明显漏读或误读。
- 核心观点、核心内容、关键事实是否被转述错。
- `待补充` 和 `待确认` 是否真实反映 AI 没识别出来的内容。
- 需要人工矫正的地方，直接写明页码、错误点和正确说法。

## 5. 后台 Context Asset Index

`10_context_asset_index.md` 是后续 AI 调用资料的关键索引。它会把内容归入 8 类上下文资产：

品牌经理第一轮不需要在 HTML 页面里逐项确认这 8 类资产。它主要服务后续 GEO、PDP、拍摄、种草、销售、客服、复盘等派生 Skill。

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

确认时要看：哪些资产能被 GEO、PDP、拍摄、种草、销售、客服、复盘 Skill 调用；哪些必须先补报告、数据、品牌确认或法务口径。

## 6. 关于真实测试资料

本项目开发时可能会用真实 PDF 做测试，但这些测试资料不等于正式 Skill 示例。正式 Skill 包、公开文档和 `examples/` 目录不应直接包含真实品牌资料、真实 PDF、真实截图或真实商业数据。

如果要把某个测试案例沉淀为正式示例，需要另写一份匿名化假数据版本，删除或改写：

- 真实品牌名、竞品名、产品线、SKU。
- 价格、预算、销量、曝光、搜索增长、渠道激励。
- 渠道、经销商、KA、供应商、负责人和内部执行细节。
- 原始 PDF、页面截图和可反推客户策略的数据表。

## 7. 产品资料怎么处理

产品培训资料、PDP、包装文案、功效报告仍然支持，但它们只是 Marketing 文件的一类。只有资料类型明确是产品相关时，才启用 Product Knowledge、Claim Matrix、SKU Cards、User Language Map 等产品上下文子 Skill。

尤其要避免：

- 单一 SKU 或香型数据泛化到全系列。
- 消费者实证写成医学承诺。
- 身体清洁 claim 延展到脸部彩妆。
- 竞品对比写成攻击性表达。

## 8. 如何进入第二阶段

第一阶段审核完成后，再基于已确认的底稿和 Context Asset Index 派生：

- GEO answer base。
- PDP brief。
- Shooting brief。
- Seeding brief。
- Sales enablement brief。
- Customer service FAQ。
- Campaign recap brief。
- Competitor battlecard。

第二阶段所有 brief 都应该回到已确认资产调用事实、策略、证据和风险边界，不要让 AI 或供应商脱离底稿自由发挥。
