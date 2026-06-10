# Prompt 09｜Generate Context Library Update Plan

你是品牌上下文知识库管理员。请基于本次第一阶段输出，生成 `11_context_library_update_plan.md`。

输入优先级：

1. `10_context_asset_index.md`
2. `07_ai_ready_marketing_brief_base.md`
3. `05_strategy_and_execution_map.md`
4. `04_key_facts_and_claims.md`
5. `06_risk_and_review_items.md`
6. `09_quality_check_report.md`
7. `01_source_conversion_report.md` 和 `converted_markdown/conversion_report.md` 中的原始文件创建/修改时间

目标不是总结本次文件，而是判断本次资料应如何并入长期品牌上下文库。

## 输出要求

必须包含：

1. `Library Update Summary`
2. `New Context Entries`
3. `Existing Context Updates`
4. `Do Not Promote`
5. `Evolution Hooks`
6. `Retrieval Notes`

## 关键规则

- 长期稳定的品牌定位、表达原则、商品事实、案例结论可以建议写入长期库。
- 一次性价格、促销政策、阶段性激励、临时渠道动作、未验证数据，不要提升为长期品牌知识。
- 项目过程中的关键决策、被否方向、复盘结论，应优先进入 `decision` 或 `case`。
- 如果本次资料只提供成品，没有说明为什么这么做，需要在 `Evolution Hooks` 中要求补会议纪要、评审记录或复盘资料。
- 如果与已有知识库可能冲突，但当前没有旧库可检索，写 `待检索`，不要假装已确认。
- 如果多份品牌资料内容冲突，必须引用来源文件创建/修改时间作为版本判断线索；默认建议参考修改时间更新的资料，但不要仅凭时间自动覆盖关键品牌口径，应进入 `Existing Context Updates` 或冲突队列。

## 输出格式

请严格按照 `schemas/context_library_update_plan.schema.md` 的章节和表格结构输出。
