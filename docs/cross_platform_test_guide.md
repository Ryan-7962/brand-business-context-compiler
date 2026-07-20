# 换电脑安装与测试

安装完成后，请继续执行仓库根目录的 [真实 WorkBuddy A/B 测试任务](../TEST_ON_ANOTHER_COMPUTER.md)。它会说明另一台电脑需要提供哪些真实资料、如何生成同一份 Brief，以及如何比较直接读取和 Wiki 读取。

本项目由两部分组成：

- 完整 GitHub 仓库：负责 PDF / PPT / DOCX 转写、页码锚点、版本线索和校验。
- WorkBuddy / Codex Skill ZIP：告诉 Agent 如何把转写结果编译成 Markdown Wiki。

## Windows：最短安装

先安装 Git、Python 3.11 和 Codex，然后在 PowerShell 执行：

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

重启 Codex。确认 CLI 可用：

```powershell
.\.venv\Scripts\brand-skill.exe --help
```

## macOS：最短安装

```bash
git clone https://github.com/Ryan-7962/brand-business-context-compiler.git
cd brand-business-context-compiler

python3.11 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python scripts/build_workbuddy_package.py

mkdir -p "$HOME/.codex/skills"
unzip -o dist/brand-business-context-compiler-workbuddy.zip -d "$HOME/.codex/skills"
```

重启 Codex，然后运行：

```bash
.venv/bin/brand-skill --help
```

## 第一次真实测试

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

## WorkBuddy 测试

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
