# Implementation Roadmap｜Brand Marketing Context Compiler

## Phase 0. Repositioning

目标：确认项目从 Product Knowledge Compiler 上移为 Brand Marketing Context Compiler。

交付：

- README、PRD、Skill Spec 改为品牌营销上下文编译器。
- 产品资料相关输出降级为 optional product module。
- 示例产品训练资料和示例品牌策略资料均仅作为本地私有测试样本，不能作为正式 Skill 内置 demo 发布。
- 正式 `examples/` 只使用匿名化假数据或已授权公开资料。

## Phase 1. Source-to-Markdown Baseline

目标：把 PDF / PPT / 长图 / 文档尽量保真转成 AI 可读 Markdown。

交付：

- `converted_markdown/source_transcripts/`
- `converted_markdown/assets/`
- `converted_markdown/conversion_report.md`
- `docs/source_converter_strategy.md`

成功标准：

- 保留页码 / slide 编号。
- 保留页面截图和低置信度说明。
- 不在转写层提前做营销总结。

## Phase 2. Marketing Semantic Base

目标：生成通用 Marketing 语义底稿。

默认输出：

- `02_document_profile.md`
- `03_marketing_semantic_transcript.md`
- `04_key_facts_and_claims.md`
- `05_strategy_and_execution_map.md`
- `06_risk_and_review_items.md`
- `07_ai_ready_marketing_brief_base.md`
- `08_review_pack.md`
- `09_quality_check_report.md`
- `10_context_asset_index.md`
- `11_context_library_update_plan.md`

成功标准：

- 能识别资料类型。
- 能完整转述策略页、执行页、图表页。
- 能区分事实、AI 结构化转述、AI 推断、待补充和不适用。
- 不把所有资料强行产品化。
- 能将可复用内容归档为品牌、商品、素材、项目、话术、人设、网络、案例 8 类上下文资产。

## Phase 3. Context Asset Index and Exception Review Queue

目标：让系统默认自动入库候选内容，只把识别异常、疑似漏读、表格错位、小字图片识别问题交给用户处理。

交付：

- `08_review_pack.md`
- `10_context_asset_index.md`
- 后续静态 `review/brand_review.html`
- 后续 `review_decisions.json`

成功标准：

- 没有异常的文件显示自动通过。
- 异常页只展示识别问题，不展示后台字段。
- Context Asset 在后台保留来源、状态、风险、下游调用限制。
- 审核结果可被后续流程读取。

## Phase 3.5. Context Library Update Plan

目标：让每次资料编译都能形成长期品牌知识库更新建议。

交付：

- `11_context_library_update_plan.md`
- `docs/brand_context_library_architecture.md`

成功标准：

- 区分写入长期库、暂存待验证、不应提升为长期知识。
- 能把项目过程、被否方向、复盘结论沉淀到 decision / case。
- 能给后续 GEO、PDP、种草、销售、复盘等调用场景提供检索提示。

## Phase 4. Optional Product Module

目标：当资料类型是产品培训 / PDP / 包装 / 功效报告时，启用产品结构化模块。

可选输出：

- Product Knowledge Base。
- Claim Matrix。
- SKU Cards。
- User Language Map。

成功标准：

- 产品 claim 不泛化。
- SKU / 香型 / 产品结构清楚。
- 外发安全边界清楚。

## Phase 5. Derived Briefs

目标：基于 Marketing Semantic Base 派生不同场景 brief。

候选派生：

- GEO brief。
- PDP brief。
- Shooting brief。
- Seeding brief。
- Sales enablement brief。
- Campaign recap brief。
- Customer service FAQ。
- Competitor battlecard。

原则：

- 所有派生 brief 必须回到第一阶段底稿。
- 不允许脱离事实、策略、证据和风险边界自由发挥。
