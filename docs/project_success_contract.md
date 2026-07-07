# Project Success Contract

本文件定义 Brand Marketing Context Compiler 后续迭代的执行准则。每轮开发前，Codex 应用本文件判断下一步是否值得做；每轮结束时，Codex 应用本文件检查结果是否可验证、是否破坏限制条件。

## 执行护栏：第一性原则

每轮开发前先做最小必要性审查：

- 这个改动是否直接推进 Source-to-Markdown、结构化知识库、本地报告或验收证据？
- 现有代码、文档、测试或标准库是否已经能解决，不需要新增功能？
- 能否用更少文件、更少代码、更少 UI 字段完成同一个目标？
- 如果没有可验证证据，先补证据，不先堆功能。
- 如果只是“以后可能有用”，本轮跳过。

## ＜你希望 Codex 最终完成的目标>

Codex 最终应把本项目推进为一个本地优先的 Brand / Business Context Compiler：

- 能读取品牌、营销、产品、销售、渠道、会议、复盘等人类资料。
- 能把本地文件夹、用户明确授权的私有知识库导出文件和 ima 等私有资料源作为输入，但真实资料只进入本地私有测试区。
- 能把 PDF / PPT / 长图 / 文档尽量保真地转成 AI-readable Markdown。
- 能把 pymupdf4llm、Microsoft MarkItDown、MinerU 等 source conversion 候选放进同一套本地评估框架，先用证据判断是否值得接入。
- 能生成文件画像、语义转述、关键事实、策略执行结构、风险与待确认项。
- 能把可长期复用的信息沉淀为本地结构化知识库。
- 能维护冲突、旧知识更新、不应入库内容和检索提示。
- 能生成 `library_report.html`，让使用者通过 Brand Context Map、搜索、筛选和详情查看知识库结构。
- 能为后续 GEO、PDP、种草、拍摄、销售、客服、投放复盘、案例复用等 brief 提供可靠上下文。

第一阶段的目标不是做完整平台，而是跑通并验证这个闭环：

```text
原始资料
→ 高保真转写
→ AI-readable 结构化 MD
→ Context Asset Index
→ Context Library Update Plan
→ 本地知识库写入
→ 冲突 / 待更新 / 不入库队列
→ Brand Context Map 浏览
→ 后续 brief 可调用
```

## ＜具体可验证的证据>

只有出现以下证据时，才认为一轮迭代有效：

- CLI 能从示例项目生成或更新真实文件，而不是只在对话中描述方案。
- `SKILL.md` 能作为 AI Agent 的技能入口，明确第一阶段边界、默认 CLI 工作流、source engine 评估、人工复核范围、隐私边界和验收命令。
- `prompt_bundle.md`、`prompts/` 和 `schemas/` 能构成第一阶段 Prompt / Schema 包，至少覆盖 Source-to-Markdown、Document Profile、Marketing Semantic Transcript、Key Facts、Strategy、Risk、Review Pack、Context Asset Index、Context Library Update Plan 和 Quality Check。
- `brand-skill run-phase1 <project_dir>` 能从 `source/` 原始资料跑到 `contract_verification_report.md`，避免使用者手动串联步骤时漏掉 source facts、review page 或 benchmark。
- `converted_markdown/` 中有来源转写、页码 / 截图 / 低置信度说明、识别质量摘要和文件创建 / 修改时间。
- `converted_markdown/source_quality_report.md` 能告诉使用者哪些页面需要 OCR、MinerU、MarkItDown 或人工复核，并必须包含 `表格数`，避免表格页被误判为无需复核。
- `converted_markdown/source_version_report.md` 能告诉使用者哪些资料疑似同主题多版本、最新修改时间线索是什么；常见 `v2` / `final` / 日期 / hash 后缀应被归一化为版本线索，但仍明确不自动覆盖旧知识。
- `converted_markdown/source_engine_readiness_report.md` 能告诉使用者当前本机是否具备 pymupdf4llm baseline、MarkItDown 和 MinerU 的评估条件，并明确候选引擎只属于 Source-to-Markdown 层。
- `converted_markdown/source_engine_eval_plan.md` 能从 source quality report 中挑选最多 5 个高价值小样，对比 pymupdf4llm、MarkItDown、MinerU 在文字覆盖率、页码 / slide 锚点、表格结构、图片 / 图表 / 小字、阅读顺序、Markdown 可读性、部署复杂度和隐私风险上的差异。
- `converted_markdown/source_engine_eval_results.md` 能记录候选引擎小样级观察、是否调整默认链路和隐私边界；在没有真实小样证据前必须保持“待判断 / 否，待证据”，不能把候选引擎写成默认替代。
- MinerU 独立 readiness / eval 文件只作为可选调试证据，不作为第一阶段默认验收前置条件。真实验收优先看通用 `source_engine_*` 评估链路；只有连续出现图片、表格、小字或扫描件读取缺口时，再用 MinerU 小样证明是否值得增强。
- 项目价值不能只用“单次 PDF 总结是否顺口”判断。必须能用同一批资料对比“直接把 PDF/PPT 发给 AI”和“先经本 Skill 转写、抽 facts、编译、入库后再回答”的差异，并在覆盖率、来源追溯、多文件版本冲突、长期复用和人工修正成本上拿出证据。
- `evaluation/direct_vs_skill_benchmark.md` 能把上述对比落实成固定问题集、当前 Skill 证据清单、两套可复制 A/B 评估提示词、答案记录模板和评分表，避免项目价值停留在主观判断。
- 当资料来自 ima 或其他外部知识库时，`source/source_manifest.json` 能保留来源平台、知识库、路径、media id 等追溯线索，并写入 transcript / conversion report。
- ima 私有资料导入必须通过 `_private_test_runs/` 私有目录验证，导入后能继续跑 `convert-source` 和 `build-source-facts`。
- `converted_markdown/source_facts/` 能继承 Source Anchor，并尽量保留章节上下文、表格行和低置信度说明；事实候选仍不得冒充品牌确认。
- `outputs/` 中有文件画像、语义转述、关键事实、策略结构、风险项、Context Asset Index 和 Context Library Update Plan。
- `compile-outputs` 能在不调用模型的情况下，从 source facts / transcripts / quality reports 生成 00-11 结构化输出初稿，并把表格行保留为“表格结构信息”和 `structured_table` 资产。
- `brand_context_library/` 中实际生成 Markdown 条目。
- `review_queue/conflicts.md` 能记录疑似重复或冲突条目。
- `review_queue/updates.md` 能记录可能需要更新旧知识的条目。
- `review_queue/do_not_promote.md` 能记录不应提升为长期知识的内容。
- `retrieval_maps/source_packages.md` 能记录未来适合调用资料的任务场景。
- `library_report.html` 能展示知识地图、搜索、分类筛选、状态筛选、条目详情和中文待处理事项；多版本复核应显示建议动作和最新修改时间线索，不直接暴露后台报告文件名。
- `verify-contract` 能拦截报告页暴露后台报告文件名、缺少版本复核建议动作或缺少最新修改时间线索的退化。
- 多版本文件的创建 / 修改时间能作为版本判断线索被记录，而不是靠模型猜。
- 测试通过，并且测试覆盖新增行为。
- 编译检查通过。
- 隐私扫描通过。
- Git 提交清楚记录每轮完成内容。

如果无法提供这些证据，本轮结果只能视为讨论、设计或原型，不能视为完成。

## ＜必须遵守的限制条件>

以下限制不能被破坏：

- 不把真实测试 PDF / PPT / 图片 / 品牌资料提交进正式仓库。
- `import-ima-media` 这类私有导入命令不得写入 `examples/`、`docs/`、`prompts/`、`schemas/` 或项目根正式 source 目录。
- 不把真实测试品牌名、竞品名、价格、预算、销量、渠道政策、平台数据写入 README、PRD、prompt、schema、docs 或 examples。
- 不伪造 `已品牌确认`。
- 不把资料缺失内容编造成事实。
- 不让使用者逐条确认所有 Markdown 文件。
- 不自动覆盖旧知识。
- 不把一次性价格、临时政策、阶段激励、未验证判断和内部敏感执行信息提升为长期知识。
- 第一阶段不做复杂 Web UI、不接复杂模型 API、不做企业级 RAG。
- 不因某个开源工具 stars 高或 issue 少而直接替换默认 source engine；必须先通过本地小样评估证明它降低漏读和人工复核成本。
- `library_report.html` 必须保持本地静态产物，不依赖远程服务。
- Source anchor、risk level、内部质量标记默认不铺满用户界面，只在必要详情或后台文件中保留。
- 真实客户资料只能用于本地私有测试，不进入公开 demo 或 Skill 发布包。
- 遇到安全、隐私、权限或真实性不确定时，优先停止并报告，不继续扩大影响面。

## ＜允许使用的输入、工具、文件范围或操作边界>

Codex 允许使用：

- 当前仓库内的代码、文档、prompts、schemas、examples 和 tests。
- `_private_test_runs/` 中的私有测试资料，仅用于本地验证；该目录不得提交。
- ima 等私有知识库中的资料，仅在用户明确要求时读取，并只能下载或缓存到 `_private_test_runs/` 这类私有测试目录。
- 本地 Python CLI、单元测试、编译检查、文本搜索和 Git。
- 本地生成的临时目录，例如 `/tmp/...`，用于 demo 验证。
- 用户明确提供的本地文件路径。
- 公开项目或公开资料的经验，但必须转化为本项目自己的设计和实现。

Codex 不允许默认使用：

- 上传真实品牌资料到外部服务。
- 默认联网处理私有文件。
- 把 ima 等私有知识库中的真实文件、真实标题、真实内容复制进正式 examples、docs、prompts、schemas 或 README。
- 写入用户 Obsidian、NAS、云盘或其他非项目目录，除非用户明确要求。
- 修改与当前目标无关的文件。
- 删除、移动或覆盖用户未要求处理的资料。
- 将 `_private_test_runs/` 中的内容复制到正式 examples 或 docs。

## ＜如何判断下一步最优行动>

Codex 每轮选择下一步时，应按以下优先级判断：

1. **修复核心闭环断点**：如果 source conversion、输出结构、入库、报告页、测试或隐私检查存在断点，优先修复。
2. **补足验证证据**：如果某能力只有设计或说明，没有测试、demo 或实际文件证据，优先补证据。
3. **降低真实使用摩擦**：优先减少使用者需要人工确认、翻找文件、理解后台字段的负担。
4. **提升知识库可靠性**：优先处理冲突、版本、分类、状态、来源和可追溯性。
5. **增强可迁移性**：避免只适配单一品牌或单一 marketing 场景，让分类和流程可被不同业务使用者调整。
6. **再做体验增强**：视觉、交互、酷炫效果应建立在可验证知识结构之上。

每轮开始前，Codex 应能回答：

- 这一步会让核心闭环更完整吗？
- 这一步会带来新的可验证证据吗？
- 这一步会降低用户真实使用成本吗？
- 这一步是否会增加隐私或错误入库风险？
- 这一步是否仍在第一阶段边界内？

如果答案不清楚，应先讨论，不应直接开发。

## ＜已经尝试过的方法、已获得的证据、当前阻塞点，以及还需要什么信息或权限才能继续推进>

当遇到阻塞，或已经没有有效路径可以继续尝试时，Codex 必须停止，并按以下格式报告：

```text
已经尝试：
- ...

已获得的证据：
- ...

当前阻塞点：
- ...

还需要什么信息或权限：
- ...
```

必须停止报告的情况包括：

- 真实资料识别质量无法证明。
- 测试连续失败且原因不清楚。
- 需要模型 API、OCR 工具、外部服务、浏览器权限或文件权限，但当前不可用。
- 需求明显超出第一阶段边界。
- 继续开发会增加私有资料泄露风险。
- 输出可以运行，但无法证明对真实使用者有价值。
- 下一步只剩视觉炫技，没有明确验证价值。
- 需要用户确认分类、知识覆盖范围、业务口径或是否允许读取 / 写入某些资料。

在阻塞报告前，Codex 应先完成已经可安全完成的本地检查，例如查看错误日志、运行相关测试、确认文件存在性和检查 Git 状态。
