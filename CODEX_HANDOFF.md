# Windows Codex 项目交接

## 你接手的项目

这是一个本地优先、AI 驱动的 Brand / Business Context Compiler。它把多份 PDF / PPT / DOCX 等人类阅读型资料编译成可追溯、可检索、可持续更新的 Markdown Wiki。

GitHub 仓库：

```text
https://github.com/Ryan-7962/brand-business-context-compiler
```

当前稳定基线是远程 `main`；接手前先执行 `git pull --ff-only`，不要依赖文档中写死的提交号。

## 当前状态

第一阶段已经完成，不需要重新设计产品或继续堆功能。已有能力包括：

- PDF / PPTX / DOCX / MD / TXT 基础转写；
- 页码 / slide、文件时间和版本线索；
- source transcripts、source facts 和质量报告；
- Agent-neutral Markdown Wiki；
- 中文 HTML 报告和结构校验；
- Codex 与 WorkBuddy Skill 包；
- macOS 本地真实资料验证；
- `148` 项测试通过。

当前最重要的下一步不是继续开发，而是在 Windows 公司环境中完成一次真实 WorkBuddy A/B：同一批真实产品资料、同一个种草 Brief，比较直接读取原文件与基于 Wiki 读取。

## 开始前必须阅读

按顺序读取：

1. `docs/project_goal.md`
2. `docs/phase1_completion_audit.md`
3. `TEST_ON_ANOTHER_COMPUTER.md`
4. `docs/cross_platform_test_guide.md`
5. `SKILL.md`
6. `README.md`

不要根据旧文件名把项目误解为单一“产品资料转 MD”工具，也不要把它扩展成 Web App、企业级 RAG 或完整下游营销内容平台。

## Windows 环境初始化

```powershell
git clone https://github.com/Ryan-7962/brand-business-context-compiler.git
cd brand-business-context-compiler

py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe scripts\build_workbuddy_package.py

New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Expand-Archive .\dist\brand-business-context-compiler-workbuddy.zip `
  -DestinationPath "$env:USERPROFILE\.codex\skills" -Force
```

重启 Codex，然后验证：

```powershell
.\.venv\Scripts\brand-skill.exe --help
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pytest -q
```

## 接手后的第一项任务

严格执行 `TEST_ON_ANOTHER_COMPUTER.md`：

1. 在 `_private_test_runs/workbuddy_real_brief_ab/source/` 放入获授权的真实产品资料。
2. 用新的 WorkBuddy 会话完成 A 组：直接读原文件生成种草 Brief。
3. 运行 `prepare-wiki`。
4. 导入 WorkBuddy Skill，编译 `wiki/`。
5. 用另一个新会话完成 B 组：基于 Wiki 生成相同 Brief。
6. 用第三个会话中立比较 A/B。
7. 保存 `A_direct_brief.md`、`B_wiki_brief.md` 和 `comparison_report.md`。
8. 只根据真实测试暴露的问题决定是否修改代码。

## 开发原则

- 先复现，再修改；不能复现的问题不加功能。
- 确定性代码只负责文件处理和证据，AI 负责语义理解。
- 最小修改，优先复用现有实现。
- 不新增 Web UI、数据库、RAG、复杂模型 API 或下游 Brief 系统。
- 不把所有质量候选页变成人工确认项。
- 不宣称 90% 准确率，除非有人完成原页抽样并留下证据。
- 原文件是事实依据；AI 归纳、资料缺失和来源事实必须区分。
- 真实公司资料留在 `_private_test_runs/` 或仓库外，不默认提交到 GitHub。
- 即使仓库是私有的，也要遵守公司对品牌资料和商业数据的存储规定。

## 修改代码时的 Git 流程

不要直接在 `main` 上试验：

```powershell
git pull --ff-only
git switch -c codex/windows-workbuddy-test
```

每次只提交一个真实问题的修复。提交前运行：

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\brand-skill.exe verify-wiki `
  ".\_private_test_runs\workbuddy_real_brief_ab"
git diff --check
git status --short
```

测试通过后推送：

```powershell
git push -u origin codex/windows-workbuddy-test
```

## 什么情况下才继续开发

只有 A/B 或真实 Windows 运行出现下面的问题才改代码：

- 支持文件被漏掉或页数不一致；
- 图片、表格、OCR 或阅读顺序造成真实信息缺失；
- 文件版本判断错误；
- Wiki 主题、大纲或事实明显偏离原资料；
- `uncertainties.md` 误报大量无需人工处理的问题；
- WorkBuddy 无法发现 Skill、读取项目或生成符合 Schema 的 Wiki；
- Windows 路径、编码或命令兼容性错误。

没有真实问题时，停止开发并提交测试报告，不要为了“优化”增加代码。

## 接力完成后需要汇报

```text
Windows 版本：
Codex 版本：
WorkBuddy 版本：
测试资料文件数 / 类型 / 页数：
A/B 是否完成：
verify-wiki 是否通过：
A/B 对比结论：
发现的真实问题：
修改的文件和提交：
仍需 Ryan 确认的事项：
```
