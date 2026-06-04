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
