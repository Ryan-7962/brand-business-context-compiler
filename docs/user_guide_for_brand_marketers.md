# 品牌经理 / Work Buddy 使用指南

本指南面向品牌经理和日常使用 Work Buddy / Agent 的同事，用于把一批品牌、Marketing、销售、会议、复盘或产品资料编译成 AI 可读的本地 Markdown Wiki。

第一阶段的目标不是让人逐条审核 AI 读得对不对，也不是直接生成投放 brief 或宣传文案。默认流程是先自动完成读取、转写、索引和入库；人只处理例外，例如漏页、OCR 不清、图片/表格/小字无法识别、版本冲突或资料本身缺信息。

## 0. 推荐使用路径

1. 新建一个项目文件夹，把 PDF / PPTX / DOCX / Markdown / TXT 等资料放入 `source/`。
2. 运行：

```bash
brand-skill run-phase1 <project_dir> --library-dir <brand_context_library_dir>
```

3. 先看这几个结果：

| 文件 | 用途 |
|---|---|
| `outputs/00_source_index.md` | 看本次读了哪些文件、每份文件大概讲什么、转写稿和 source facts 在哪里 |
| `review/brand_review.html` | 只看识别异常、未读清页面和需要补救的问题 |
| `converted_markdown/source_quality_report.md` | 看总页数、复核页、表格数、OCR / 图片 / 小字风险 |
| `brand_context_library/retrieval_maps/source_packages.md` | 告诉 Work Buddy 后续做 GEO / PDP / 种草 / 销售 / 复盘 brief 时优先读什么 |
| `evaluation/direct_vs_skill_benchmark.md` | 对比“直接丢 PDF/PPT”和“先经 Skill 编译”的价值证据 |

如果这些文件能回答“读了哪些资料、每份讲什么、哪些页没读清、后续 Agent 该读哪里”，通常不需要人工逐条打开所有 Markdown。

## 1. 先看来源资料是否完整

请先检查：

- `outputs/00_source_index.md`：资料是否列全，每份文件的大概内容是否明显正确。
- `converted_markdown/conversion_report.md`：总页数、文件创建时间、修改时间和转写时间是否存在。
- `converted_markdown/source_quality_report.md`：哪些页面、图表、表格或小字被标为低置信度。
- `converted_markdown/source_transcripts/`：关键页面是否保留了页码和截图。

如果某些活动方案、广告提案、销售策略、投放复盘、包装文案或检测报告没有进入来源目录，请先补充资料。

## 2. 审核 Document Profile

请重点确认：

- 文件类型是否识别正确。
- 文件目的是否准确。
- 目标读者是否准确。
- 时间范围和业务阶段是否准确。
- 是否被错误理解成产品资料。

如果资料是活动方案，不应被强行拆成 SKU；如果资料是投放总结，不应被强行写成产品知识卡。

## 3. 审核 Marketing Semantic Transcript

请检查：

- 是否漏掉关键页。
- 图表、流程图、策略页是否被正确转述。
- 是否保留来源锚点。
- 是否把原资料中的内部判断写得过于确定。
- 低置信度区域是否需要人工补录。

这一层重点是“转述完整”，不是文案润色。

## 4. 审核 Key Facts and Claims

请重点确认：

- 明确事实是否准确。
- 数据和指标是否保留原始口径。
- 传播主张 / claim 是否有来源。
- 适用范围是否清楚。
- 待补充项是否列全。

产品资料里的 SKU / 香型 / 功效 claim 只在产品类资料中适用。

## 5. 审核 Strategy and Execution Map

请重点确认：

- 业务背景是否准确。
- 核心目标是否准确。
- 核心洞察是否被误读。
- 策略主线是否清楚。
- 渠道、触点、内容资产、时间线是否完整。
- 预算、资源、货盘、组织分工是否需要保密或补充。
- 下一步动作是否来自资料，而不是 AI 自行发挥。

## 6. 审核 Risk and Review Items

请重点看：

- 事实缺口。
- 策略推断风险。
- 数据口径风险。
- 竞品攻击风险。
- 平台合规风险。
- 医疗化 / 功效化风险。
- 内部信息外泄风险。
- 外发前必须确认的内容。

## 7. 审核 Review Pack

`review/brand_review.html` 和 `08_review_pack.md` 会把最需要人工处理的内容集中列出。品牌经理不需要逐个打开所有 Markdown 文件。

静态 HTML Review Pack 是中文轻量确认页，只要求确认：

- PDF / PPT 输出内容的大概结构、核心观点、核心内容是否和原资料一致。
- AI 没识别清楚或不确定的点，哪些需要人工矫正、补充或删除。
- 资料是否缺页、漏页，或总页数与实际文件不一致。

它不展示后台 8 类 Context Asset 分类，也不要求品牌经理逐项审核下游 AI 调用索引。

注意：如果 Review Pack 来自真实测试 PDF，它只属于本地私有测试结果，不应作为正式 Skill 内置 demo 或公开示例发布。

## 8. 后台 Context Asset Index

`10_context_asset_index.md` 是后续 AI 使用这些资料的关键索引。它不是给人看的总结，而是告诉后续 Skill：哪些内容可以调用、哪些必须限制、哪些还缺品牌确认。

如果后续要进入 GEO、PDP、拍摄、种草、销售、客服或复盘派生 Skill，Work Buddy / Agent 应优先读取：

- `outputs/00_source_index.md`
- `outputs/10_context_asset_index.md`
- `outputs/11_context_library_update_plan.md`
- `brand_context_library/retrieval_maps/source_packages.md`

项目负责人或 AI 操作者只在需要时复核：

- 8 类上下文资产是否归类正确：品牌、商品、素材、项目、话术、人设、网络、案例。
- 是否把活动方案、投放复盘、广告提案错误归成产品资料。
- 每个 Context Asset 是否有来源锚点。
- 每个 Context Asset 的信息状态是否正确。
- 高风险 claim、预算、竞品表达、内部策略是否被标为高或中审核优先级。
- 下游 Skill 的使用限制是否足够清楚。
- `待补充` 项是否真实反映当前资料缺口。

确认后的 Context Asset 才适合被 GEO、PDP、拍摄、种草、销售、客服、复盘等后续 Skill 调用。

## 9. 真实测试资料不进入正式 examples

开发过程中可以使用真实品牌 PDF 做本地测试，但正式 Skill 包、README、PRD、prompt 示例、schema 示例和 `examples/` 目录不应直接包含真实测试 PDF 的品牌信息和商业数据。

如果要把真实测试案例沉淀成正式 demo，需要另写匿名化假数据版本，删除或改写真实品牌名、竞品名、SKU、价格、预算、销量、曝光、搜索增长、渠道激励、供应商和内部执行数据。

## 10. 第一阶段完成标准

第一阶段完成时，应至少具备：

- 来源资料已转写并保留页码锚点。
- Document Profile 能说明资料类型、目的和读者。
- Marketing Semantic Transcript 尽量完整转述原资料。
- Key Facts and Claims 可追溯来源。
- Strategy and Execution Map 能表达资料中的策略和执行逻辑。
- Risk and Review Items 列出关键风险和待确认问题。
- Quality Check Report 标明待补充和待复核项。
- Context Asset Index 能说明哪些内容可以被后续 Skill 调用，哪些必须先确认。
- 正式 examples 不包含真实测试 PDF、真实截图、真实品牌信息或精确商业数据。
