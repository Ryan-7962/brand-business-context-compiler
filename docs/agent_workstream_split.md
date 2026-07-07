# Agent Workstream Split｜30+ Agent 子板块拆分

本文件用于把 `docs/project_goal.md` 的目标拆成可分派的 Agent 任务卡。

第一性原则：不要真的让 30 多个 Agent 同时改同一个仓库。正确用法是先按依赖关系分批推进，每个 Agent 只负责一个独立问题域，交付一个可验证结果，再由主 Agent 合并。

## 分批原则

| 批次 | 目标 | 是否适合并行 |
|---|---|---|
| Batch 0 | 守住目标、边界、验收和隐私 | 可并行审计，不建议并行改代码 |
| Batch 1 | Source-to-Markdown 读取质量 | 可并行研究和测试不同文件类型 |
| Batch 2 | Structured Wiki 编译质量 | 可并行优化不同输出文档 |
| Batch 3 | Review / Report / Work Buddy 使用体验 | 可并行，但需统一最终用户语言 |
| Batch 4 | 验证、benchmark、回归测试 | 可并行跑不同证据 |
| Batch 5 | 后续派生 brief 和真实工作流 | 等第一阶段稳定后再做 |

## 任务卡

### Batch 0｜目标与边界

| Agent | 子板块 | 交付物 | 验收证据 |
|---|---|---|---|
| A01 | Project Goal 守门 | 对照 `docs/project_goal.md` 检查新增功能是否偏离三层架构 | 新增或更新的审计记录 |
| A02 | Ponytail 简化审计 | 找出不必要的抽象、配置、页面和字段 | 删除建议或最小改动 PR |
| A03 | Privacy Boundary 审计 | 检查公开目录不包含真实测试资料信息 | 隐私关键词扫描通过 |
| A04 | Skill Package 入口审计 | 检查 `SKILL.md`、prompt、schema、README 是否一致 | `verify-contract` 通过 |
| A05 | User Workflow 审计 | 从普通 marketer 视角检查最小使用路径 | 一页中文 SOP 或问题清单 |

### Batch 1｜Source-to-Markdown 读取层

| Agent | 子板块 | 交付物 | 验收证据 |
|---|---|---|---|
| A06 | PDF 文本型资料读取 | 验证文本型 PDF 页码、锚点、元数据 | demo contract 通过 |
| A07 | PDF 图片型资料读取 | 抽样检查图片多、小字多页面的低置信度暴露 | `source_quality_report.md` 准确标出风险页 |
| A08 | PPTX 轻量读取 | 验证 slide 文本、slide 编号和限制说明 | PPTX fixture 转写结果 |
| A09 | DOCX / TXT / MD 读取 | 验证文档型资料进入同一 source transcript 流程 | 多格式 fixture 转写结果 |
| A10 | MarkItDown Adapter | 评估 Microsoft MarkItDown 在多格式输入上的收益 | source engine eval 记录 |
| A11 | MinerU Adapter 预留 | 评估 MinerU 对版式、表格、OCR 的增强点 | 不强制依赖的接入建议 |
| A12 | Source Metadata | 保留创建时间、修改时间、转写时间和版本线索 | `00_source_index.md` 与 version report |
| A13 | Page Coverage | 保证总页数、已读页数、缺失页数不被瞎报 | source quality 全页表 |

### Batch 2｜Structured Wiki 编译层

| Agent | 子板块 | 交付物 | 验收证据 |
|---|---|---|---|
| A14 | Source Index | 让 Agent 知道每份资料在哪里、讲什么、读哪份 facts | `outputs/00_source_index.md` |
| A15 | Document Profile | 识别资料类型、目的、目标读者、业务阶段 | `outputs/02_document_profile.md` |
| A16 | Semantic Transcript | 把人看的资料转为 AI 更容易理解的语义稿 | `outputs/03_marketing_semantic_transcript.md` |
| A17 | Key Facts | 抽取只来自来源的关键事实和 claim | `outputs/04_key_facts_and_claims.md` |
| A18 | Strategy Map | 抽取策略、执行动作、渠道、内容和复盘信息 | `outputs/05_strategy_and_execution_map.md` |
| A19 | Risk Review | 暴露缺来源、待确认、OCR 不清、版本冲突 | `outputs/06_risk_and_review_items.md` |
| A20 | AI-ready Brief Base | 生成后续 brief 可复用的底稿，不直接做最终 brief | `outputs/07_ai_ready_marketing_brief_base.md` |
| A21 | Context Asset Index | 让后续任务知道哪些信息可复用 | `outputs/10_context_asset_index.md` |
| A22 | Library Update Plan | 说明本次资料如何进入长期 Wiki | `outputs/11_context_library_update_plan.md` |
| A23 | Dynamic Taxonomy | 让分类由资料语境生成，内置分类只作为建议 | taxonomy 说明或最小规则 |

### Batch 3｜长期库与使用体验

| Agent | 子板块 | 交付物 | 验收证据 |
|---|---|---|---|
| A24 | Library Entries | 生成长期 Markdown 条目 | `brand_context_library/entries/` |
| A25 | Conflict Queue | 多版本或冲突知识进入队列，不自动覆盖 | `review_queue/conflicts.md` |
| A26 | Update Queue | 新资料可能更新旧知识时进入更新队列 | `review_queue/updates.md` |
| A27 | Do Not Promote | 阻止临时执行信息进入长期知识 | `review_queue/do_not_promote.md` |
| A28 | Retrieval Map | 告诉 Agent 不同任务优先读哪些 Wiki 文件 | `retrieval_maps/source_packages.md` |
| A29 | Review HTML | 只展示读了什么、哪些没读清、怎么补 | `review/brand_review.html` |
| A30 | Library HTML | 中文展示知识库地图、索引大纲、待处理事项 | `library_report.html` |
| A31 | Work Buddy Handoff | 给 Work Buddy 一段可复制的任务提示词 | `docs/work_buddy_handoff_guide.md` |

### Batch 4｜验证与证据

| Agent | 子板块 | 交付物 | 验收证据 |
|---|---|---|---|
| A32 | Contract Verification | 检查第一阶段核心产物齐全 | `contract_verification_report.md` |
| A33 | Test Suite | 保证 CLI 和输出约束不回退 | pytest 通过 |
| A34 | Compile Check | 保证 Python 代码可编译 | compileall 通过 |
| A35 | Public Demo | 匿名 demo 能独立跑通 | demo contract 通过 |
| A36 | Private Pack Smoke Test | 私有多文件资料包能跑通，但不进入公开仓库 | 私有 contract 通过，Git 未追踪私有源文件 |
| A37 | A/B Benchmark | 证明 Wiki 链路比直接丢 PDF/PPT 给 Agent 更好 | 同题答案对比表 |
| A38 | Quality Sampling | 抽样核对几页真实资料，估计读取准确度 | 抽样记录和修正建议 |

### Batch 5｜后续派生能力

这些不是第一阶段默认要做的代码，只是后续可分派方向。

| Agent | 子板块 | 交付物 | 验收证据 |
|---|---|---|---|
| A39 | GEO Brief Skill | 基于 Wiki 生成 GEO brief | 与原始资料引用一致 |
| A40 | PDP Brief Skill | 基于 Wiki 生成 PDP brief | 产品 claim 有来源 |
| A41 | Seeding Brief Skill | 基于 Wiki 生成种草 brief | 人群、场景、话术有依据 |
| A42 | Shooting Brief Skill | 基于 Wiki 生成拍摄 brief | 视觉、场景、禁用表达清楚 |
| A43 | Sales Enablement Skill | 基于 Wiki 生成销售话术 | 渠道和经销商信息有来源 |
| A44 | Campaign Recap Skill | 基于 Wiki 生成复盘总结 | 事实、结论、建议分离 |
| A45 | Competitor Analysis Skill | 基于 Wiki 生成竞品分析 | 竞品事实和推断分离 |

## 推荐执行顺序

当前不建议同时启动全部 45 个 Agent。

下一步最小有效并行批次：

1. A02：Ponytail 简化审计，避免继续变臃肿。
2. A07：PDF 图片型资料读取质量，解决真实资料大量需复核的问题。
3. A30：Library HTML 使用体验，确认 marketer 看得懂知识库地图。
4. A37：A/B Benchmark，证明 Wiki 链路比直接丢 PDF/PPT 更好。
5. A38：Quality Sampling，给读取准确度一个真实抽样证据。

这 5 个任务彼此相对独立，能共同回答当前最关键的问题：这个项目是否真的比普通 OCR / 普通总结更有价值。
