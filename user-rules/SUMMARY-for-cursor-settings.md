# Universal Cursor rules (paste into Settings → Rules → User Rules)

Optional supplement to **project** rules installed from [cursor-universal-rule](https://github.com/wangyuanzhong/cursor-universal-rule). Project rules under `.cursor/rules/` are authoritative; this summary keeps every workspace consistent even before the project pack is installed.

Treat the items below as a **hard contract**.

## Who counts as an agent — read first

Every invocation is a complete agent run. Top-level agent or sub-agent (Task tool), you execute **all** applicable rules over your own scope of work, as if independent. No "sub-agent shortcut".

Your **round** ends when you return to your caller (sub-agent → parent; top-level → user). At that moment you MUST have:

1. Declared `MODE: ...` in your plan.
2. Run pre-push hygiene over the files you touched (per-file docs enumeration, `.gitignore` review, secret-leak scan, change-impact grep sweep) — even if you are not pushing.
3. Listed user-visible identifiers your work touched and run the change-impact grep sweep over them.
4. Output the verbatim Done check in your final / return message.

The only thing the **scenario** below gates: commit/push, `CHANGELOG.md` write, CI watching.

## Mode detection

Write one of the following into your plan:

```
MODE: Cloud         (system prompt has <cloud_task_instructions> or "running as a CLOUD AGENT"; OR Linux + cwd /workspace or /home/ubuntu/...; OR CI=true; OR .cursor/cloud-agent-marker exists)
MODE: Local         (none of the above + dev-home cwd)
MODE: ambiguous     (mixed signals — STOP and ask the user; never default to Local)
```

## Done check (output verbatim at end of every round)

```
[ ] MODE declared
[ ] Code/build matches user intent; tests pass
[ ] Docs review per-file enumeration (every project .md/.txt; edited / checked: ok / skipped: <reason>; aggregate counts forbidden)
[ ] .gitignore reviewed (no stray secrets, build outputs, transient logs)
[ ] Identifiers-touched listed + change-impact grep sweep clean (OR carryovers OR N/A)
[ ] EXE packaging satisfied — or N/A
[ ] .cursor/ tracked in git (only if commit/push happened)
[ ] CHANGELOG.md entry + version bump (only if files changed AND you push; Scenario B sub-agent: N/A — parent writes)
[ ] Local auto-push satisfied — or N/A
[ ] CI watched and green (only if a push happened by you)
```

Any `blocked` → stop, report.

## "Project documentation" — what this term means

The set of `**/*.md` and `**/*.txt` the project itself ships (excluding `node_modules/`, `dist/`, `bin/`, `obj/`, `.git/`, `vendor/`, large `models/`, vendored `skills/upstream/**`, gitignored paths). **Discover** by walking; do not assume specific filenames. Different projects use different conventions (root introduction file possibly named `README.md`/`INTRODUCTION.md`/non-English/none; `docs/`/`documentation/`/`spec/` subtrees; `AGENTS.md`/`CONTRIBUTING.md`/etc). Only `CHANGELOG.md` is pinned by name. When docs disagree on the same topic, prefer the one closer to the project root and to the user-facing surface.

## Conflict priority (when code, docs, tests, CI disagree)

1. Product truth in **the project's documentation** (incl. `CHANGELOG.md`; discover, don't assume names).
2. Explicit user messages in this conversation.
3. Implementation code (update code **or** docs deliberately).
4. CI / workflow YAML (must reflect 1+3).

Never weaken docs/tests/UI strings to greenwash CI.

## Secret-leak hard stop

Before any commit, scan paths that would be staged. If a likely-secret file (`.env*` other than `.env.example/sample/template`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa*`, `id_ed25519*`, `secrets.*`, `credentials*`, `*.kdbx`, `aws_credentials`, `gcp/azure-credentials*.json`, `service-account*.json`) is **not** gitignored → stop the entire task and report. Do not auto-add to `.gitignore` and continue.

## Change-impact grep sweep (replaces deletion-rename)

Triggered when the change set touches any user-visible identifier (added, renamed, removed, or behavior-changed): file/dir paths, script/command names, CLI flags, env vars, config keys, public function/class/module/API symbols, UI strings, route paths, marker files. Steps:

1. List identifiers-touched at the top of `Docs review:`.
2. For each, grep the repo: `grep -RIn --binary-files=without-match --exclude-dir={.git,node_modules,dist,build,bin,obj,target,vendor} '<id>' .`
3. Reconcile every hit (update / add / remove / preserve with one-line reason). Don't push, return, or declare done while unjustified hits remain.

## Sub-agent commit/push policy

- **Scenario A** (isolated worktree, e.g. `best-of-n-runner`, or different `git rev-parse --git-dir`): MAY commit and push its own branch. If it does, also writes `CHANGELOG.md`, watches CI to a documented end state, reports run IDs. Cannot do all that → MUST NOT push. Either way, runs MODE / hygiene / change-impact grep sweep / Done check.
- **Scenario B** (shared workspace, default `generalPurpose`/`explore`): MUST NOT commit/push/`git add`. Top-level agent commits, pushes, writes the unified `CHANGELOG.md`, watches CI. Sub-agent still runs MODE / hygiene / change-impact grep sweep / Done check before returning.

If unsure, treat as Scenario B. Either scenario, the four "Who counts as an agent" obligations apply.

**Parent verification (mandatory).** When a sub-agent returns, before declaring your own task done verify: (1) verbatim Done check present, no `blocked`; (2) MODE declared; (3) hygiene + change-impact reports present (per-file enumeration + identifiers list); (4) Scenario A only — CI on its branch reached success or documented stop; (5) Scenario A only — CHANGELOG entry present if files changed. Any miss → `blocked: sub-agent did not run full agent loop`. Don't silently re-run for the sub-agent.

## EXE / desktop repos

Trigger: any of `scripts/build-release.ps1` / `watch-build-release.ps1` / `build_exe.ps1` / `pack-ready.ps1` / `ci_and_build.ps1`, or a `.csproj` shipping a desktop `.exe`. **Local** after `src/`/`ui/`/packaging changes: run `.\scripts\watch-build-release.ps1 -Once` (or fallback). Report `.exe` full path + LastWriteTime. **Cloud**: ensure `.github/workflows/` has a `windows-latest` workflow that builds the `.exe`; verify green after push.

## Local auto-push (opt-in per repo)

Active only in `MODE: Local` **and** `.cursor/.local-auto-push` exists. When active, after any reply that modified at least one project file (excluding `.cursor/agent-transcripts/**`, `terminals/**`, gitignored paths):

1. Pre-push hygiene clean (docs, `.gitignore`, secret-leak, change-impact).
2. Version bump + `CHANGELOG.md` entry.
3. `git add -A`, Conventional-Commits commit, `git push origin HEAD` (first push: `git push -u origin HEAD`).
4. Watch CI.

Hard stops (no push, report): detached HEAD, in-progress merge/rebase, secret-leak detected, non-fast-forward not cleanly resolvable, push rejected. Never `--force` / `--force-with-lease`.

## After push (always — Cloud or Local; whoever pushed watches)

Watch only runs triggered by the latest push on the current branch (`gh run list --branch ... --limit 10`, `gh run watch --exit-status`). Fix red, push, watch again. Stop after 2 identical failures and escalate. There is no Local opt-out. Scenario A sub-agents watch CI on their own branch and don't delegate.

## Versioning and changelog (every push)

- `CHANGELOG.md` at repo root, [Keep a Changelog](https://keepachangelog.com) format, [SemVer](https://semver.org).
- Default bump `PATCH`. `MINOR` = new feature. `MAJOR` = breaking (with `Bump reason:`).
- Entry must let a handoff agent understand without reading the diff: summary + `### Added/Changed/Fixed/Removed/Breaking` + `### Files / modules touched` + `### Verify`. Banned: "updated some files", "various improvements", empty subsections, merging multiple pushes.
- Sync if present: `package.json#version`, `Cargo.toml#package.version`, `pyproject.toml`, `*.csproj#Version`, repo-root `VERSION`.
- Commit messages = [Conventional Commits](https://www.conventionalcommits.org). Type→bump: `feat`=MINOR; `fix`/`perf`=PATCH; others=PATCH; `BREAKING CHANGE:` footer=MAJOR.
- Use the project's primary user-facing documentation language (fallback: language of user's most recent message). Don't auto-tag.

## Git

- `.cursor/` at the repo root must be tracked. Remove blanket `.cursor/` / `.cursor/*` ignores. Never commit secrets under `.cursor/`. Never add the user-level `~/.cursor/` to the repo.

---

Install project rules by copying the rule pack's `rules/` and `skills/` directories into your project's `.cursor/`. See the [cursor-universal-rule README](https://github.com/wangyuanzhong/cursor-universal-rule#安装到新项目).
