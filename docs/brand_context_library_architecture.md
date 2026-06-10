# Brand Context Library Architecture

## 1. 定位

Brand Marketing Context Compiler 的长期目标不是给每份 PDF 做总结，而是把品牌 Marketing 工作中不断产生的资料、会议、方案、复盘和判断，沉淀为一个可持续演化的品牌上下文知识库。

## 2. 推荐长期目录

```text
brand_context_library/
├── 00_library_index.md
├── brand/
├── product/
├── project/
├── asset/
├── language/
├── persona/
├── network/
├── case/
├── decision/
├── retrieval_maps/
├── review_queue/
└── evolution_log.md
```

## 3. 目录含义

| 目录 | 内容 |
|---|---|
| `brand/` | 品牌定位、品牌资产、调性、表达原则 |
| `product/` | 商品事实、卖点、SKU、证据、适用范围 |
| `project/` | 活动、上市、渠道、销售、投放项目过程 |
| `asset/` | 图片、视频、脚本、视觉风格、素材表现 |
| `language/` | 销售话术、客服话术、种草表达、禁用表达 |
| `persona/` | 用户画像、达人/主播人设、目标人群理解 |
| `network/` | 平台语境、搜索语境、竞品舆情、行业趋势 |
| `case/` | 成功/失败案例、复盘结论、可迁移打法 |
| `decision/` | 关键决策、被否方案、判断理由和会议结论 |
| `retrieval_maps/` | 不同任务应调用哪些上下文 |
| `review_queue/` | 可能重复、冲突或需要人工合并的条目 |
| `evolution_log.md` | 每次资料入库、修正、冲突和更新记录 |

`00_library_index.md` 会由 Library Writer 自动刷新，显示各目录条目数量、待处理队列数量和最近入库记录。

## 4. 入库原则

- 默认先完整转写，再判断是否入库。
- 有识别异常时进入 Exception Review Queue，没有异常则自动进入候选入库。
- 不把一次性价格、临时政策、阶段激励直接提升为长期品牌知识。
- 被否方向、会议决策理由、复盘教训比成品总结更有长期价值。
- 每次派生 brief 或人工修正，都应回流到 `evolution_log.md`。
- 多份品牌资料内容冲突时，参考 source conversion 中记录的原始文件创建/修改时间；通常优先考虑修改时间更新的资料，但关键品牌口径不自动覆盖，进入 `review_queue/updates.md` 或 `review_queue/conflicts.md`。

## 5. 与当前 Skill 的关系

当前 Skill 负责从单次资料包生成：

- `03_marketing_semantic_transcript.md`：完整可读转述。
- `10_context_asset_index.md`：本次资料里的可复用上下文资产。
- `11_context_library_update_plan.md`：如何并入长期品牌上下文知识库。

后续可以再开发真正的 Library Writer，把 update plan 自动写入 `brand_context_library/`。

## 6. 当前 CLI

当前已提供最小 Library Writer：

```bash
brand-skill apply-library-update <project_dir> --library-dir <brand_context_library_dir>
brand-skill build-library-report <brand_context_library_dir>
```

它会读取 `outputs/11_context_library_update_plan.md` 的 `New Context Entries` 表，把 `写入建议` 为 `写入` 或 `暂存` 的条目写入对应目录，并追加 `evolution_log.md`。

当前版本不会自动覆盖旧知识。若同目录下已经存在相同 slug 或相同标题的条目，新条目会进入 `review_queue/conflicts.md`，等待人工判断是补充、替换还是另存。

同时会维护两个运营文件：

- `review_queue/do_not_promote.md`：记录不应提升为长期品牌知识的临时信息、一次性政策或未验证判断。
- `review_queue/updates.md`：记录可能需要补充、修正、替换旧知识的更新请求。
- `retrieval_maps/source_packages.md`：记录本次资料未来适合在哪些任务中被调用，以及不应在哪些场景误用。

`build-library-report` 会生成 `library_report.html`，用于给 marketer 快速查看知识库规模、待处理事项、最近入库内容和后续可复用场景。
