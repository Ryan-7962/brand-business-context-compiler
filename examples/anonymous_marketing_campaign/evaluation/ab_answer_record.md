# A/B Answer Record｜Direct Source vs Structured Wiki

本文件用于记录同一批资料、同一组问题下的两组真实 Agent 回答。不要在这里编造评估结果；没有实际跑过就保持 `待粘贴` / `待评分`。

## 运行信息

| 项目 | 记录 |
|---|---|
| 资料包 | anonymous_marketing_campaign |
| 直接读原始资料的 Agent / 模型 | 本地匿名 demo 样例：只读取 `source/campaign_plan/city_refresh_campaign.md` |
| 读取 Structured Wiki 的 Agent / 模型 | 本地匿名 demo 样例：读取 `outputs/`、`source_facts/`、`retrieval_maps/` |
| 评分人 | Codex local verification |
| 最终判断 | Skill 更好，但仅作为匿名 demo 样例；真实品牌资料仍需另跑 A/B |

## 同题答案记录

| 问题 | 直接读原始资料答案摘要 | Structured Wiki 答案摘要 | 胜出方 | 证据 |
|---|---|---|---|---|
| 这个资料大概讲什么？ | 一份匿名夏季活动方案，包含项目背景、目标、人群、策略主线、触点规划和审核要求。 | 同样能说明资料主题，并能定位到 `S001#page=1-6`、`outputs/00_source_index.md` 和 source facts。 | Structured Wiki | Raw source；`outputs/00_source_index.md`；`converted_markdown/source_facts/S001_campaign_plan_source_facts.md` |
| 哪些内容被完整转写了？ | 可人工读到 6 个 slide 的正文，但需要人工自己判断覆盖是否完整。 | 明确记录页/slide 范围为 1-6，并在 source facts 中拆成 14 条来源事实。 | Structured Wiki | `outputs/00_source_index.md`；source facts `SF001-001` 至 `SF001-014` |
| 哪些页面/图片/表格/小字识别不可靠？ | raw source 是 Markdown 文本，直接读时只能主观判断没有明显图片、表格、小字问题。 | `source_quality_report.md` 明确总页数 6、需要复核页数 0；无明显低置信度。 | Structured Wiki | `converted_markdown/source_quality_report.md` |
| 哪些事实来自原文，来源在哪里？ | 能从原文段落找到，但没有机器可检索的事实 ID。 | 每条事实有 `Fact ID` 和 `Source Anchor`，例如目标人群在 `SF001-006 / S001#page=3`。 | Structured Wiki | `converted_markdown/source_facts/S001_campaign_plan_source_facts.md` |
| 哪些内容可以长期进入品牌知识库？ | 可人工判断目标、策略、触点和审核边界可复用。 | 已生成 Context Asset 和长期库候选条目，能看到资产 ID、场景和来源锚点。 | Structured Wiki | `outputs/10_context_asset_index.md`；`brand_context_library/project/*.md` |
| 哪些内容只是临时政策、阶段判断或敏感信息，不能入库？ | raw source 提到预算、人员分工、渠道合作名单暂未提供，但需要人工自己抽出风险。 | 风险和不入库边界被结构化保留：缺预算/人员/渠道名单，功效表达需证据，竞品表达只用品类层描述。 | Structured Wiki | `SF001-012` 至 `SF001-014`；`outputs/06_risk_and_review_items.md`；`review_queue/do_not_promote.md` |
| 如果未来写 GEO / PDP / 种草 / 销售 / 复盘 brief，应该调用哪些知识资产？ | raw source 只说后续可用于 GEO / PDP / 种草 / 销售 brief，但没有读取顺序。 | retrieval map 明确后续任务先读 `outputs/10_context_asset_index.md`，精读 source facts，必要时回看 transcript。 | Structured Wiki | `brand_context_library/retrieval_maps/source_packages.md` |

## 评分维度

| 维度 | 直接读原始资料 | Structured Wiki | 胜出方 | 证据 |
|---|---|---|---|---|
| 覆盖率 | 覆盖 6 个 slide，但没有自动页数/事实覆盖证据 | 记录页/slide 1-6，生成 14 条 source facts | Structured Wiki | Source Index + source facts |
| 准确率 | 匿名 demo 文本简单，直接读也准确 | 同样准确，并保留“资料未提供/待补充”边界 | 差异不明显 | Raw source + source facts |
| 来源追溯 | 只能回到原文段落 | 可回到 Fact ID、Source Anchor、transcript、source index | Structured Wiki | `SF001-*`；`S001#page=*` |
| 低置信度暴露 | 需要人工判断 | 自动记录总页数、复核页数和低置信度说明 | Structured Wiki | `source_quality_report.md` |
| 多文件版本冲突 | 本 demo 只有单文件，无法比较 | 本 demo 只有单文件，version report 记录无疑似多版本 | 差异不明显 | `source_version_report.md` |
| 长期知识沉淀 | 需要人工手动整理 | 已生成 Context Asset、Library Update Plan 和长期库条目 | Structured Wiki | `outputs/10_context_asset_index.md`；`outputs/11_context_library_update_plan.md`；library entries |
| 后续 brief 复用 | 只能从原文中自己找段落 | retrieval map 给出优先读取、精读和回看原文路径 | Structured Wiki | `retrieval_maps/source_packages.md` |
| 人工修正成本 | 需要人工判断覆盖、事实、风险和后续读取顺序 | 只需检查 review / quality 标记的异常；本 demo 无明显异常 | Structured Wiki | `review/brand_review.html`；`source_quality_report.md` |

## 本样例限制

- 这是匿名 Markdown demo，不是复杂 PDF / PPT / 图片型资料。
- 这份记录证明 A/B 评估格式可执行，但不证明真实品牌资料已经达到 90% 准确。
- 下一步仍需对 `_private_test_runs/` 中真实资料包跑同题 A/B，并只在私有目录保留真实内容。
