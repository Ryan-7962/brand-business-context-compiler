# 换电脑安装与测试

默认先测单次转译；确实需要持续建库时，再执行仓库根目录的 [真实 WorkBuddy A/B 测试任务](../TEST_ON_ANOTHER_COMPUTER.md)，比较直接读取和 Wiki 读取。

本项目由两部分组成：

- 完整 GitHub 仓库：负责 PDF / PPT / DOCX 转写、页码锚点、版本线索和校验。
- WorkBuddy / Codex Skill ZIP：默认编译详细结构化MD，明确要求建库时才生成Wiki。宿主Agent能完整读文件时，单次转换不要求安装CLI。

## 单次测试（默认）

普通同事下载明确的[v0.2.0-pilot.1试用版](https://github.com/Ryan-7962/brand-business-context-compiler/releases/tag/v0.2.0-pilot.1)，不要误用旧版latest。Windows先用一份授权PDF和一份PPTX试跑，再基于MD生成一份实际brief；保留输出、WorkBuddy版本/模型、实际页数与具体异常。无须逐条人工批准，也不将真实资料上传GitHub。

导入最新生成的 Skill ZIP 后，在 Codex 或 WorkBuddy 中发送：

```text
调用 brand-business-context-compiler，将【文件或文件夹完整路径】转为详细的中文MD。
只做单次转换，不建Wiki、不生成HTML。保留完整正文、表格、数据条件、香型/产品区别和来源位置，不要只给摘要。
全部文件和页/slide都要登记；实际没读清的关键区域才告诉我具体位置和补救方式。
输出到【指定目录】，不要覆盖原件或已有结果。
```

验收：每份文件有可用MD，大纲与正文对应，关键事实和条件可回源，读取状态真实；没有额外生成知识库、强制确认表或HTML。多文件仍可单次交付。下面的CLI安装步骤是可选辅助工具，Wiki步骤只在明确建库时执行。

## Windows：最短安装

普通同事优先按[中文使用说明](work_buddy_handoff_guide.md)直接导入ZIP，不需要开发环境。以下仅用于开发或备用转换工具。先安装 Git、Python 3.11 和 Codex，然后在 PowerShell 执行：

```powershell
git clone --branch codex/agent-neutral-wiki-v1 https://github.com/Ryan-7962/brand-business-context-compiler.git
cd brand-business-context-compiler

py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe scripts\build_workbuddy_package.py

New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
if (Test-Path "$env:USERPROFILE\.codex\skills\brand-business-context-compiler") {
  throw "同名Skill已存在，请先保留旧版并确认升级，不自动覆盖。"
}
Expand-Archive .\dist\brand-business-context-compiler-workbuddy.zip `
  -DestinationPath "$env:USERPROFILE\.codex\skills"
```

重启 Codex。确认 CLI 可用：

```powershell
.\.venv\Scripts\brand-skill.exe --help
```

## macOS：最短安装

```bash
git clone --branch codex/agent-neutral-wiki-v1 https://github.com/Ryan-7962/brand-business-context-compiler.git
cd brand-business-context-compiler

python3.11 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python scripts/build_workbuddy_package.py

mkdir -p "$HOME/.codex/skills"
if [ -e "$HOME/.codex/skills/brand-business-context-compiler" ]; then
  printf '%s\n' '同名Skill已存在，请先保留旧版并确认升级。'
else
  unzip dist/brand-business-context-compiler-workbuddy.zip -d "$HOME/.codex/skills"
fi
```

重启 Codex，然后运行：

```bash
.venv/bin/brand-skill --help
```

## 持续建库测试（按需）

新建一个项目，并把已获授权的 PDF / PPTX / DOCX / MD / TXT 放进 `source/`：

Windows：

```powershell
.\.venv\Scripts\brand-skill.exe init "D:\BrandWiki\test-project"
.\.venv\Scripts\brand-skill.exe prepare-wiki "D:\BrandWiki\test-project"
```

macOS：

```bash
.venv/bin/brand-skill init "$HOME/BrandWiki/test-project"
.venv/bin/brand-skill prepare-wiki "$HOME/BrandWiki/test-project"
```

`prepare-wiki` 完成后，在 Codex 中发送：

```text
请调用 brand-business-context-compiler Skill，处理这个项目目录：
【填写 test-project 的完整路径】

请完整读取 prepared evidence，按照 Skill 的 Wiki Schema 生成 wiki/。
只把真正没读清、缺页、来源冲突或阻塞理解的问题写入 uncertainties.md。
不要编造资料没有的信息。完成后生成中文报告并运行 verify-wiki。
```

成功标准：

- `wiki/00_index.md` 存在，并列全所有来源文件。
- `wiki/documents/` 中每个来源都有知识页。
- `wiki/uncertainties.md` 只列真实异常。
- `wiki/report.html` 可以打开。
- `verify-wiki` 输出 `Wiki verification passed.`。

## WorkBuddy 建库测试（按需）

从 GitHub Releases 下载 `brand-business-context-compiler-workbuddy.zip`，在 WorkBuddy 的 Skill 管理界面导入。

推荐先由本仓库 CLI 运行 `prepare-wiki`，再让 WorkBuddy 读取该项目目录。WorkBuddy 中发送：

```text
请调用 brand-business-context-compiler Skill，读取这个已经完成 prepare-wiki 的项目目录：
【填写项目完整路径】

请基于全部 source transcripts 和 evidence 编译 wiki/，不要直接做普通 PDF 摘要。
来源事实保留页码或 slide；AI 归纳必须明确标记；资料没有的信息写“资料未提供”。
只上报真正需要人工处理的读取异常。
```

## 遇到问题时怎么反馈

不要先增加功能。把下面四项交给 Codex：

1. 出问题的原文件类型和页码。
2. `converted_markdown/` 与 `wiki/` 的实际结果。
3. 预期结果和实际结果的差异。
4. `verify-wiki` 或终端的完整报错。

真实品牌资料、商业数据和公司内部文件不要提交到 GitHub；它们只放在本机项目目录或仓库忽略的 `_private_test_runs/`。
