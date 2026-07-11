# WorkBuddy 真实验证清单

## 当前状态

**部分验证。** 2026-07-11 已在 macOS WorkBuddy 5.2.5 使用官方 CLI API 完成认证连通测试，并从临时项目的 `.codebuddy/skills/` 加载 ZIP：`brand-business-context-compiler` 被正确发现，且返回了 Skill 中定义的完整核心流程。尚未完成真实来源文件的 Wiki 编译、重复办公任务验证，以及公司电脑环境验证。

## 准备

- [x] 使用 `python scripts/build_workbuddy_package.py` 构建 `dist/brand-business-context-compiler-workbuddy.zip`。
- [x] 确认 ZIP 仅含 `SKILL.md`、Wiki schema 和 Wiki 编译 prompt 三个公开文件。
- [ ] 准备一个已获授权、可在公司电脑上处理的来源文件夹；不要把私有资料复制进仓库、ZIP 或本清单。

## WorkBuddy 导入与触发

- [ ] 在 WorkBuddy 导入 ZIP，并记录导入日期、操作者和可复现的界面证据位置。
- [x] 在本机 CLI 临时项目中确认 `brand-business-context-compiler` 可被发现并执行；公司电脑界面仍待验证。
- [ ] 对准备好的来源文件夹发起一次任务，确认 WorkBuddy 触发该 Skill；记录任务入口和触发结果。

## 必须保留的 Wiki 产物

- [ ] `wiki/00_index.md` 已创建，并覆盖该批次全部来源文件。
- [ ] `wiki/documents/<source-id>.md` 已为每个来源创建一页知识页。
- [ ] `wiki/uncertainties.md` 已创建，并记录真实异常或明确说明没有异常。
- [ ] WorkBuddy 未读取的文件、页面、表格、图片、小字或 OCR 区域已逐项如实写入 `wiki/uncertainties.md`；没有未读内容时，也要记录检查结论。

## 办公任务验证

- [ ] 选择一个代表性办公任务，要求 WorkBuddy 优先读取 `wiki/00_index.md` 和相关知识页，而非重新总结原始文件。
- [ ] 记录任务名称、使用的 Wiki 文件、输出位置和需要回看来源的例外。
- [ ] 确认输出没有把资料转述、AI 推断或未确认内容写成已确认的品牌口径。

## 完成记录

完成后在本节填写：公司电脑导入证据位置、触发任务链接或截图位置、来源批次标识、三类 Wiki 产物路径、未读内容记录、办公任务结果，以及仍存在的限制。在这些证据齐全前，保持本清单的“部分验证”状态。
