# Source Converter Strategy｜资料转写增强方案

## 1. 目的

Brand AI Product Knowledge Compiler 的第一阶段分为两层：

1. Source-to-Markdown 资料保真转写层。
2. Product Knowledge Base 品牌知识母库编译层。

MinerU 这类成熟项目的价值主要在第一层：把 PDF、PPTX、长图、扫描件、表格、图片和复杂版面尽量保真地转成 Markdown/JSON，降低 AI 误读和漏读。

本项目不把 MinerU 当作品牌知识编译器。它是可选的高保真 source converter engine。

## 2. 从 MinerU 吸收的关键经验

MinerU 官方定位是面向 LLM / RAG / Agent 工作流的高精度文档解析引擎，输入覆盖 PDF、图片、DOCX、PPTX、XLSX，输出覆盖 Markdown、JSON 和中间结构。它的经验对本项目最有价值的部分，不是“总结能力”，而是“尽量保真地把人看的资料变成机器可读资料”。

### 2.1 多格式输入不是附加能力，而是核心入口

品牌资料不会只是一种格式。实际输入包括：

- PDF 产品培训资料。
- PPT/PPTX 品牌策略或营销材料。
- 电商详情页长图。
- 包装图。
- 检测报告截图。
- 竞品公开资料截图。

因此 Source Converter 层应设计为 adapter，而不是只写死一个 PDF 转 Markdown 方法。

推荐抽象：

```text
SourceConverter
├── pymupdf4llm_adapter      # 轻量默认 PDF 解析
├── mineru_adapter           # 高保真可选解析
├── image_ocr_adapter        # 长图/截图 OCR
└── manual_review_adapter    # 人工补录/复核
```

当前轻量实现已经支持 PDF / PPTX / Markdown / TXT / DOCX；长图、截图、XLSX 和扫描件应作为下一阶段高保真适配对象，而不是在轻量路径里假装已经完整识别。

### 2.2 输出不应只有 Markdown，还要有结构化元数据

MinerU 类项目的经验是：复杂资料只输出一份正文 Markdown 不够。我们需要同时保留：

- Markdown transcript。
- 页面/slide metadata。
- 图片/图表 asset。
- 表格结构。
- OCR/解析置信度。
- 低置信度区域。
- 转写报告。

本项目第一阶段应保留：

```text
converted_markdown/
├── source_transcripts/
├── assets/
├── source_facts/
└── conversion_report.md
```

MinerU 支持 Markdown、按阅读顺序排序的 JSON、可视化版面结果和 span 级结果。对应到本项目，后续不应只接收最终 Markdown，还应优先接收或映射这些中间结构，用来标记阅读顺序、版面块、表格、图片、公式、OCR 区域和低置信度区域。

### 2.3 阅读顺序和来源锚点必须保留

品牌资料中，claim 的可信度来自“它出现在哪一页、哪张图、哪个表格、哪条脚注”。

每个重要事实都应尽量保留 source anchor：

```text
S001#page=24
S001#slide=12
S003#image=long_pdp_01#region=claims
```

后续 Claim Matrix、Brand Lock Sheet Draft、Product Knowledge Base 都必须能回到这些 anchor。

### 2.4 视觉页不能只抽文字

实际产品培训 PDF/PPT 常有大量视觉页。文本层可能为空或不完整。

本项目应保留：

- 整页截图。
- 图片/图表占位。
- 客观图片说明。
- `低置信度，待人工复核` 标记。

只有这样才能避免把视觉页中的卖点、包装信息、图表数据和角标说明丢掉。

这也是 MinerU 对本项目最关键的启发：OCR、版面识别、图片/图表提取和阅读顺序恢复应属于资料转写质量问题，而不是让后面的营销语义编译 prompt 去猜。

### 2.5 表格和图片要单独评估质量

表格、商品详情页长图、检测报告截图最容易出错。Source Conversion Report 应记录：

- 表格是否检测到。
- 表格是否能还原为 Markdown/HTML。
- 图片是否已保留 asset。
- 是否需要 OCR。
- 是否需要人工复核。

### 2.6 后端模式要分层，不能让重型依赖阻塞第一版

MinerU 的能力强，但部署可能比轻量 CLI 更重。第一版应采用分层策略：

| 模式 | 用途 | 是否第一版必需 |
|---|---|---|
| lightweight | PyMuPDF / pymupdf4llm 默认解析 PDF | 是 |
| high_fidelity | MinerU 高保真解析 PDF/PPTX/图片/表格/OCR | 否，作为 optional |
| manual_review | 人工查看截图并补录关键事实 | 是 |

MinerU CLI 的典型调用方式是：

```bash
mineru -p <input_path> -o <output_path>
mineru -p <input_path> -o <output_path> -b pipeline
```

其中 `pipeline` 后端可作为 CPU 友好的本地评估路径。正式接入前，本项目只做 optional adapter，不把安装 MinerU 作为默认门槛。

## 3. 本项目的 Source Converter 输出规范

### 3.1 Source Transcript

每个原始资料生成一个 transcript：

```text
converted_markdown/source_transcripts/S001_product_training.md
```

每页结构：

```markdown
## Page 24
- Source Anchor：S001#page=24
- Page Screenshot：../assets/S001_product_training/page_24.png
- Extracted text chars：
- Embedded images detected：
- Vector drawings detected：

### Text

### Images / Charts

### Tables

### Notes / Footnotes / Small Print

### Low Confidence / Need Review
```

### 3.2 Source Conversion Report

每个资料生成转换质量记录：

```markdown
| 来源编号 | 原始文件 | 原始文件创建时间 | 原始文件修改时间 | 转写 Markdown | 提取方式 | 页码/Slide 范围 | 表格保留 | 图片/图表占位 | Notes/角标/脚注 | 低置信度区域 | 待人工复核 |
```

后续应增加：

```markdown
| 转写引擎 | OCR 是否启用 | 表格还原质量 | 图片说明质量 |
```

文件创建/修改时间用于多版本品牌资料的版本判断。若内容冲突，默认把修改时间更新的文件作为优先参考线索，但关键品牌口径、价格政策、策略判断不应被自动覆盖，应进入后续冲突或旧知识更新队列。

### 3.3 Source Facts

Source Facts 是从 transcript 中抽取的事实层：

```text
converted_markdown/source_facts/S001_source_facts.md
```

规则：

- 只抽取来源资料明确出现的信息。
- 不做品牌确认判断。
- 不做外发安全判断。
- 不生成 brief。
- 不能确认的写 `待确认`。
- 资料缺失的写 `待补充`。

当前轻量 CLI 已提供：

```bash
brand-skill build-source-facts <project_dir>
```

它会从 `converted_markdown/source_transcripts/` 生成 `converted_markdown/source_facts/`，作为后续 Marketing Semantic Compiler 的事实候选输入。该步骤只做确定性文本拆分和 Source Anchor 继承，不替代模型语义抽取，也不代表品牌方确认。

## 4. MinerU 在本项目中的建议接入方式

### 4.1 第一版

不强制安装 MinerU。

当前保留：

- PyMuPDF / pymupdf4llm 默认转写。
- 每页截图保真。
- 人工复核视觉页。
- Source Conversion Report。
- `brand-skill check-mineru <project_dir>` 本地 readiness 检查，只判断 MinerU CLI 是否存在、版本是否可读取，并生成 `converted_markdown/mineru_readiness_report.md`。

### 4.2 第二步评估

先运行 readiness 检查，确认本机可以评估 MinerU：

```bash
brand-skill check-mineru <project_dir>
```

用示例品牌产品培训资料抽 5 页做 MinerU 对比：

- 封面/纯视觉页。
- 卖点总览页。
- 香型表格页。
- 消费者实证页。
- 26 年升级页。

评估维度：

| 维度 | 当前 pymupdf4llm | MinerU | 是否值得接入 |
|---|---|---|---|
| OCR 完整度 | | | |
| 表格还原 | | | |
| 图片/图表保留 | | | |
| 阅读顺序 | | | |
| 输出 Markdown 可读性 | | | |
| 部署复杂度 | | | |

额外评估：

| 维度 | 当前 pymupdf4llm | MinerU | 是否值得接入 |
|---|---|---|---|
| 阅读顺序是否稳定 | | | |
| header/footer/page number 清理 | | | |
| 图片中文字 OCR | | | |
| 图表标题和脚注保留 | | | |
| 低置信度区域是否可定位 | | | |
| 输出 JSON 是否能映射到 Source Anchor | | | |

### 4.3 正式接入

如果 MinerU 在关键页明显优于 baseline，则增加：

```bash
brand-skill convert-source <project_dir> --engine mineru
brand-skill convert-source <project_dir> --engine pymupdf4llm
```

并在 `conversion_report.md` 中记录 engine。

## 5. 当前开发 next step

1. 先把当前 PyMuPDF/pymupdf4llm baseline 做成可复用 CLI。
2. 保证混合文件导入时 Source ID 按 `source/` 相对路径稳定分配，避免因文件类型导致引用漂移。
3. 继续增强 `source_facts/`：识别标题上下文、表格行、图片说明和低置信度页面。
4. 给 Source Conversion Report 增加 engine/OCR/table/image quality 字段。
5. 小规模评估 MinerU。
6. 再决定是否把 MinerU 做成 optional adapter。
