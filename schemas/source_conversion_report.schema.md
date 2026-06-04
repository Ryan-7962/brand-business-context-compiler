# Schema｜Source Conversion Report

```markdown
# Source Conversion Report｜<产品名>

| 来源编号 | 原始文件 | 转写 Markdown | 转写引擎 | 提取方式 | OCR 是否启用 | 页码/Slide 范围 | 表格还原质量 | 图片/图表保留 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S001 | | converted_markdown/source_transcripts/<file>.md | pymupdf4llm / mineru / manual | 文本解析 / OCR / 人工摘录 / 截图说明 | 是/否/不适用 | | 高/中/低/待复核 | 是/部分/否/不适用 | 是/部分/否/不适用 | | |
```

## 填写规则

- 资料转写层不做营销总结。
- 每个原始文件都应有一条转写记录。
- 必须记录转写引擎，便于对比 pymupdf4llm、MinerU 和人工补录。
- 转写失败、OCR 不确定、复杂表格和视觉页必须进入 `待人工复核`。
- 图片、图表、包装图和详情页视觉区应保留资产路径或占位说明。
