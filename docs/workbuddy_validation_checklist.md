# WorkBuddy 真实验证清单

## 当前状态

**尚未验证。** 本清单记录需要在公司电脑的 WorkBuddy 界面完成的真实导入和运行证据。ZIP 的本地构建与自动隐私检查不能证明 WorkBuddy 已导入、已触发或已完成语义编译。

## 准备

- [ ] 使用 `python scripts/build_workbuddy_package.py` 构建 `dist/brand-business-context-compiler-workbuddy.zip`。
- [ ] 确认 ZIP 仅含 `SKILL.md`、Wiki schema 和 Wiki 编译 prompt 三个公开文件。
- [ ] 准备一个已获授权、可在公司电脑上处理的来源文件夹；不要把私有资料复制进仓库、ZIP 或本清单。

## WorkBuddy 导入与触发

- [ ] 在 WorkBuddy 导入 ZIP，并记录导入日期、操作者和可复现的界面证据位置。
- [ ] 确认 `brand-business-context-compiler` 出现在可用 Skill 列表中。
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

完成后在本节填写：导入证据位置、触发任务链接或截图位置、来源批次标识、三类 Wiki 产物路径、未读内容记录、办公任务结果，以及仍存在的限制。没有这些证据前，保持本清单的“尚未验证”状态。
