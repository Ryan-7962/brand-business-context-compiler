# Prompt Bundle｜Phase 1 Brand Context Skills Pack

按以下顺序执行第一阶段品牌上下文资产编译提示词。第二阶段派生 brief prompt 不纳入本 bundle。

<!-- 00_source_to_markdown_conversion.md -->
# Prompt 00｜Source-to-Markdown 资料保真转写

你是资料转写工程师。请把原始 PDF/PPT/PPTX/详情页/包装文案等资料，尽量保真地转成 AI 可读取的中间 Markdown。

## 目标

本步骤只负责保留信息，不做营销总结，不改写 claim，不生成 brief。

## 必须保留

1. 原始文件名。
2. 页码 / slide 编号。
3. 页标题 / slide 标题。
4. 原文正文。
5. 表格结构。
6. 图片、图表、包装图、详情页视觉区占位。
7. speaker notes / 备注。
8. 页脚、角标、小字、脚注。
9. 低置信度区域。
10. 待人工复核位置。

## 输出结构

```markdown
# Source Transcript｜<原始文件名>

## Source Metadata
- 原始文件：
- 文件类型：
- 转写方式：文本解析 / OCR / 人工摘录 / 截图说明
- 转写日期：
- 低置信度说明：

## Page / Slide 1｜<标题>
- Source Anchor：<source_file>#page=<n> 或 <source_file>#slide=<n>

### Text

### Tables

### Images / Charts
| Asset ID | 位置 | 客观说明 | 文件路径/截图编号 | 待复核 |
|---|---|---|---|---|

### Notes / Footnotes / Small Print

### Low Confidence / Need Review
```

## 规则

- 不删除看似“不重要”的角标、小字、页脚和备注。
- 表格优先保留为 Markdown 表格。
- 复杂表格无法可靠还原时，保留原始文本块并标注 `表格结构待人工复核`。
- 图片和图表即使无法识别，也必须保留占位和客观说明。
- 不把广告语改写成 claim。
- 不把单页数据扩展到全系列。
- 不判断可外发性，只记录原始信息和来源锚点。

<!-- 01_generate_document_profile.md -->
# Prompt 01｜生成 Document Profile

请基于 `converted_markdown/source_transcripts/` 和 `00_source_index.md`，生成 `02_document_profile.md`。

目标不是总结内容，而是识别这份 Marketing 资料是什么、给谁看、为了解决什么业务问题。

必须包含：

- 文件类型：活动方案 / 广告提案 / 新品上市 / 销售策略 / 经销商大会 / 投放总结 / 爆款视频复盘 / 产品培训 / 品牌策略 / 其他。
- 文件目的。
- 目标读者。
- 时间范围。
- 业务阶段。
- 主要内容模块。
- 可复用价值。
- 资料可信度。
- 解析限制。
- 待人工确认问题。

所有判断必须标注信息状态：`已从来源资料提取` / `AI 结构化转述，待确认` / `AI 初步拟定，待品牌确认` / `待补充` / `不适用`。

<!-- 02_generate_marketing_semantic_transcript.md -->
# Prompt 02｜生成 Marketing Semantic Transcript

请基于 Source Transcript 生成 `03_marketing_semantic_transcript.md`。

这不是摘要。请尽可能完整地把原始 PDF / PPT 中的内容转述为 AI 可理解的结构化 Markdown，并保留页码 / slide 来源锚点。

要求：

- 按页码或 slide 顺序组织。
- 保留原资料的信息密度。
- 对视觉页、图表页、流程图、策略图、时间线进行文字化说明。
- 对无法确定的信息标注 `低置信度，待人工复核`。
- 不要把活动方案、销售策略、投放总结强行改写成产品 SKU 结构。
- 不要生成下游 brief。

<!-- 03_generate_key_facts_and_claims.md -->
# Prompt 03｜生成 Key Facts and Claims

请基于 `03_marketing_semantic_transcript.md` 生成 `04_key_facts_and_claims.md`。

抽取：

- 明确事实。
- 数据和指标。
- 业务判断。
- 传播主张 / claim。
- 证据来源。
- 适用范围。
- 待确认事项。

规则：

- 原资料明确出现的信息标注 `已从来源资料提取`。
- AI 重新组织的表达标注 `AI 结构化转述，待确认`。
- AI 推导出的判断标注 `AI 初步拟定，待品牌确认`。
- 缺失信息写 `待补充`。
- 当前资料类型不涉及写 `不适用`。

<!-- 04_generate_strategy_and_execution_map.md -->
# Prompt 04｜生成 Strategy and Execution Map

请基于前序输出生成 `05_strategy_and_execution_map.md`。

根据资料内容抽取：

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

不要硬填不存在的信息。没有则写 `待补充` 或 `不适用`。

<!-- 05_generate_risk_and_review_items.md -->
# Prompt 05｜生成 Risk and Review Items

请生成 `06_risk_and_review_items.md`。

识别：

- 事实缺口。
- 策略推断风险。
- 数据和口径风险。
- 竞品攻击风险。
- 平台合规风险。
- 医疗化 / 功效化风险。
- 内部信息外泄风险。
- 需要品牌经理确认的关键判断。

每条风险需包含：风险说明、来源锚点、风险等级、建议处理、是否影响外发。

<!-- 06_generate_ai_ready_marketing_brief_base.md -->
# Prompt 06｜生成 AI-ready Marketing Brief Base

请生成 `07_ai_ready_marketing_brief_base.md`。

这是给后续大模型调用的营销语义底稿，不是最终 brief。

必须包含：

- 文件画像摘要。
- 可复用事实。
- 可复用策略。
- 可复用执行信息。
- 可复用数据。
- 可复用内容资产。
- 风险和禁用表达。
- 待补充和待确认项。
- 后续可派生的 brief 类型。

输出应让 AI 能基于本文件继续生成 GEO / PDP / 拍摄 / 种草 / 销售 / 复盘等 brief。

<!-- 07_generate_review_pack.md -->
# Prompt 07｜生成 Review Pack

请生成 `08_review_pack.md`。

目标是帮助品牌经理集中审核关键判断，而不是让用户逐个打开所有 Markdown 文件。

必须包含：

- 需要优先确认的 10 个问题。
- 高风险 claim / 数据 / 策略判断。
- 待补充资料清单。
- 可外发前必须确认的内容。
- 不适用项说明。
- 建议进入 Review HTML 的审核项。

<!-- 08_generate_context_asset_index.md -->
# Prompt 08｜Generate Context Asset Index

## 任务

基于 `00_source_index.md`、`01_source_conversion_report.md`、`02_document_profile.md`、`03_marketing_semantic_transcript.md`、`04_key_facts_and_claims.md`、`05_strategy_and_execution_map.md`、`06_risk_and_review_items.md`、`07_ai_ready_marketing_brief_base.md` 和 `09_quality_check_report.md`，生成 `10_context_asset_index.md`。

这个文件不是普通摘要，而是把本次资料中可复用的品牌上下文沉淀为 Context Assets，方便后续不同 Skill 调用，例如 GEO brief、PDP brief、拍摄 brief、种草 brief、销售 brief、客服 FAQ、投放复盘、案例复用等。

## 上下文类型

请按以下 8 类识别和归档：

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

## 输出要求

1. 不要把所有内容强行归入商品上下文。活动方案、投放复盘、广告提案等应优先识别项目、素材、话术、案例、网络上下文。
2. 每个 Context Asset 必须包含来源锚点，如 `S001#page=3`。如果来自多个页面，用逗号分隔。
3. 每个 Context Asset 必须标注信息状态：`已从来源资料提取`、`AI 结构化转述，待确认`、`AI 初步拟定，待品牌确认`、`待补充`、`不适用` 或 `已品牌确认`。
4. 如果资料没有决策背景、品牌确认结论、预算口径、投放数据、复盘原因、素材表现等，不要补写成确定事实，标注 `待补充`。
5. 对高风险 claim、竞品表达、内部策略、预算、平台规则、疗效/功效相关内容，必须在 Review Priority 中标为 `高` 或 `中`。
6. 为每个资产标出可被哪些下游 Skill 调用，但不要在本步骤生成下游 brief。

## 输出结构

请严格按以下结构输出：

```markdown
# Context Asset Index

## 1. Context Type Coverage

| 上下文类型 | 覆盖程度 | 本资料包含的内容 | 缺失/待补充 | 信息状态 |
|---|---|---|---|---|

## 2. Reusable Context Assets

| Asset ID | 上下文类型 | 可复用资产 | 适用场景 | 来源锚点 | 信息状态 | Review Priority |
|---|---|---|---|---|---|---|

## 3. Decision Rationale and Missing Context

| Context ID | 需要理解的决策/判断 | 当前资料能说明什么 | 缺失内容 | 建议品牌方确认 |
|---|---|---|---|---|

## 4. Downstream Skill Reuse Map

| 下游 Skill | 可调用资产 | 禁止/限制使用 | 需要先确认 |
|---|---|---|---|

## 5. Context Evolution Hooks

| 后续新增资料类型 | 应补充的上下文 | 合并规则 | 审核要求 |
|---|---|---|---|
```

<!-- 11_quality_check.md -->
# Prompt 11｜质量检查

你是品牌 Marketing 资料语义底稿质检员。请检查第一阶段输出是否满足“Marketing 资料 → AI-readable Marketing Semantic Markdown”的要求。

请生成 `09_quality_check_report.md`。

## 检查项

1. 是否存在 `00_source_index.md`。
2. 是否存在 `01_source_conversion_report.md`。
3. 是否存在 `02_document_profile.md`。
4. 是否存在 `03_marketing_semantic_transcript.md`。
5. 是否存在 `04_key_facts_and_claims.md`。
6. 是否存在 `05_strategy_and_execution_map.md`。
7. 是否存在 `06_risk_and_review_items.md`。
8. 是否存在 `07_ai_ready_marketing_brief_base.md`。
9. 是否存在 `08_review_pack.md`。
10. Document Profile 是否识别资料类型、文件目的、目标读者和业务阶段。
11. Marketing Semantic Transcript 是否尽量完整转述，而不是只做短摘要。
12. 关键事实、数据、claim、策略和执行动作是否有来源锚点。
13. 资料缺失信息是否标注 `待补充` 或 `不适用`。
14. AI 推断是否标注 `AI 初步拟定，待品牌确认`。
15. 是否存在把非产品资料强行拆成 SKU / 香型 / 产品项的问题。
16. 内部策略、预算、竞品攻击、平台风险、医疗化/功效化风险是否进入审核项。
17. 后续派生 brief 是否能回到本底稿调用事实、策略、证据和风险。

## 输出格式

```markdown
# Quality Check Report｜<资料名>

## 总体结论

通过 / 有条件通过 / 不通过。

## 关键问题

| 问题 | 位置 | 风险 | 建议处理 |
|---|---|---|---|

## 文件完整性检查

| 文件 | 是否存在 | 主要问题 |
|---|---|---|

## 资料类型理解检查

## 转述完整性检查

## 策略与执行结构检查

## 风险与审核项检查

## 待补充资料

## 下一步建议
```
