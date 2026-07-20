# 另一台电脑需要完成的真实测试

如果你刚刚从 GitHub 获取这个仓库，请先完成 [安装指引](docs/cross_platform_test_guide.md)，然后按本页做一次真实 WorkBuddy A/B 测试。

## 测试目的

用同一批真实产品资料和同一个 Brief 任务，对比：

- **A｜直接读取**：WorkBuddy 直接读取原始 PDF / PPT / DOCX 后生成 Brief。
- **B｜Wiki 读取**：先用本项目编译 Markdown Wiki，再让 WorkBuddy 基于 Wiki 生成同一份 Brief。

我们不预设 B 一定更好。测试要回答：Wiki 是否减少漏读、版本混淆、无来源结论和重复读取成本。

## 1. 准备真实资料

在仓库内新建：

```text
_private_test_runs/workbuddy_real_brief_ab/
├── source/
└── evaluation/
```

把一次真实工作会共同使用的资料放进 `source/`，建议至少包含：

- 一份产品介绍或培训资料；
- 一份功效、科研或检测资料；
- 一份历史 Brief、内容复盘或渠道资料；
- 有条件时加入同一主题的旧版和新版。

只使用公司允许在该电脑和 WorkBuddy 中处理的资料。该目录已被 Git 忽略，不会被普通提交上传。

## 2. A 组：直接读取原文件

打开一个全新的 WorkBuddy 会话，只提供 `source/`，不要让它读取本项目生成的 Wiki。发送：

```text
请完整读取我提供的 source/ 中全部原始资料，生成一份产品种草内容 Brief。

Brief 必须包含：
1. 本次读取的文件清单；
2. 项目背景与目标；
3. 目标人群与核心洞察；
4. 产品核心价值与传播主张；
5. 有来源支持的关键产品事实、功效和 claim；
6. 三个内容方向，每个方向写清场景、内容钩子和必须带出的信息；
7. 必须遵守的表达边界；
8. 资料冲突、没有提供或没有读清的内容。

要求：
- 不得编造资料中没有的信息；
- 尽量标注事实来自哪个文件、哪一页或哪一张 slide；
- 多版本冲突时说明判断依据，不要静默选一个版本；
- 不追求文案华丽，优先保证完整、准确和可追溯。
```

将完整回答保存为：

```text
evaluation/A_direct_brief.md
```

同时记录从开始读取到完成回答的大致耗时。

## 3. 编译 Wiki

Windows PowerShell：

```powershell
.\.venv\Scripts\brand-skill.exe prepare-wiki `
  ".\_private_test_runs\workbuddy_real_brief_ab"
```

然后在一个新的 WorkBuddy 会话中导入 `v0.1.0` Release 的 Skill ZIP，并发送：

```text
请调用 brand-business-context-compiler Skill，处理这个已经完成 prepare-wiki 的项目目录：
【填写 _private_test_runs/workbuddy_real_brief_ab 的完整路径】

请完整读取 conversion_report、全部 source_transcripts、source_facts、
source_quality_report 和 source_version_report，按照 Skill 的 Schema 生成 wiki/。

要求：
- 每份来源生成一份知识页；
- 来源事实保留真实页码或 slide；
- AI 归纳与来源事实明确区分；
- 资料没有的信息写“资料未提供”；
- 只把真正没读清、缺页、来源冲突或阻塞理解的问题写入 uncertainties.md；
- 不得把所有质量候选页面都变成人工确认项。
```

Wiki 生成后，在 PowerShell 运行：

```powershell
.\.venv\Scripts\brand-skill.exe build-wiki-report `
  ".\_private_test_runs\workbuddy_real_brief_ab"

.\.venv\Scripts\brand-skill.exe verify-wiki `
  ".\_private_test_runs\workbuddy_real_brief_ab"
```

必须看到：

```text
Wiki verification passed.
```

## 4. B 组：基于 Wiki 输出同一份 Brief

再打开一个全新的 WorkBuddy 会话。只让它优先读取 `wiki/`；除非 Wiki 明确标注异常，否则不要重新读取原始文件。发送：

```text
请基于这个项目已经生成的 Markdown Wiki，生成一份产品种草内容 Brief。

请先读 wiki/00_index.md，再按任务读取 wiki/documents/ 中相关知识页，
并检查 wiki/uncertainties.md。除非 Wiki 明确标注未读清或来源冲突，
否则不要重新读取 source/ 中的原始文件。

Brief 必须包含：
1. 本次读取的文件清单；
2. 项目背景与目标；
3. 目标人群与核心洞察；
4. 产品核心价值与传播主张；
5. 有来源支持的关键产品事实、功效和 claim；
6. 三个内容方向，每个方向写清场景、内容钩子和必须带出的信息；
7. 必须遵守的表达边界；
8. 资料冲突、没有提供或没有读清的内容。

要求：
- 不得编造 Wiki 或来源中没有的信息；
- 关键事实尽量保留 Source ID 与页码 / slide；
- AI 推断必须写“待确认”；
- 不追求文案华丽，优先保证完整、准确和可追溯。
```

将完整回答保存为：

```text
evaluation/B_wiki_brief.md
```

同时记录从开始读取到完成回答的大致耗时。

## 5. 对比 A 与 B

打开第三个全新会话，让 WorkBuddy 或 Codex 同时读取 A、B 两份结果和原始资料，发送：

```text
请对 A_direct_brief.md 和 B_wiki_brief.md 做中立对比。不要预设任何一方获胜。

请逐项按 1-5 分评分并给出原文件证据：
1. 信息完整性：是否覆盖所有对任务重要的资料；
2. 来源可追溯性：关键事实能否找到文件和页码 / slide；
3. 版本处理：是否识别旧版、新版和冲突；
4. 事实可靠性：是否出现无来源数字、claim 或 AI 编造；
5. Brief 可用性：是否能直接交给内容、媒介或代理商执行；
6. 再次调用成本：下次换任务时是否需要重新读取全部原文件。

最后明确回答：
- A 更好、B 更好，还是各有优势；
- Wiki 真正改善了什么；
- Wiki 没有改善什么；
- 本项目下一步只需要修复的一个最重要问题是什么。
```

将结果保存为：

```text
evaluation/comparison_report.md
```

## 6. 测试完成后反馈

把以下信息发给项目维护者即可，不需要提交真实资料：

```text
操作系统：
WorkBuddy 版本：
来源文件数 / 类型 / 总页数：
是否包含真实旧版与新版：
prepare-wiki 是否成功：
verify-wiki 是否通过：
A 组耗时：
B 组耗时：
对比结论：
最严重的一个问题：
comparison_report.md 路径：
```

如果公司政策允许，也可以把 `_private_test_runs/workbuddy_real_brief_ab/` 保留在私有电脑上供 Codex排查，但不要默认提交真实产品资料、商业数据或内部 Brief。
