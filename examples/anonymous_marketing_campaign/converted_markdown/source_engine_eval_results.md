# Source Engine Evaluation Results

## 评估边界

- Baseline：pymupdf4llm。
- 候选：Microsoft MarkItDown、MinerU。
- 本文件只记录 source conversion 工具链的小样证据，不是品牌确认，也不是内容总结。
- 真实品牌资料只能在 `_private_test_runs/` 中评估；公开 examples / docs / prompts / schemas 不得写入真实品牌名、预算、销量、价格、平台数据或内部会议内容。
- 未经结果证据证明前，不把候选引擎设为默认链路。

## 小样级对比记录

| Source Anchor | 原始文件 | 推荐对比引擎 | pymupdf4llm baseline 观测 | MarkItDown 观察 | MinerU 观察 | 结论 | 是否调整默认链路 |
|---|---|---|---|---|---|---|---|
| 待补充 | 待补充 | pymupdf4llm baseline | 暂无候选小样，需先生成 source_quality_report 候选页 | 待填写 | 待填写 | 待判断 | 否，待证据 |

## 接入判断表

| 维度 | 当前判断 | 证据 | 后续动作 |
|---|---|---|---|
| 文字覆盖率 | 待判断 | 待填写 | 对比抽样页全文覆盖情况 |
| 页码 / slide 锚点 | 待判断 | 待填写 | 检查是否能稳定回溯原文件位置 |
| 表格结构 | 待判断 | 待填写 | 检查复杂表格和跨页表格 |
| 图片 / 图表 / 小字 | 待判断 | 待填写 | 检查视觉页和小字区域 |
| 阅读顺序 | 待判断 | 待填写 | 检查多栏、图文混排和长页 |
| Markdown 可读性 | 待判断 | 待填写 | 检查后续 facts / semantic transcript 是否更稳定 |
| 本地部署复杂度 | 待判断 | 待填写 | 评估依赖、速度和失败模式 |
| 隐私和外部服务风险 | 待判断 | 待填写 | 确认不上传真实品牌资料 |

## 当前建议

- MarkItDown 已可作为 optional adapter 使用，但只有当它在多格式输入上明显减少漏读，才扩大使用范围。
- MinerU 仍保持高保真候选；只有当 OCR / 表格 / 图片 / 阅读顺序显著优于 baseline，才考虑接入 `convert-source --engine mineru`。
- 如果候选引擎只是让摘要更顺口，但不能改善 source anchor、覆盖率和复核成本，不应改变默认链路。
