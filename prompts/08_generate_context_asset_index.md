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
