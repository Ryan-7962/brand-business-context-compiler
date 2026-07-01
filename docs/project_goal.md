# Project Goal｜Brand / Business Context Compiler

## 1. 最终目标

本项目不是普通 PDF / PPT 总结工具，也不是企业级 RAG 或正式 Web App。

它的最终目标是形成一组本地优先的 Brand / Business Context Compiler Skills：把品牌、Marketing、销售、渠道、产品、会议、策略、Campaign、培训、复盘、投放、竞品、科研或功效检测报告等“原本给人看的资料”，编译成 AI 更容易读取、理解、检索、引用、复用和持续更新的 Markdown Wiki。

更简单地说：

```text
Raw Sources
→ Compiler Skill
→ Structured Wiki
→ Work Buddy / Agent 基于 Wiki 生成工作产出
```

## 2. 三层架构

### Layer 1｜Raw Sources

同事或使用者直接丢进来的原始资料：

- PDF / PPT / PPTX / DOCX / Markdown / TXT。
- 产品介绍、产品培训、品牌策略、Campaign 方案、广告公司提案、销售策略、经销商大会资料。
- 过往种草 brief、达人内容复盘、竞品内容、投放总结、科研或功效检测报告。

Raw Sources 是事实来源，不被改写、不被覆盖。多个版本并存时，保留创建时间、修改时间和转写时间；内容冲突时，默认把更新资料作为更高优先级线索，但不自动覆盖旧知识。

### Layer 2｜Structured Wiki

Compiler Skill 把 Raw Sources 编译成 AI-readable Markdown Wiki：

- `converted_markdown/`：尽量保真转写，保留页码 / slide / 文件来源锚点。
- `outputs/`：文件大纲、语义转述、关键事实、策略结构、风险和索引。
- `brand_context_library/`：长期可复用的品牌 / 产品 / 内容 / 渠道 / 竞品 / 案例 / 话术 / 决策知识。
- `00_source_index.md`、`10_context_asset_index.md`、`retrieval_maps/source_packages.md`：告诉 Agent 什么时候该读哪份资料。

Wiki 的价值不是“写得像人类总结”，而是让 Agent 少漏读、少混淆版本、少重复读取全文，并能持续沉淀上下文。

### Layer 3｜Agent Outputs

Work Buddy、Codex、Claude 或其他 Agent 基于 Wiki 生成后续工作产出：

- GEO brief。
- PDP brief。
- 种草内容 brief。
- 拍摄 brief。
- 销售话术。
- 客服 FAQ。
- 投放复盘。
- 竞品分析。
- 品牌策略总结。

这些派生产出不属于第一阶段默认开发重点。第一阶段只保证 Wiki 层足够可靠、可索引、可追溯。

## 3. 第一阶段边界

第一阶段只做：

- 本地 workflow。
- Skill 文件组包。
- CLI。
- Schema / Prompt Pack。
- Demo。
- 本地 HTML 报告。

第一阶段不做：

- 正式 Web UI。
- 企业级 RAG。
- 多用户权限系统。
- 复杂模型 API。
- 自动外发或自动品牌确认。
- 复杂数据库或向量服务。

## 4. 人工介入原则

本项目不应把“让人逐条检查 AI 是否读对”作为主要工作流。

默认应相信 Source-to-Markdown 和 AI 结构化能力，先自动完成读取、转写、索引和 Wiki 编译。人只处理例外：

- 文件大纲明显识别错。
- 页面、slide、表格、图片、小字、截图或 OCR 区域没有读清楚。
- 总页数、已读取页数、缺失页数不一致。
- 关键事实缺来源、缺版本依据或与旧知识冲突。
- 资料本身没有提供的信息，需要业务人员补充。

人工确认页和报告只回答四个问题：

1. 这次读了哪些文件、每份文件大概讲什么？
2. 识别出来的索引大纲是什么？
3. 哪些页面 / slide / 图表 / 表格没有读清楚？
4. 如果需要弥补，应该重新提供截图、换转写引擎、补充原文件，还是人工补录？

不要求使用者逐条确认所有 Markdown、事实表、资产 ID、风险等级或后台质量字段。

## 5. 真实性原则

系统必须基于真实读取结果说话：

- 有 18 页就必须说明 18 页的读取状态，不能只读 16 页却假装完整。
- 没有数据就写“资料未提供”，不能编造数字或结论。
- OCR、图片、表格、小字没有读清楚，就明确标出来。
- AI 推断必须标注为待确认，不能冒充来源事实或品牌确认。
- 真实品牌测试资料只进入本地私有测试区，不进入公开 examples、docs、prompts、schemas 或 README。

## 6. 验收标准

第一阶段有效，不看“摘要是否顺口”，而看是否能证明 Wiki 层更可靠：

- `run-phase1` 能从 `source/` 跑到 `contract_verification_report.md`。
- `converted_markdown/` 有完整来源转写、页码 / slide 锚点、文件创建时间、修改时间、转写时间。
- `source_quality_report.md` 能说明总页数、需要复核页数、表格数、图片/图表/小字/OCR 风险和建议动作。
- `outputs/00_source_index.md` 能告诉 Agent 每份文件的转写稿和 source facts 在哪里。
- `outputs/10_context_asset_index.md` 能告诉 Agent 哪些内容适合后续任务调用。
- `outputs/11_context_library_update_plan.md` 能说明本次资料如何进入 Wiki，以及后续任务应优先读取什么。
- `brand_context_library/` 能生成长期 Markdown 条目、冲突队列、更新队列和 retrieval map。
- `library_report.html` 能用中文展示知识库地图、索引大纲、待处理事项和条目详情。
- 对同一批资料，基于 Wiki 的 Agent 输出应比直接丢 PDF / PPT 给 Agent 更完整、更可追溯、更少版本混淆。
- 测试、编译检查、隐私边界和 Git 提交记录通过。

## 7. 当前下一步

当前不优先继续堆功能或做复杂工具评估。

下一步应选 1-2 个真实私有资料包做瘦身验收：

1. 把多份资料放入同一个 `source/` 文件夹。
2. 跑 `run-phase1`。
3. 检查 HTML 报告和 Wiki 索引是否能回答：
   - 读了哪些文件？
   - 每份文件的大纲是什么？
   - 哪些页或内容没读清楚？
   - 后续做 GEO / 种草 / PDP / 拍摄 brief 时应优先读取哪些 Wiki 文件？
4. 只修复真实验收暴露出的最小缺口。
