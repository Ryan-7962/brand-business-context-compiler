# Source Version Real-Run Fix Report

## 红灯

- 新增两个最小回归测试，使用真实 16 列 conversion report：页级重复行分别覆盖无版本组和 v1/v2 版本组场景。
- 修复前测试结果：2 failed。
- 失败证据：来源文件数分别为 5/4，页级重复行被重复计数并形成虚假版本组；版本组表格也重复渲染同一 source。

## 绿灯

- 在 `_parse_conversion_report` 中按 `来源编号 + 原始文件 + 转写 Markdown` 折叠逐页行，保留每组首行元数据。
- 未修改 conversion report，也未新增抽象层。
- 聚焦回归测试：2 passed。
- `tests/test_phase1_workflow.py`：106 passed，2 warnings。
- `tests/test_wiki_workflow.py`：32 passed。

## Commit

- `b8e4ea9dd03b4d004f4f2e10f165d0f5a1f6e89e` (`fix: deduplicate source version report rows`)

## Concerns

- 测试仍有 PyMuPDF/系统绑定触发的既存 `DeprecationWarning`，不影响通过结果。
- 折叠键只使用 Source ID、原始文件和转写 Markdown；同一三元组若页级元数据不一致，当前保留首行，需由上游 conversion report 另行校验。
