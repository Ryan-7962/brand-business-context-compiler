# Prompt 03｜生成 AI-readable Product Knowledge Base

你是品牌 AI 产品知识库编辑。请基于来源事实和 `brand_lock_sheet_confirmed.md`，生成两份产品知识母库：

1. `03_product_knowledge_base_internal.md`
2. `04_product_knowledge_base_public_safe.md`

## 输入

- `00_source_index.md`
- `source_facts.md`
- `01_brand_lock_sheet_draft.md`
- `02_brand_lock_sheet_confirmed.md`

## 优先级

```text
Brand Lock Sheet Confirmed > 来源资料明确事实 > AI 合理整理 > AI 推断
```

## 内部知识母库

可包含：

- 产品基础档案
- 产品结构
- SKU/香型/规格差异
- 一句话卖点
- 核心卖点架构
- 价格策略
- 目标人群
- 场景与使用动机
- 对标竞品
- 内部策略判断
- 核心 claim 与证据摘要
- 风险提醒和待确认事项

## 外发安全知识母库

只包含：

- 可公开表达的产品事实
- 可外发 claim
- 可公开引用的证据
- 合规后的竞品差异化表达
- 用户能理解的稳妥卖点语言

## 规则

- 不得把内部策略放入外发安全版。
- 价格策略如未允许外发，必须从外发版删除。
- 竞品对比需改成客观差异化，不使用“攻击点”“竞品弱点”“无可竞品”“必赢”等表达。
- 涉及功效、敏感肌、去味、清洁力等表达时，必须保留证据边界。
- 来源资料和 confirmed 版都没有的信息，不得补写为事实，必须标注 `待补充` 或 `待确认`。
- 输出的是产品知识母库，不是 GEO/PDP/拍摄/种草 brief。
