# Work Buddy Handoff Guide｜把 Structured Wiki 交给 Agent 使用

这份文档用于第一阶段之后，把本项目生成的 Markdown Wiki 交给 Work Buddy、Claude、ChatGPT 或其他 Agent 做 GEO / PDP / 种草 / 拍摄 / 销售 / 复盘等后续工作。

核心原则：后续 Agent 应优先读取 Wiki 索引和 source facts，不要重新从一堆 PDF / PPT 里临时猜重点。

## 0. 一句话给同事

```text
我已经把这批资料跑成 Structured Wiki。请先读 outputs/00_source_index.md、outputs/10_context_asset_index.md、outputs/11_context_library_update_plan.md 和 brand_context_library/retrieval_maps/source_packages.md，再按任务需要读取 source_facts；只有遇到识别异常、来源冲突、外发高风险 claim 或资料写着“待确认”时，才回看 transcript / 原 PDF / PPT。
```

最小判断：

- `brand_review.html` 只看有没有漏页、误读、OCR/图片/表格没读清。
- `library_report.html` 只看知识库地图、冲突、待补和后续该读什么。
- `quality_sampling_log.md` 没有人抽样通过前，不要对外宣称“90% 准确”。
- `contract_verification_report.md` 里的 `Quality sampling evidence: pending; no 90% evidence` 也不能当成 90% 准确率证明。

## 1. 给同事的最小使用方式

1. 新建或打开一个项目目录，把本次要处理的 PDF / PPT / DOCX / Markdown / TXT 等资料都放进这个项目目录下的 `source/` 文件夹。
2. 运行本项目的第一阶段流程：

```bash
brand-skill run-phase1 <project_dir> --library-dir <brand_context_library_dir>
```

3. 打开下面两个 HTML：

| 文件 | 用途 |
|---|---|
| `review/brand_review.html` | 看本次资料是否读完整、哪些页没读清、是否需要补截图或换转写引擎 |
| `brand_context_library/library_report.html` | 看当前知识库地图、待处理事项、后续任务应优先读哪些 Wiki 文件 |

4. 如果 `brand_review.html` 没有明显识别异常，且 `library_report.html` 里没有必须先处理的冲突或待补资料，就把这个项目目录和下面的“Work Buddy 任务提示词”交给 Work Buddy。
5. Work Buddy 后续优先读 Structured Wiki，不要一上来重新读原始 PDF / PPT。

如果 `evaluation/quality_sampling_log.md` 还没有人工通过率记录，Work Buddy 仍可使用 Wiki，但不能把它当成已经证明 90% 准确的资料。已有人工记录时，把它当成验收证据；重跑 `build-value-benchmark` 会保留这份日志。

## 2. 后续 Agent 优先读取顺序

让 Work Buddy 先读这些文件：

1. `outputs/00_source_index.md`
2. `outputs/10_context_asset_index.md`
3. `outputs/11_context_library_update_plan.md`
4. `brand_context_library/retrieval_maps/source_packages.md`
5. 任务相关的 `converted_markdown/source_facts/*.md`
6. 需要核对原文时，再读 `converted_markdown/source_transcripts/*.md`

把 Structured Wiki 交给 Work Buddy 时，给它项目目录路径，并要求它按上面的顺序读取。不要默认让 Agent 读取全部 PDF / PPT 原文。

只有下面几种情况需要回到原始 PDF / PPT、截图或 transcript：

- `review/brand_review.html` 或 `source_quality_report.md` 标记页面、表格、图片、小字、OCR 区域没读清。
- source facts 和 transcript 对同一事实说法不一致，或多版本资料互相冲突。
- 后续任务要外发关键 claim、价格、预算、功效、合规表达、竞品判断等高风险内容。
- Structured Wiki 里写了“资料未提供”“待补充”“待确认”，但任务必须给出明确结论。

## 3. Work Buddy 任务提示词

```text
你现在不要直接重新总结原始 PDF / PPT。

我会给你一个已经跑完第一阶段的项目目录。请优先基于这个项目已经生成的 Structured Wiki 工作：

1. 先读取 outputs/00_source_index.md，确认本次资料包包含哪些文件、每份文件大概讲什么、转写稿和 source facts 在哪里。
2. 再读取 outputs/10_context_asset_index.md，判断哪些上下文资产适合当前任务调用。
3. 再读取 outputs/11_context_library_update_plan.md 和 brand_context_library/retrieval_maps/source_packages.md，判断后续任务应优先精读哪些 source facts / transcripts。
4. 当前任务需要事实依据时，优先引用 converted_markdown/source_facts/*.md。
5. 如果 source facts 不够清楚，再回看 converted_markdown/source_transcripts/*.md 中对应页码 / slide。
6. 只有 review/brand_review.html、source_quality_report.md、source facts 或 transcript 明确提示异常、冲突、缺口，或当前任务涉及高风险外发 claim 时，才回到原始 PDF / PPT、截图或对应 transcript 核对。
7. 如果某些页、表格、图片、小字、OCR 区域没有读清楚，请明确说明“不确定”，不要自行补写。

输出要求：
- 只使用 Wiki 或来源中已有的信息。
- 没有资料支持的内容写“资料未提供”。
- AI 推断必须标注“待确认”。
- 不要把来源文本、AI 转述或会议讨论写成品牌方已确认口径。
- 需要引用依据时，写明来自哪个 source facts / transcript / source index。

我的当前任务是：
【在这里填写：例如生成 GEO brief / PDP brief / 种草 brief / 拍摄 brief / 销售话术 / 客服 FAQ / 投放复盘 / 竞品分析】
```

## 4. 不同任务的读取建议

| 任务 | 优先读取 | 精读 | 必要时回看 |
|---|---|---|---|
| GEO brief | `10_context_asset_index.md`、`retrieval_maps/source_packages.md` | 与品牌、产品、用户语言、渠道相关的 source facts | 关键 claim 对应 transcript |
| PDP brief | `00_source_index.md`、产品类 source facts | 产品卖点、功效证据、SKU、使用场景 | 产品培训或检测报告 transcript |
| 种草 brief | `10_context_asset_index.md`、案例/人群/语言类条目 | 用户痛点、场景、表达边界、竞品参考 | 过往种草复盘 transcript |
| 拍摄 brief | `10_context_asset_index.md`、素材/场景/话术条目 | 场景、视觉方向、产品露出要求、禁用表达 | 提案 PPT / campaign transcript |
| 销售话术 | `00_source_index.md`、产品/渠道 source facts | 产品卖点、渠道策略、经销商关注点 | 销售策略或产品培训 transcript |
| 投放复盘 | `source_facts`、case 类 library 条目 | 表现结论、有效素材、失败点、后续动作 | 投放总结 transcript |
| 竞品分析 | network / case / product 相关条目 | 竞品事实、价格带、内容打法、渠道动作 | 竞品详情页转写稿 |

## 5. 使用边界

- Structured Wiki 是 Agent 的优先上下文，不是品牌经理确认过的最终口径。
- `已从来源资料提取` 只表示来源中出现过，不等于可外发。
- `AI 结构化转述，待确认` 不能当作品牌确认。
- 多版本资料冲突时，修改时间更新的文件只是更高优先级线索，不自动覆盖旧知识。
- 真实品牌测试资料只能留在本地私有目录，不进入公开 examples、docs、prompts、schemas 或 README。
