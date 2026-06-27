# Updated Project Goal｜Brand / Business Context Compiler

## 1. 最终目标

本项目最终要完成的不是一个普通 PDF / PPT 转 Markdown 工具，也不是一个单次资料总结器，而是一个本地优先的 Brand / Business Context Compiler。

它要帮助品牌、Marketing、销售、渠道、产品、客服或个人知识工作者，把长期散落在 PDF、PPT、长图、会议资料、策略方案、复盘报告、培训稿、投放总结和私有知识库中的“人类阅读型资料”，转成 AI 能稳定理解、检索、引用、复用和持续演进的结构化上下文知识库。

第一阶段的核心目标是跑通：

```text
原始资料
→ Source-to-Markdown 高保真转写
→ AI-readable 结构化 Markdown
→ 文件画像 / 语义转述 / 事实 / 策略 / 风险
→ Context Asset Index
→ Context Library Update Plan
→ 本地知识库写入
→ 冲突 / 旧知识更新 / 不入库队列
→ library_report.html 知识地图
→ 后续 brief / Agent / 工作流调用
```

## 2. 项目不是什么

- 不是把 PPT 变成更漂亮的摘要。
- 不是让 AI 直接替品牌经理做最终判断。
- 不是企业级 RAG 平台。
- 不是复杂 Web UI。
- 不是默认上传真实品牌资料到外部服务。
- 不是把所有资料强行归类成产品资料、SKU 或 claim。

## 3. 对用户的价值

使用者现在的普通做法是：把一份 PDF / PPT 直接发给 AI，让 AI 读完后回答问题。这个方法适合临时问答，但不稳定：

- 多文件、多版本时容易混淆。
- 图片页、表格页、PPT 版式页容易漏读。
- 没有稳定来源锚点，后续难追溯。
- 一次回答结束后，知识不会自然沉淀。
- 后续做 GEO、PDP、种草、销售、复盘 brief 时，需要反复重新喂资料。

本项目的价值是把“临时读文件”升级为“持续积累上下文”：

- 每份资料先转成可追溯的 Markdown 中间层。
- 每个事实、策略、结论尽量保留来源位置。
- 每次导入都生成可入库的 Context Assets。
- 多版本冲突和旧知识更新进入队列，不自动覆盖。
- 用户只处理识别异常和真正需要判断的问题。
- 后续任何 brief 或 Agent 工作流都能从长期库调用上下文。

## 4. Source Converter 策略

资料转写层采用多引擎评估，不把任何单一工具神化。

| 引擎 | 当前角色 | 接入原则 |
|---|---|---|
| `pymupdf4llm` | 当前 baseline | 保持默认轻量路径，用于跑通第一阶段闭环 |
| Microsoft MarkItDown | 优先评估候选 | 重点评估多格式 Markdown 转换、PPTX / DOCX / XLSX / HTML / ZIP 和普通 PDF |
| MinerU | 高保真候选 | 重点评估复杂版式、扫描件、图片文字、表格和阅读顺序 |
| DuanYan007/markitdown4j | 后续候选 | 需要 Java、本地 OCR、PaddleOCR 或批量部署时再评估 |
| manual review | 兜底能力 | 对关键低置信度页面进行人工补录或修正 |

MarkItDown / MinerU 的价值只在 Source-to-Markdown 层。它们不能替代本项目的 Context Asset Index、Library Update Plan、版本冲突、异常复核和长期知识库。

## 5. 第一阶段验收标准

第一阶段有效，不看“摘要是否顺口”，而看是否有证据证明链路更可靠：

- `run-phase1` 能从 `source/` 跑到 `contract_verification_report.md`。
- `converted_markdown/` 有页码、截图、低置信度说明、质量报告和文件创建 / 修改时间。
- `source_engine_readiness_report.md` 能记录本机可评估的 source engines。
- `source_engine_eval_plan.md` 能列出适合对比 pymupdf4llm / MarkItDown / MinerU 的小样。
- `outputs/` 能生成文件画像、语义转述、事实、策略、风险和 Context Asset Index。
- `brand_context_library/` 能实际写入长期条目。
- `library_report.html` 能让用户用中文查看知识地图、搜索、筛选和待处理事项。
- `direct_vs_skill_benchmark.md` 能对比“直接发 PDF/PPT 给 AI”和“先编译成上下文库再问”的差异。
- 测试、隐私扫描和 contract verification 通过。

## 6. 当前下一步

当前最优下一步是补齐 Source Engine Evaluation：

1. 保持 `pymupdf4llm` 默认路径不变。
2. 增加 `check-source-engines`，检查 MarkItDown / MinerU 本机评估条件。
3. 增加 `plan-source-engine-eval`，用真实质量报告选出小样对比页。
4. 用私有测试资料记录 pymupdf4llm / MarkItDown / MinerU 的差异。
5. 只有当候选引擎明显降低漏读和人工复核成本，才进入真实 adapter 接入。
