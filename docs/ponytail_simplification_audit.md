# Ponytail 简化审计｜A02

审计日期：2026-07-07  
审计范围：`docs/project_goal.md`、`docs/agent_workstream_split.md`、当前 `README.md`、当前仓库文件清单。  
成功标准：第一阶段只服务 `Raw Sources -> Compiler Skill -> Structured Wiki` 闭环；不能直接证明 Wiki 更可靠、更可追溯、更少漏读的内容，默认延后或删除。

## 总判断

当前方向是对的，但第一阶段表面积偏大：README 同时写了核心闭环、候选 source engine、私有 IMA 导入、产品资料模块、派生 brief、benchmark、HTML 报告和 45 个 Agent 任务。按 Ponytail 标准，第一阶段应先收成一条能跑通真实私有资料包的主路径：

```text
source/
-> run-phase1
-> converted_markdown/
-> outputs/00-11
-> brand_context_library/
-> review/brand_review.html
-> contract_verification_report.md
```

其余能力只在真实验收暴露缺口后补。

## 保留

| 项目 | 原因 | 验证方式 |
|---|---|---|
| `run-phase1` 作为唯一推荐入口 | README 已经给出一条命令跑完整闭环，这符合最小使用路径；分步命令保留给调试即可。 | 对匿名 demo 和 1 个私有资料包运行 `brand-skill run-phase1 ...`，确认能生成 `contract_verification_report.md`。 |
| Source-to-Markdown 基础转换、页码 / slide 锚点、创建 / 修改 / 转写时间 | 这是第一阶段区别于普通总结的核心证据，不能删。 | 抽查 `converted_markdown/source_transcripts/` 和 `conversion_report.md` 是否能追溯到源文件与页 / slide。 |
| `source_quality_report.md` 和异常复核页 | 项目目标明确：人只处理例外，不逐条确认事实表；质量报告和 review HTML 是这个边界的落点。 | 检查报告能回答：读了哪些文件、哪些页没读清、建议怎么补。 |
| `source_version_report.md`、冲突 / 更新队列 | 多版本品牌资料是高频真实问题；不自动覆盖旧知识是必要约束。 | 准备同主题两个版本样本，确认进入 `review_queue/updates.md` 或冲突队列。 |
| `outputs/00_source_index.md`、`10_context_asset_index.md`、`11_context_library_update_plan.md` | 这三份文件直接决定后续 Agent 是否少漏读、少重复读、知道先读什么。 | 让一个后续任务只读这三份文件，能定位应读取的原始转写和长期库条目。 |
| `verify-contract --write-report` / `demo-contract` | 需要一个本地门禁证明第一阶段没退化；这是最小验证，不是额外产品功能。 | 每轮开发后生成或更新 `contract_verification_report.md`。 |
| 匿名 demo 与隐私扫描规则 | 真实品牌资料不能进入公开 examples；这个边界必须保留。 | `git status --short` 不出现 `_private_test_runs/` 真实资料；必要时跑隐私关键词扫描。 |

## 延后

| 项目 | 延后原因 | 何时再做 | 验证方式 |
|---|---|---|---|
| Derived Brief Skills：GEO / PDP / 拍摄 / 种草 / 销售 / 客服 / 复盘 / 竞品 | `docs/project_goal.md` 明确这些是 Layer 3，不属于第一阶段默认开发重点。当前只需要证明 Wiki 可供它们调用。 | 当 1-2 个真实资料包的 Wiki 闭环稳定后，再选一个最高频 brief 做端到端派生。 | 派生 brief 中每个关键结论能反查 `source_packages.md`、asset index 和来源锚点。 |
| 产品资料可选模块：Brand Lock、SKU Cards、Claim Matrix、User Language Map | README 已声明这些只是产品资料模块，不是全局默认输出；保留在第一阶段会把营销资料强行产品化。 | 遇到真实产品培训 / claim 审核资料包，并且用户明确要产品模块。 | 只对产品资料样本启用，非产品营销资料不生成这些文件。 |
| MarkItDown / MinerU 深度评估 | 当前下一步是私有资料包瘦身验收；先用 baseline 暴露真实读取缺口，再决定是否换引擎。 | `source_quality_report.md` 连续暴露 baseline 读不清的表格、图片、小字或扫描件。 | 对最多 5 页问题页面做小样对比，不全量接入。 |
| `import-ima-media` 私有导入命令 | 它解决的是特定来源接入，不是编译器主闭环；手动放入 `source/` 已能覆盖第一阶段验收。 | 当真实工作流中 IMA 是主要来源，且手动导入成本成为瓶颈。 | 导入后仍只写 `_private_test_runs/`，manifest 可追溯，公开 demo 不含真实信息。 |
| `build-value-benchmark` 的完整评分体系 | “证明 Wiki 比直接读 PDF/PPT 好”是必要目标，但完整评分表、两套提示词和多维评分容易抢走主线。 | 核心闭环跑通后，用 1 个真实包做轻量 A/B 证据。 | 先只保留 3-5 个固定问题：覆盖率、来源追溯、低置信度暴露、版本冲突、后续调用路径。 |
| Rich Library HTML：搜索、筛选、条目详情交互 | `library_report.html` 需要中文可读，但第一阶段不需要做成小型 Web App。 | marketer 看静态概览页仍找不到条目或待处理事项时。 | 先验证一页静态报告能回答“有哪些知识、哪些待处理、后续读哪份”。 |
| Dynamic Taxonomy | 动态分类会增加规则与调试面；第一阶段用内置分类建议已经够。 | 多个真实资料包出现固定分类无法表达的重复问题。 | 新分类必须改善 `10_context_asset_index.md` 的后续调用准确性。 |
| 45 个 Agent 任务卡 | 分工文档有助于并行，但不应驱动仓库继续铺功能。 | 每次只拿当前 3-5 个最小任务执行。 | 任务完成标准落到一个文件、一条命令或一个真实验收问题。 |

## 建议删除或从第一阶段文档移出

| 项目 | 建议 | 原因 | 验证方式 |
|---|---|---|---|
| README 中 `outputs/derived_briefs/` 默认目录展示 | 从第一阶段默认产物移出，放到“第二阶段示例”或删除。 | 它会暗示第一阶段已经要产出 GEO / PDP / shooting / seeding brief，偏离 `project_goal.md`。 | README 的第一阶段产物只剩 `outputs/00-11`、review、library、verification。 |
| 派生 brief prompts / schemas：`generate_geo_pack`、`generate_influencer_brief`、`generate_customer_service_faq`、`generate_competitor_battlecard`、`geo_activation_pack.schema.md` | 从第一阶段 Skill 发布包移出或标记为 archived / phase2。 | 这些是 Layer 3，当前保留在主 prompt/schema 目录会扩大维护面。 | `verify-contract` 不要求这些文件存在；第一阶段 demo 不引用它们。 |
| 单独的 MinerU 命令组：`check-mineru`、`plan-mineru-eval`、`scaffold-mineru-eval-results` | 删除独立命令面，合并到通用 `check-source-engines` / `plan-source-engine-eval`。 | README 已有通用 source engine eval；再给 MinerU 一套命令是重复抽象。 | README 只保留“MinerU 是候选引擎，由通用评估计划覆盖”。 |
| README 中 DuanYan007/markitdown4j、Java、本地 OCR、PaddleOCR 方向描述 | 从当前 README 删除。 | 这是工具研究路线，不是第一阶段用户闭环；会把注意力带到转换器选型。 | README 的 source engine 说明只保留当前可用 baseline 和可选 MarkItDown / MinerU 小样评估。 |
| `check-brand-lock` / `check-claim-matrix` 出现在主 CLI 第一版 | 从主命令列表移到产品资料可选模块。 | 第一阶段不是产品 claim 系统；主命令越多，越难判断最小路径。 | 新用户只看到 `run-phase1`、少量调试命令和 contract 验证。 |
| `08_review_pack.md` 作为默认 `outputs/` 文件 | 如果 review HTML 已覆盖异常复核，建议删除或降级为内部调试产物。 | 项目目标明确不让用户逐条确认后台事实；额外 review pack 容易回到全量审核。 | 使用者只看 `review/brand_review.html` 仍能处理异常；后台质量信息留在质量报告。 |
| `source_engine_eval_results.md` 脚手架默认出现在匿名 demo | 建议从默认 demo 输出移除，只有执行评估计划时生成。 | 没有真实小样证据的 eval results 容易制造“已经评估过”的错觉。 | demo contract 不依赖该文件；评估命令运行后才出现。 |

## 最小下一步

1. 先不删代码，先把 README 的“第一阶段默认路径”收窄：默认只展示 `run-phase1`、核心 `outputs/00-11`、review HTML、library、verification。
2. 用 1 个真实私有资料包跑瘦身验收，记录真正卡住的是读取质量、索引可读性还是后续调用路径。
3. 只修复真实验收暴露出的最小缺口；如果没有证据，派生 brief、产品模块、引擎深度评估继续延后。

