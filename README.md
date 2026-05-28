# cursor-universal-rule

通用 Cursor **项目规则**包：新开仓库后安装到项目的 `.cursor/`，在 **本地 Desktop** 与 **Cloud Agent** 下共用同一套规则文件（文件中分「本地 / 云端」条款，而不是两套 Git 文件）。

仓库：<https://github.com/wangyuanzhong/cursor-universal-rule>

## 覆盖能力

| # | 能力 | 规则文件 |
|---|------|----------|
| 1 | EXE 项目：本地自动打包；云端 CI 必须含 release exe 构建 | `exe-packaging-local-cloud.mdc` |
| 2 | 云端：push 后盯 GitHub Actions，红则修到绿；修复不得与上下文及项目内 `.md`/`.txt` 中的功能/UI 定义冲突 | `post-push-ci-green.mdc` |
| 3 | 改动结束前（push 前，或无 push 要求则任务结束前）：遍历并升级项目内 `.md`/`.txt`，与代码一致 | `docs-sync-before-finish.mdc` |
| 4 | `.gitignore` 不得阻止 `.cursor/` 进 Git | `git-track-cursor-folder.mdc` |
| — | 总纲：完成定义、冲突优先级 | `00-universal-core.mdc` |

## 重要说明（必读）

Cursor **Rule 是约束 Agent 的说明书**，不会在保存文件时自动执行 PowerShell，也 **不能** 100% 替代：

- 本机 `git hook` / 文件监视脚本（真·自动打包）
- GitHub Actions（云端真· CI）

本包把「该做什么」写进 **alwaysApply 项目规则**，并配合 **skills** 与 **安装脚本**，尽量让 Agent **每次会话都看到同一标准**。若要「绝不漏打包」，请同时在项目里保留 `build-release.ps1` 等脚本，并按 README 启用 hook / 监视。

## 安装到新项目

在 **目标仓库根目录** 执行（PowerShell）：

```powershell
# 克隆本仓库一次
git clone https://github.com/wangyuanzhong/cursor-universal-rule.git $env:TEMP\cursor-universal-rule

# 安装规则 + skill + 修正 .gitignore
& "$env:TEMP\cursor-universal-rule\scripts\install-universal-rules.ps1" -ProjectRoot .

# 可选：把「用户级摘要」复制到剪贴板，粘贴到 Cursor → Settings → Rules → User Rules
& "$env:TEMP\cursor-universal-rule\scripts\install-universal-rules.ps1" -InstallUserRulesClipboard
```

或指定本仓库路径：

```powershell
.\scripts\install-universal-rules.ps1 -ProjectRoot "C:\path\to\your-app" -UniversalRepo "C:\path\to\cursor-universal-rule"
```

安装结果：

- `.cursor/rules/*.mdc` — 项目规则（进 Git，Cloud / 本地同源）
- `.cursor/skills/github-actions-ci/SKILL.md` — CI 排错 playbook
- `.cursor/README.md` — 说明
- 若 `.gitignore` 忽略了 `.cursor/`，脚本会尝试移除整目录忽略（保留 `agent-transcripts/` 等常见例外）

## 本地不想启用「push 后盯 CI」

默认 **云端** 执行 `post-push-ci-green.mdc`；**本地 Desktop** 若不想盯 Actions：

```powershell
New-Item -ItemType File -Path .cursor\.local-skip-post-push-ci -Force
```

或在已安装 ASR 类仓库使用：`scripts/cursor-local-opt-out-post-push-ci.ps1`（若项目自带）。

## 目录结构

```
cursor-universal-rule/
├── README.md
├── rules/                          # 源规则（安装时复制到项目的 .cursor/rules/）
├── skills/github-actions-ci/
├── user-rules/                     # 可选：粘贴到 Cursor User Rules 的摘要
└── scripts/
    └── install-universal-rules.ps1
```

## 与 array-mic-refreshment 的关系

本包由 [array-mic-refreshment](https://github.com/wangyuanzhong/array-mic-refreshment) 实践中的全局 User Rule、项目 `.cursor/rules` 与 CI skill 归纳而来，并改为 **通用措辞**（不绑定单一产品名）。

## License

MIT
