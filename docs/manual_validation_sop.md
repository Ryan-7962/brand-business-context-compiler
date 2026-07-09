# Manual Validation SOP｜人工原页抽样验收

本 SOP 用于补齐第一阶段最后的证据缺口：证明或否定 Structured Wiki 是否达到 90% 页面级 / 事实级准确率。

## 1. 先选一个私有资料包

只在 `_private_test_runs/` 里操作，不把真实品牌资料、截图、原文、价格、预算、销量或内部策略写入公开目录。

优先选择已经跑过当前主链路并通过 contract 的资料包。确认存在：

- `contract_verification_report.md`
- `converted_markdown/source_quality_report.md`
- `converted_markdown/source_facts/`
- `evaluation/quality_sampling_log.md`

## 2. 按质量日志抽页

打开 `evaluation/quality_sampling_log.md`，按其中的 Page Sampling Plan 回到原 PDF / PPT / 截图核对。

如果私有目录里已有 `evaluation/human_validation_packet.md` 或 `evaluation/human_validation_packet.html`，优先从这份入口包开始核对；它只是减少查找成本，不能替代人工判断。HTML 入口包如提供“生成回填摘要”，可直接复制到 `quality_sampling_log.md` 后再补 facts 结论。

人工回填后的 `quality_sampling_log.md` 是验收证据；重跑 `build-value-benchmark` 会保留它。只有源文件大改、需要重新抽样时，才手动另存旧日志后再重新生成。

优先按 `source_anchor` 打开对应的 `converted_markdown/source_transcripts/*.md`。如果 transcript 里有 `Page Screenshot` 或页面截图表，先用截图快速核对；截图不足以判断时，再回到原 PDF / PPT / 原始图片。

每页只判断五件事：

- 页码 / slide 锚点是否正确。
- 主要文字是否被转写。
- 表格、图片、图表、小字、OCR 不清时是否被标为低置信度。
- 关键事实是否能回到该页或相邻上下文。
- 是否有资料未提供却被写成确定事实。

## 3. 抽 source facts

从 `converted_markdown/source_facts/` 抽至少 5 条事实候选，逐条回到 transcript 或原页。

每条只判断四件事：

- 是否有 Source Anchor。
- 是否能在来源中找到依据。
- 数字、时间、对象、范围是否被改错。
- 是否把 AI 转述或来源讨论冒充品牌确认。

## 4. 记录结果

只在私有目录的 `evaluation/quality_sampling_log.md` 里记录结果。公开文档只写匿名汇总。

AI 视觉预检或 source facts 可追溯性预检只能作为旁证，不能填入页面级 / 事实级通过率；通过率必须来自人工回看原页、截图或 transcript 后的判断。

最小汇总格式：

```text
抽样页数：N
页面级通过：N
页面级不通过：N
抽样 facts：N
事实级通过：N
事实级不通过：N
P0 / P1：N / N
是否可作为 90% 准确率证据：是 / 否
下一步：无需处理 / 重新截图 / 换引擎小样 / 修 prompt / 修代码
```

## 5. 通过标准

同时满足才算本批次通过：

- 页面级通过率 >= 90%。
- 事实级通过率 >= 90%。
- P0 = 0。
- 所有 P1 已进入复核队列，不提升为长期可靠知识。

不满足就不要包装结论，直接写“不能作为 90% 准确率证据”。
