# Schema｜10_context_asset_index.md

## 目的

`10_context_asset_index.md` 用于把一次 Marketing 资料编译得到的内容沉淀为可复用、可检索、可审核的 Brand Context Assets。它连接第一阶段的语义底稿和第二阶段的派生 Skill，但不直接生成 GEO、PDP、拍摄、种草或销售 brief。

## 必须包含的章节

### 1. Context Type Coverage

| 字段 | 要求 |
|---|---|
| 上下文类型 | 必须从 8 类中选择：品牌、商品、素材、项目、话术、人设、网络、案例 |
| 覆盖程度 | `高` / `中` / `低` / `不适用` |
| 本资料包含的内容 | 简述本资料覆盖的信息 |
| 缺失/待补充 | 没有的信息必须明示 |
| 信息状态 | 使用标准信息状态 |

### 2. Reusable Context Assets

| 字段 | 要求 |
|---|---|
| Asset ID | `CA001` 起连续编号 |
| 上下文类型 | 8 类之一 |
| 可复用资产 | 可被后续 Skill 调用的事实、策略、话术、限制、证据或模式 |
| 适用场景 | GEO / PDP / 拍摄 / 种草 / 销售 / 客服 / 投放 / 复盘 / 案例沉淀等 |
| 来源锚点 | 至少一个 `S001#page=1` 格式锚点 |
| 信息状态 | 使用标准信息状态 |
| Review Priority | `高` / `中` / `低` |

### 3. Decision Rationale and Missing Context

记录资料背后的关键决策、当前资料能解释的部分，以及必须由品牌或项目人员补充的内容。不要把缺失的决策背景补写为确定事实。

### 4. Downstream Skill Reuse Map

| 字段 | 要求 |
|---|---|
| 下游 Skill | 例如 GEO Brief Skill、PDP Brief Skill、Shooting Brief Skill、Seeding Brief Skill |
| 可调用资产 | 引用 Asset ID |
| 禁止/限制使用 | 说明不能外发、不能泛化、不能跨 SKU 使用等限制 |
| 需要先确认 | 说明调用前需要品牌经理确认的字段 |

### 5. Context Evolution Hooks

定义后续新增资料时如何补充上下文资产，例如投放数据补素材上下文、复盘资料补案例上下文、客服记录补话术上下文、用户评论补网络上下文。

## 标准信息状态

| 状态 | 含义 |
|---|---|
| 已从来源资料提取 | 资料中明确出现，可追溯来源 |
| AI 结构化转述，待确认 | AI 将原资料转成更清楚的结构化表达，需人工复核 |
| AI 初步拟定，待品牌确认 | AI 根据资料合理推导，不能视为品牌最终确认 |
| 待补充 | 资料中没有，AI 也不能合理拟定，必须由品牌方补充 |
| 不适用 | 当前资料类型不涉及该字段 |
| 已品牌确认 | 品牌经理确认后，才能作为最高优先级依据 |

## 校验规则

- 每个 `Reusable Context Assets` 行必须有 Asset ID、上下文类型、来源锚点、信息状态和 Review Priority。
- 功效、数据、竞品、预算、内部策略相关资产不得标为 `低` Review Priority。
- `Decision Rationale and Missing Context` 不允许为空；如果资料没有决策背景，也必须写出 `待补充` 项。
- `Downstream Skill Reuse Map` 只能映射调用关系，不允许生成完整下游 brief。
