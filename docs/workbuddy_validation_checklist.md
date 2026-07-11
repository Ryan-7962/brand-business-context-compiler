# WorkBuddy 真实验证清单

## 当前状态

**本机端到端验证通过，公司环境待验证。** 2026-07-11 已在 macOS WorkBuddy 5.2.5 完成 CLI 认证连通、Skill 发现和匿名来源到 Wiki 的完整编译。WorkBuddy 完整读取 6/6 页，创建 `wiki/00_index.md`、`wiki/documents/S001.md` 和 `wiki/uncertainties.md`；异常数为 0，外部 `verify-wiki` 通过。尚未完成重复办公任务验证和公司电脑环境验证。

## 准备

- [x] 使用 `python scripts/build_workbuddy_package.py` 构建 `dist/brand-business-context-compiler-workbuddy.zip`。
- [x] 确认 ZIP 仅含 `SKILL.md`、Wiki schema 和 Wiki 编译 prompt 三个公开文件。
- [ ] 准备一个已获授权、可在公司电脑上处理的来源文件夹；不要把私有资料复制进仓库、ZIP 或本清单。

## WorkBuddy 导入与触发

- [ ] 在 WorkBuddy 导入 ZIP，并记录导入日期、操作者和可复现的界面证据位置。
- [x] 在本机 CLI 临时项目中确认 `brand-business-context-compiler` 可被发现并执行；公司电脑界面仍待验证。
- [x] 在本机匿名样例上触发该 Skill，并完成来源到 Wiki 的语义编译；公司资料批次仍待验证。

## 必须保留的 Wiki 产物

- [x] 本机匿名样例的 `wiki/00_index.md` 已创建，并覆盖该批次全部来源文件。
- [x] 本机匿名样例的 `wiki/documents/<source-id>.md` 已为每个来源创建一页知识页。
- [x] 本机匿名样例的 `wiki/uncertainties.md` 已创建，并明确说明没有人工异常。
- [x] 本机匿名样例 6/6 页均已读取，无 OCR 或页面缺失；更复杂的真实文件仍需继续验证。

## 办公任务验证

- [ ] 选择一个代表性办公任务，要求 WorkBuddy 优先读取 `wiki/00_index.md` 和相关知识页，而非重新总结原始文件。
- [ ] 记录任务名称、使用的 Wiki 文件、输出位置和需要回看来源的例外。
- [ ] 确认输出没有把资料转述、AI 推断或未确认内容写成已确认的品牌口径。

## 完成记录

本机验证使用隔离临时目录和匿名公开样例，未保留 API Key，也未将私有品牌资料写入公开产物。公司电脑仍需补充界面导入证据、真实授权批次、重复办公任务结果和相应 Wiki 路径；在这些证据齐全前，不声明公司环境验证完成。
