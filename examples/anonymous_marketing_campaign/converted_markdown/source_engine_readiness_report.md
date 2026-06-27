# Source Engine Readiness Report

## 检查边界

- 检查时间：2026-06-27T15:31:51Z
- 本报告只检查本机是否具备评估条件，不上传真实品牌资料。
- Microsoft MarkItDown / MinerU 都只是 Source-to-Markdown 候选引擎，不是品牌知识编译器本体。
- 未经小样证据证明前，不把任何候选引擎设为默认。

| Engine | 状态 | CLI / 路径 | 版本输出 | 建议动作 |
|---|---|---|---|---|
| pymupdf4llm | 内置默认 | Python dependency | 随项目环境 | 继续作为 baseline。 |
| markitdown | 未检测到 CLI | 未找到 | 未执行 | 不影响第一阶段闭环；仅在本机可用后进入小样评估。 |
| mineru | 未检测到 CLI | 未找到 | 未执行 | 不影响第一阶段闭环；仅在本机可用后进入小样评估。 |

## 当前建议

- `pymupdf4llm` 保持 baseline。
- `markitdown` 优先作为 Microsoft MarkItDown 多格式 Markdown 转换候选评估，重点看 PPTX / DOCX / XLSX / HTML / ZIP 和普通 PDF。
- `mineru` 继续作为复杂版式、扫描件、图片文字、表格和阅读顺序的高保真候选评估。
- DuanYan007/markitdown4j 暂不进入默认检查；若后续需要 Java / PaddleOCR / 本地批量部署，再单独评估。
