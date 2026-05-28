# cursor-universal-rule

通用 Cursor **项目规则**包：新开仓库后安装到项目的 `.cursor/`，在 **本地 Desktop** 与 **Cloud Agent** 下共用同一套规则文件（文件中分「本地 / 云端」条款，而不是两套 Git 文件）。

仓库：<https://github.com/wangyuanzhong/cursor-universal-rule>

## 覆盖能力

| # | 能力 | 规则文件 |
|---|------|----------|
| 1 | EXE 项目：本地自动打包；云端 CI 必须含 release exe 构建 | `exe-packaging-local-cloud.mdc` |
| 2 | push 后（云/本地都要）盯 GitHub Actions 直到绿；修复不得违反项目内 `.md`/`.txt` 中的功能/UI 定义 | `post-push-ci-green.mdc` |
| 3 | 改动结束前（push 前，或无 push 要求则任务结束前）：遍历并升级项目内 `.md`/`.txt`、维护 `.gitignore`、扫描密钥泄漏 | `docs-sync-before-finish.mdc` |
| 4 | `.gitignore` 不得阻止 `.cursor/` 进 Git | `git-track-cursor-folder.mdc` |
| 5 | 本地：每次完整回复改了文件就自动 commit + push 到当前分支（仓库 opt-in） | `local-auto-push-current-branch.mdc` |
| 6 | 每次 push 都 bump SemVer + 写详细 `CHANGELOG.md` entry；commit 用 Conventional Commits | `versioning-and-changelog.mdc` |
| — | 总纲：模式声明、Done check、冲突优先级、子 agent push 策略 | `00-universal-core.mdc` |

## 规则风格（v2）

为提高 Agent 的执行率，所有 `.mdc` 已统一为下列结构，避免散文化和模糊语气：

- **When this rule fires** — 一句话触发条件，不命中就在 Done check 里写 `N/A: <reason>` 跳过。
- **You MUST** — 硬约束，编号短句，可直接对照执行。
- **You MUST NOT** — 明确的负面清单。
- **Required output / Stop conditions** — 任务结束时必须输出哪些信息、何时停止重试。

`00-universal-core.mdc` 还要求 Agent：

1. 在计划中写一行 `MODE: Local` / `MODE: Cloud` / `MODE: ambiguous — blocking`，单次任务只判定一次；判定算法见该文件。
2. 在最终消息里**逐项打勾输出 Done check**（`done` / `N/A: <reason>` / `blocked: <reason>`），任何 `blocked` 必须停下来报给用户，不得越过。

## 模式判定（Cloud vs Local）

`00-universal-core.mdc` 给出确定性算法（任一命中即 Cloud）：

1. 系统 prompt 里出现 `<cloud_task_instructions>` 块，或字面 `running as a CLOUD AGENT`。这是 Cursor Cloud Agent 平台注入的、Local Desktop 永远不会出现的 marker。
2. `uname -s = Linux` 且 `pwd` 以 `/workspace` 或 `/home/ubuntu/` 开头。
3. 环境变量 `CI=true`，或仓库根存在 `.cursor/cloud-agent-marker`。

都不命中且 cwd 在开发者家目录 → `MODE: Local`。出现矛盾信号（典型：WSL 上的 Local 开发）→ `MODE: ambiguous — blocking`，停下来问用户，**禁止默认 Local**。

## 本地自动 push（opt-in）

`local-auto-push-current-branch.mdc` 默认**不启用**。要让 Agent 在每次完整回复改了项目文件后自动 commit + push 到当前分支，在仓库根做一次：

```bash
mkdir -p .cursor && touch .cursor/.local-auto-push
git add .cursor/.local-auto-push
git commit -m "chore(cursor): enable local auto-push for current branch"
```

启用后规则强制：

- 推**当前分支**到对应远端分支，永远不直推 main（除非你本来就在 main 上）。
- 必须先过 pre-push hygiene（文档同步、`.gitignore` 检查、密钥扫描）和版本号 bump（见下）。
- 推完必须盯 CI 到绿（无 Local opt-out）。
- 永不 `--force` / `--force-with-lease`；非 fast-forward / 检测到密钥 / detached HEAD / 进行中的 merge-rebase → 一律停下报你。

详见 `templates/local-auto-push-marker.md`。

## 版本号 + CHANGELOG（每次 push）

`versioning-and-changelog.mdc` 强制：

- 仓库根 `CHANGELOG.md`，[Keep a Changelog](https://keepachangelog.com) 格式 + [SemVer](https://semver.org)。
- 默认 bump = `PATCH`。`MINOR` 用于新增功能，`MAJOR` 用于破坏性变更（必须写 `Bump reason:`）。
- 每个 entry 包含：一段总结、`### Added/Changed/Fixed/Removed/Breaking`、`### Files / modules touched`、`### Verify`，详细到能让 handoff 的另一个 agent 不读 diff 就能理解这次改动。
- 自动同步 `package.json#version`、`Cargo.toml#package.version`、`pyproject.toml`、`*.csproj#Version`、仓库根 `VERSION`（哪个存在就同步哪个）。
- commit message 用 [Conventional Commits](https://www.conventionalcommits.org)：`<type>(<scope>): <subject>`，type ∈ `{feat, fix, docs, refactor, test, chore, build, ci, perf, revert}`。type → bump：`feat`=MINOR；`fix`/`perf`=PATCH；其它=PATCH；footer 含 `BREAKING CHANGE:` → MAJOR。
- entry 用项目 `README.md` 的主语言。

仓库初始化用 `templates/CHANGELOG-initial.md` 作起点。

## 子 agent 是否可以 push

`00-universal-core.mdc` 区分两种场景：

- **Scenario A — 隔离 worktree 的子 agent**（`best-of-n-runner`，或子 agent 的 `git rev-parse --git-dir` 与顶层不同）：可以 commit + push 自己的分支，自己维护 CHANGELOG entry。顶层 agent 在合并时再去重 / 整合。
- **Scenario B — 与顶层共享工作区的子 agent**（默认的 `generalPurpose`/`explore`）：**禁止** `git add`/`git commit`/`git push`。改动留在工作区，由顶层 agent 在自己回复结束时统一 commit + push。

无法判断时按 Scenario B。

## CI watch 不再可关闭

旧版规则曾允许在仓库里放 `.cursor/.local-skip-post-push-ci` 让 Local 跳过盯 CI。**新版完全废除该开关**。如果你的仓库还有这个文件，可以删掉，规则不再读它。理由：本地 auto-push 启用后再让 CI 不盯，会让 main / 工作分支静悄悄地红着，得不偿失。

## 重要说明（必读）

Cursor **Rule 是约束 Agent 的说明书**，不会在保存文件时自动执行 PowerShell，也 **不能** 100% 替代：

- 本机 `git hook` / 文件监视脚本（真·自动打包）
- GitHub Actions（云端真· CI）

本包把「该做什么」写进 **alwaysApply 项目规则**，并配合 **skills** 与 **安装脚本**，尽量让 Agent **每次会话都看到同一标准**。若要「绝不漏打包」，请同时在项目里保留 `build-release.ps1` 等脚本，并按 README 启用 hook / 监视。

## 安装到新项目

规则就是几个 Markdown 文件，**直接复制即可**，没有安装脚本。

```bash
git clone https://github.com/wangyuanzhong/cursor-universal-rule.git /tmp/cursor-universal-rule

cd /path/to/your-repo
mkdir -p .cursor
cp -r /tmp/cursor-universal-rule/rules   .cursor/rules
cp -r /tmp/cursor-universal-rule/skills  .cursor/skills

git add .cursor/
git commit -m "chore(cursor): install universal rules pack"
```

PowerShell 等价写法：

```powershell
git clone https://github.com/wangyuanzhong/cursor-universal-rule.git $env:TEMP\cursor-universal-rule

cd C:\path\to\your-repo
New-Item -ItemType Directory -Path .cursor -Force | Out-Null
Copy-Item "$env:TEMP\cursor-universal-rule\rules"  .cursor\rules  -Recurse -Force
Copy-Item "$env:TEMP\cursor-universal-rule\skills" .cursor\skills -Recurse -Force

git add .cursor\
git commit -m "chore(cursor): install universal rules pack"
```

安装后：

- `.cursor/rules/*.mdc` — 项目规则（进 Git，Cloud / 本地同源）
- `.cursor/skills/github-actions-ci/SKILL.md` — CI 排错 playbook

如果你的 `.gitignore` 之前整个目录忽略了 `.cursor/`（`.cursor/`、`.cursor/*`、`.cursor/**`），需要手工删掉这几行；本仓库的 `git-track-cursor-folder.mdc` 规则会强制 Agent 在第一次 push 前自检 `git check-ignore -v .cursor`，所以不删它会被 Agent 卡住报你。

User Rules 摘要（可选，粘进 Cursor → Settings → Rules → User Rules）：

```bash
cat /tmp/cursor-universal-rule/user-rules/SUMMARY-for-cursor-settings.md
```

可选附加（按需手工复制，**不**自动放进项目，避免覆盖已有文件 / 静悄悄启用 CI）：

- `templates/CHANGELOG-initial.md` → 仓库根 `CHANGELOG.md`（首次启用版本号管理时）
- `templates/github-workflow-build-release-exe.yml` → `.github/workflows/build-release-exe.yml`（EXE 项目）
- `templates/local-auto-push-marker.md` → 本地 auto-push 启用方法说明

## 目录结构

```
cursor-universal-rule/
├── README.md
├── CHANGELOG.md                    # 本仓库的版本历史（按 versioning-and-changelog.mdc 维护）
├── rules/                          # 源规则（手工复制到项目的 .cursor/rules/）
├── skills/github-actions-ci/       # CI 排错 playbook
├── templates/                      # 可选模板（CHANGELOG / CI workflow / 启用说明）
├── user-rules/                     # 可选：粘贴到 Cursor User Rules 的摘要
└── .github/                        # 本仓库自校验 CI（与下游项目无关）
```

## 与 array-mic-refreshment 的关系

本包由 [array-mic-refreshment](https://github.com/wangyuanzhong/array-mic-refreshment) 实践中的全局 User Rule、项目 `.cursor/rules` 与 CI skill 归纳而来，并改为 **通用措辞**（不绑定单一产品名）。

## License

MIT
