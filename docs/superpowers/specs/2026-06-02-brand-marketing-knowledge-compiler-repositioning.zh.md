# Brand Marketing Knowledge Compiler 重定位设计

## 1. 背景

当前项目过度围绕“产品资料 → 产品知识母库”展开。这个方向能处理产品培训资料、PDP、包装文案和功效 claim，但不足以覆盖品牌 Marketing 团队真实会遇到的资料类型。

实际输入可能是：

- 活动方案 PDF。
- 广告公司营销提案。
- 新品上市方案。
- 销售策略 / 经销商大会 PPT。
- 抖音爆品打法计划书。
- 爆款视频营销总结。
- 投放复盘。
- 品牌策略 PPT。
- 产品培训资料。

因此项目应上移为：

```text
Brand Marketing Knowledge Compiler
品牌 Marketing 资料 AI 语义编译器
```

产品资料只是其中一种 document type，不再是默认中心。

## 2. 新定位

本项目的第一阶段目标是：

```text
Marketing PDF / PPT / 长图 / 文档
  ↓
Source-to-Markdown 保真转述
  ↓
Document Profile 文件画像
  ↓
Marketing Semantic Transcript 营销语义转述
  ↓
AI-ready Marketing Brief Base
  ↓
Review Pack 人工审核
```

它不是普通总结工具，也不是产品资料转述工具。核心价值是让 AI 稳定理解品牌营销资料里的事实、策略、动作、证据、风险和待确认点。

## 3. 默认输出结构

第一阶段默认输出应改为：

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
└── 09_quality_check_report.md
```

产品类输出如 Product Knowledge Base、SKU Cards、Claim Matrix 不删除，但降级为 optional module，仅在资料类型是产品培训、新品产品资料、PDP、包装文案、功效报告时启用。

## 4. 通用文档画像

`02_document_profile.md` 应识别：

- 文件类型：活动方案 / 广告提案 / 新品上市 / 销售策略 / 经销商大会 / 投放总结 / 爆款视频复盘 / 产品培训 / 品牌策略 / 其他。
- 文件目的：说服、汇报、复盘、培训、销售推进、预算申请、策略对齐等。
- 目标读者：品牌团队、管理层、销售团队、代理商、经销商、平台小二、内容团队等。
- 时间范围：活动周期、上市周期、投放周期、复盘周期。
- 业务阶段：立项、提案、执行、复盘、培训、招商、渠道推进。
- 资料可信度和限制。

## 5. 营销语义转述

`03_marketing_semantic_transcript.md` 不是简短摘要，而是更完整、更可追溯的语义转述。

要求：

- 尽量保留原资料信息密度。
- 按页码 / slide 保留来源。
- 将视觉页、图表页、策略页转述成 AI 可理解的文字。
- 保留原始策略逻辑和执行逻辑。
- 标注低置信度区域。
- 不提前把资料强行改写成产品项。

## 6. 通用营销结构

`05_strategy_and_execution_map.md` 应根据资料内容抽取：

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

某些资料不具备上述字段时，必须标注 `待补充` 或 `不适用`，不能硬编。

## 7. 风险与审核

`06_risk_and_review_items.md` 应覆盖：

- 事实缺口。
- 策略推断风险。
- 数据和口径风险。
- 竞品攻击风险。
- 平台合规风险。
- 医疗化 / 功效化风险。
- 内部信息外泄风险。
- 需要品牌经理确认的关键判断。

Review HTML Pack 应审核通用营销关键项，而不是只审核 SKU 和 Claim。

## 8. 第一轮实现原则

- 优先改默认 PRD、Skill Spec、README、输出骨架和 prompt bundle。
- 保留示例品牌 demo，但标注为 `product_training` 类型示例。
- 保留 Product Knowledge / Claim Matrix / SKU Cards 作为可选产品模块。
- 不在第一轮做复杂 Web UI、模型 API、企业级 RAG。
- 第一轮先让任意 Marketing PDF/PPT 能被转成 AI-readable Markdown 语义底稿。
