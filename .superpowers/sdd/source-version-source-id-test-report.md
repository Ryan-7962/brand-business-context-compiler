# Source ID 去重测试报告

## 变更

- 仅在 `tests/test_phase1_workflow.py` 新增测试。
- 覆盖 S001/S002 使用相同原始文件名、相同转写 Markdown 路径，且各自存在两条完全重复逐页行的场景。
- 断言报告显示 `来源文件数：2`，验证去重键包含 `source_id`。

## 验证

- `tests/test_phase1_workflow.py::Phase1WorkflowTests::test_build_source_version_report_deduplication_key_includes_source_id`：1 passed
- `tests/test_phase1_workflow.py`：107 passed，2 warnings，5 subtests passed
- `tests/test_wiki_workflow.py`：32 passed
