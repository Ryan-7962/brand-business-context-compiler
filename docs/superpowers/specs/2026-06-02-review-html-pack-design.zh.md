# Review HTML Pack 设计说明

## 1. 目标

Brand Marketing Knowledge Compiler 会输出多份 Markdown 文件。这些文件适合作为 AI 可复用的结构化营销语义底稿和审计记录，但不适合作为品牌经理的主要审核界面。

第一阶段工作流应增加一个本地静态审核包：

```text
review/
├── brand_review.html
└── review_decisions.json
```

这不是 Web UI、SaaS 产品，也不是企业级审核系统。它是一个轻量的本地交付物，由 Markdown 输出生成，帮助品牌经理在一个页面中集中审核关键判断。

## 2. 范围

### 2.1 第一版要做

- 从第一阶段输出文件生成一个本地 `review/brand_review.html`。
- 用更适合品牌经理阅读的方式呈现关键审核项。
- 优先突出高风险策略、数据、claim 和外发风险。
- Include source anchors such as `S001#page=24`。
- 显示信息状态：
  - `已从来源资料提取`
  - `AI 结构化转述，待确认`
  - `AI 初步拟定，待品牌确认`
  - `待补充`
  - `不适用`
  - `已品牌确认`
- 在浏览器页面中提供审核状态控件：
  - `确认`
  - `需修改`
  - `待补充`
  - `不采用`
- 允许用户从页面导出或复制 `review_decisions.json`。
- 增加一个 CLI 命令生成审核包。

### 2.2 第一版不做

- 不接模型 API。
- 不做后端服务。
- 不做登录、权限、多用户协作。
- 不建数据库。
- 不自动对外发布内容。
- 不做完整 React / Vite Web App。
- 不尝试在浏览器里完整编辑所有 Markdown 文件。

## 3. 审核页面结构

HTML 页面分成五个审核区。

### 3.1 总览

展示：

- 项目 / 资料名称。
- 文件类型。
- 来源资料数量。
- 审核项数量。
- 高风险项数量。
- `待补充` 项数量。
- 当前生成的关键文件路径。

目标是让品牌经理一眼知道最需要先看哪里。

### 3.2 Document Profile 审核

读取：

- `outputs/02_document_profile.md`

展示：

- 文件类型。
- 文件目的。
- 目标读者。
- 时间范围。
- 业务阶段。
- 资料可信度。

品牌经理需要确认 AI 是否理解了这份资料的性质，而不是把所有资料都当作产品资料。

### 3.3 Key Facts / Claims 审核

读取：

- `outputs/04_key_facts_and_claims.md`

展示：

- 明确事实。
- 数据和指标。
- 传播主张 / claim。
- 证据来源。
- 适用范围。
- 待确认事项。

产品资料里的 SKU / 香型 claim 只作为其中一种情况呈现。

### 3.4 Strategy and Execution 审核

读取：

- `outputs/05_strategy_and_execution_map.md`

展示：

- 业务背景。
- 核心目标。
- 核心洞察。
- 策略主线。
- 渠道和触点。
- 时间线。
- 内容资产。
- 预算 / 资源 / 货盘 / 组织分工。
- 数据指标。
- 下一步动作。

### 3.5 Risk and Review 审核

读取：

- `outputs/06_risk_and_review_items.md`
- `outputs/09_quality_check_report.md`

展示：

- 事实缺口。
- 策略推断风险。
- 数据口径风险。
- 平台合规风险。
- 竞品攻击风险。
- 内部信息外泄风险。
- 外发前必须确认的内容。

## 4. 数据流

```text
outputs/*.md
    ↓
brand-skill build-review-pack <project_dir>
    ↓
review/brand_review.html
```

第一版可以保守解析 Markdown：

- Markdown 表格解析为行数据。
- 非表格区域按标题切块，以近似 Markdown 的形式展示。
- 如果某个区域不能稳定解析，就在 HTML 中展示原始 Markdown 块，并标记为 `待人工复核`。

浏览器交互只发生在本地：

- 审核状态保存在页面 JavaScript 内存中。
- 页面提供 `Download review_decisions.json` 按钮。
- 页面提供可复制的 JSON 文本框作为兜底。

第一版只需要生成 HTML 和可导出的 JSON，不自动把点击结果写成 confirmed 版。

## 5. CLI 命令

新增：

```bash
brand-skill build-review-pack <project_dir>
```

预期行为：

- 读取 `outputs/`。
- 创建 `review/`。
- 写入 `review/brand_review.html`。
- 如果关键文件缺失，给出清晰错误。
- 不覆盖已有 `review_decisions.json`，除非后续版本显式增加参数。

## 6. HTML 设计方向

页面应该像一个 Marketing 资料审核台，而不是营销落地页。

布局：

- 顶部固定摘要栏。
- 左侧分区导航。
- 中间主审核区。
- 风险标签和信息状态标签。
- 高风险项用表格优先展示。
- 策略和执行信息用紧凑分区展示。

视觉优先级：

- 高风险项明显突出。
- `待补充`、`不适用`、`AI 初步拟定，待品牌确认` 容易被看见。
- 每个审核项旁边能看到来源锚点。
- 按钮清楚、紧凑，不抢内容注意力。

不要做装饰性 hero，不做 landing page，不做重动画。

## 7. 测试

增加聚焦测试：

- `build-review-pack` 能生成 `review/brand_review.html`。
- 生成的 HTML 包含核心区域：
  - Document Profile Review。
  - Key Facts / Claims Review。
  - Strategy and Execution Review。
  - Risk and Review Items。
- 缺少关键默认输出时应清晰失败。
- 现有单元测试继续通过。

## 8. 产品决策

第一版不自动写入 confirmed Markdown。它只在浏览器中生成可导出的 `review_decisions.json`。

这样可以保持第一阶段轻量，也避免把“页面点击确认”误认为已经产生真实品牌确认版。等审核交互格式跑顺后，再增加由 `review_decisions.json` 生成 confirmed 输出的能力。
