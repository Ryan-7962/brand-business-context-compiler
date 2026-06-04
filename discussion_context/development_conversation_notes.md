# 开发讨论纪要｜Brand AI Product Knowledge Compiler

> 说明：本文件保留了本次关于“品牌产品资料 → AI 可读产品知识库 Skill”的核心讨论脉络、判断和关键结论，便于交给 Codex 继续开发。它不是平台级完整聊天导出，而是围绕开发需求整理的可执行纪要。

## 1. 起点：GEO 供应商资料评估

用户正在推进一个示例产品 GEO 项目。供应商已有一版 GEO 知识库，主要内容包括：

- 产品基础档案
- A/B/C 三类正向 Query：综合推荐、使用场景、产品体验
- K1-K8 产品核心知识点
- K9 竞品差异化，主要围绕竞品A相关产品
- 文章生成规则

判断：供应商版本可以作为“产品知识库 V1 / 产品事实底稿”，但不够支撑完整 GEO 投放。它更像把 PPT 资料整理成 Word，而不是完整的 GEO 激活包。

## 2. Agent V2.1 的价值判断

用户找另一个 Agent 基于供应商稿增强出 V2.1，新增：

- D 类防御/质疑 Query
- 扩展 K9 竞品对比框架
- K10 用户语言 ↔ 品牌术语映射表
- GEO 适配规范
- AI 搜索平台适配规范
- Query 优先级与内容生成 SOP

判断：V2.1 方向正确，补上了供应商稿最缺的 GEO 策略层。但需要品牌方再做 V2.2 收口，避免过度攻击竞品、过度绝对化、证据泛化等问题。

## 3. 对供应商的要求沉淀

用户最终没有在群里发很长内容，而是要求供应商补：

1. D 类防御/质疑 Query
2. K9 竞品对比框架扩展到力士、澳宝、多芬等
3. K10 用户语言 → 品牌术语映射
4. Claim 证据矩阵

建议进一步明确：这些不应只在文章里体现，而应先作为母稿知识库固定模块补进去。下一步应先看：

- 更新后的母稿知识库
- 3-5 个典型 Query 的内容生成示例
- 每篇内容调用了哪些卖点、claim 和证据

## 4. 对供应商 AI 能力的判断

供应商回应使用“Kimi 的付费版”，后续又说“AI Agent 生成文章，结合 Query 分析和文章生成流程上下游，优化 prompt 和 skill，自动化生成”。

判断：该回答比较笼统，没有说明具体模型、是否 API、是否 RAG、是否有固定 Skill、是否批量化、知识库怎么调用、claim 如何校验。大概率是 Kimi 网页端/付费版 + 人工上传资料 + prompt 生成 + 人工校验，而不是成熟的定制 Agent 工作流。

建议：不要在群里直接质疑，而是用交付物验证能力。要求他们提供：

- 生成流程说明
- 输入如何进入系统
- 系统如何判断调用哪些卖点/claim/证据
- 是批量生成还是人工单条生成
- 怎么避免 claim 泛化
- 哪些环节 AI 自动，哪些环节人工修改

## 5. 对 GEO 周报的判断

供应商周报包含：

- 品牌可见度、Top3 可见度、产品可见度、中正情绪、文章引用率
- 本周小结
- 豆包/DS/千问等模型表现描述
- 发布数量：文章 32 篇、链接 82 条
- 下周计划

判断：作为客户 recap 勉强够；作为指导 GEO 优化的工作周报，颗粒度不足。

缺失：

- KPI 口径和分母
- 模型 × Query 明细
- 文章/链接引用归因
- 竞品占位信源分析
- 下周内容选题与对应 Query / Claim / 证据
- 与新版母稿知识库的调用关系

建议周报升级为“可诊断、可归因、可指导选题”的格式。

## 6. Skill 核心想法

用户提出真正想做的是一个 Skill：将品牌基础产品资料（PDF/PPT/电商详情页/渠道卖进资料等）转写为 AI 可读结构化文档，分为两类：

1. 品牌内部产品知识库：用于客服回答、竞品对比、AI 快速读取、减少 token 消耗。
2. GEO 产品知识库：用于指引 GEO 操作；可基于内部母库进一步生成。

判断：这个 Skill 很有价值，不是单次 GEO 项目，而是品牌产品知识资产标准化能力。

核心价值：

- 将人类产品资料转为 AI 可读知识资产。
- 避免 AI 直接读 PPT/PDF 造成漏读、误读和 token 浪费。
- 让产品 claim、香型、场景、证据、禁用表达结构化。
- 支撑客服、GEO、达人、电商、竞品、合规等多个下游场景。

## 7. Skill 不能只依赖 AI 读资料

用户补充：Skill 不能只是一味让 AI 读 PDF/PPT。品牌人员也必须输出 100% 确认内容，例如：

- 一句话卖点
- 产品价格策略
- 主推 SKU/香型
- 主要对标竞品
- 不建议对标竞品
- 本轮 GEO 优先方向
- 哪些 claim 可外发，哪些只能内部用
- 禁用表达

判断：这是项目关键升级。很多最重要的信息不会出现在产品介绍资料中，必须由品牌人员填写 Brand Lock Sheet。

Skill 应采用“双输入机制”：

- 来源资料输入：AI 抽取事实
- 品牌确认输入：品牌人员锁定商业判断和红线

优先级：

```text
品牌确认内容 > 来源资料明确事实 > AI 合理整理 > AI 推断
```

## 8. 建议转移到 Codex 开发

建议转到 Codex 开发，但第一阶段不要做复杂系统，而是做轻量 repo：

- README
- PRD
- Skill Spec
- Prompt pack
- Schema templates
- 示例项目
- 简单 CLI 骨架
- Claim Matrix 校验器
- 用户指南

第一版目标：模板 + Prompt + Schema + 示例 + 半自动脚本。

不建议一开始做企业级知识库/RAG/SaaS。

## 9. 核心架构建议

仓库建议：

```text
brand-ai-product-knowledge-skill/
├── README.md
├── prompts/
├── schemas/
├── examples/
├── docs/
├── src/
└── tests/
```

标准输出：

```text
outputs/<product_slug>/
├── 00_source_index.md
├── 01_brand_lock_sheet.md
├── 02_product_master_internal.md
├── 03_product_master_public_safe.md
├── 04_sku_cards.md
├── 05_claim_matrix.md
├── 06_user_language_map.md
├── 07_customer_service_faq.md
├── 08_competitor_battlecard_internal.md
├── 09_competitor_battlecard_public_safe.md
├── 10_geo_activation_pack.md
├── 11_influencer_brief_pack.md
├── 12_ecommerce_pdp_checklist.md
├── 13_risk_redline.md
└── 14_quality_check_report.md
```

## 10. 最重要的模块

### Brand Lock Sheet

品牌方确认锁定信息，是主控层。

### Claim Matrix

核心事实底盘，防止 AI 泛化和乱引用。

### User Language Map

把“用户怎么问”和“品牌怎么说”连接起来。

### GEO Activation Pack

从产品母库派生，用于 Query 占位、内容生成和 AI 搜索验证。

### Risk Redline

区分内部策略和外发安全表达。

## 11. 当前推荐开发策略

1. 先做示例产品训练资料 Demo。
2. 跑通 Brand Lock Sheet → Product Master → Claim Matrix → GEO Pack。
3. 形成一套可复制 Prompt 和 Schema。
4. 再把流程套到花露水、洗手液、防脱洗发水等其他产品。
5. 最后再考虑接入 WorkBuddy、IMA、Obsidian、NotebookLM 或企业知识库。
