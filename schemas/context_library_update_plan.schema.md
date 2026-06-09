# Schema｜11_context_library_update_plan.md

## 目的

`11_context_library_update_plan.md` 用于把一次资料编译结果并入长期品牌上下文知识库。它不是给单份文件做总结，而是回答：

- 这份资料给长期品牌知识库新增了什么？
- 哪些已有上下文需要更新？
- 哪些内容只是一次性项目资料，不应提升为长期品牌知识？
- 哪些问题需要后续资料或真实业务反馈继续补齐？

## 必须包含的章节

### 1. Library Update Summary

| 字段 | 要求 |
|---|---|
| Source Package | 本次资料包名称或项目名 |
| Update Type | 新增 / 更新 / 冲突待处理 / 仅归档 |
| Recommended Action | 写入长期库 / 暂存待复核 / 不写入长期库 |
| Reason | 为什么这么处理 |

### 2. New Context Entries

| 字段 | 要求 |
|---|---|
| Entry ID | `LCE001` 起连续编号 |
| 建议归档位置 | brand / product / project / asset / language / persona / network / case / decision |
| 标题 | 可读标题 |
| 内容摘要 | 应写入长期知识库的内容 |
| 来源资产 | 引用 `CAxxx` 或来源页码 |
| 稳定性 | 长期稳定 / 项目期有效 / 待验证 |
| 写入建议 | 写入 / 暂存 / 不写入 |

### 3. Existing Context Updates

| 字段 | 要求 |
|---|---|
| 可能影响的已有条目 | 如果不知道，写 `待检索` |
| 更新方式 | 补充 / 修正 / 替换 / 冲突待处理 |
| 新信息 | 本次资料带来的更新 |
| 冲突或风险 | 与旧知识可能不一致的地方 |

### 4. Do Not Promote

记录不应该进入长期品牌知识库的内容，例如一次性价格、阶段性激励、临时渠道政策、未验证猜测、内部敏感执行表。

### 5. Evolution Hooks

| 后续资料类型 | 应补充到哪里 | 触发条件 |
|---|---|---|
| 投放数据 | network / language / case | 活动结束或周报更新 |
| 销售反馈 | product / language / channel | 促销或上市后 |
| 会议纪要 | project / decision / case | 有关键决策或否决理由 |
| 素材表现 | asset / case | 有素材效果数据 |

### 6. Retrieval Notes

写给后续 AI 调用的检索提示：未来在什么任务里应该调用这份资料、不能在什么任务里误用。
