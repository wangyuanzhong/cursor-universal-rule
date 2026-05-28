# Universal Cursor rules (paste into Settings → Rules → User Rules)

Optional supplement to **project** rules installed from [cursor-universal-rule](https://github.com/wangyuanzhong/cursor-universal-rule). Project rules under `.cursor/rules/` are authoritative; this summary keeps every workspace consistent even before the project pack is installed.

---

Treat the items below as a **hard contract**. Do not paraphrase into softer commitments.

## Mode detection — declare once per task

Write one line into your plan before any state-changing tool call:

```
MODE: Cloud         (system prompt mentions "running as a CLOUD AGENT" or has a <cloud_task_instructions> block; OR Linux + cwd /workspace or /home/ubuntu/...; OR CI=true; OR .cursor/cloud-agent-marker exists)
MODE: Local         (none of the above + dev-home cwd)
MODE: ambiguous     (any mixed signals — STOP and ask the user; do NOT default to Local)
```

## Every task — MUST

1. Output the Done check verbatim at end of task with `done` / `N/A: <reason>` / `blocked: <reason>` per item:

   ```
   [ ] MODE declared
   [ ] Code/build matches user intent; tests pass
   [ ] Docs review per-file enumeration (every project .md/.txt; edited / checked: ok / skipped: <reason>; bare aggregate counts forbidden)
   [ ] .gitignore reviewed (no stray secrets, build outputs, transient logs)
   [ ] Deletion-rename grep sweep — clean OR intentional carryovers listed (N/A only if nothing deleted/renamed this task)
   [ ] EXE packaging satisfied — or N/A
   [ ] .cursor/ tracked in git (only if commit/push happened)
   [ ] CHANGELOG.md entry + version bump (only if files changed)
   [ ] Local auto-push satisfied — or N/A
   [ ] CI watched and green (only if push happened) — no Local opt-out
   ```

2. If any item is `blocked`, stop and tell the user — do not push past it.

## Conflict priority (when code, docs, tests, CI disagree)

1. Product truth in `README.md`, `docs/**/*.md`, `AGENTS.md`, `CHANGELOG.md`, shipped `.txt` specs.
2. Explicit user messages in this conversation.
3. Implementation code (update code **or** docs deliberately).
4. CI / workflow YAML (must reflect 1 + 3).

Never weaken docs, tests, or documented UI strings just to make CI green.

## Secret-leak hard stop

Before any commit, scan paths that would be staged. If a likely-secret file (`.env*` other than `.env.example/sample/template`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa*`, `id_ed25519*`, `secrets.*`, `credentials*`, `*.kdbx`, `aws_credentials`, `gcp/azure-credentials*.json`, `service-account*.json`) is **not** gitignored, **stop the task** and report. Do not auto-add to `.gitignore` and continue — the user must decide.

## Sub-agent commit/push policy

- **Scenario A** (sub-agent in an isolated worktree, e.g. `best-of-n-runner`, or different `git rev-parse --git-dir`): MAY commit and push its own branch. **Before returning to its caller it must own all of**: its own `CHANGELOG.md` entry, pre-push hygiene incl. the per-file docs review enumeration and the deletion-rename grep sweep, **CI watching for its push to a documented end state**, and its own verbatim Done check. If the sub-agent's environment cannot do all of that (no `gh`, time/turn budget too short), it MUST NOT push — leave changes in the working tree or return early with `blocked: <reason>`.
- **Scenario B** (sub-agent shares the parent's workspace, e.g. `generalPurpose`, `explore`): MUST NOT commit/push/`git add`. Top-level agent does the single commit + push, runs Done check, watches CI.

If unsure, treat as Scenario B.

**Parent verification (mandatory).** When a sub-agent returns, before declaring your own task done you MUST verify:

1. Sub-agent's reply contains a verbatim Done check; every item is `done` or `N/A: <reason>`. Any `blocked` is propagated up.
2. If the sub-agent reports a push, CI on its branch reached `success` or a documented stop condition. If absent → `blocked: sub-agent did not watch CI`; you watch CI yourself.
3. If the sub-agent's push changed project files, it appended a `CHANGELOG.md` entry. If absent → `blocked: sub-agent did not update CHANGELOG`; you write the entry, push, watch CI again.
4. Sub-agent's docs review is enumerated per-file (not a bare `Reviewed N, no edits needed`). If absent → `blocked: sub-agent docs review not enumerated`; you enumerate yourself.

## EXE / desktop repos

- Trigger: any of `scripts/build-release.ps1`, `scripts/watch-build-release.ps1`, `scripts/build_exe.ps1`, `scripts/pack-ready.ps1`, `scripts/ci_and_build.ps1`, or a `.csproj` shipping a desktop `.exe`.
- **Local** after `src/`/`ui/`/packaging changes: run `.\scripts\watch-build-release.ps1 -Once` (or fallback). Report `.exe` full path + LastWriteTime.
- **Cloud**: ensure `.github/workflows/` has a `windows-latest` workflow that builds the release `.exe`, then verify it goes green after push.

## Local auto-push (opt-in per repo)

Active only in `MODE: Local` **and** `.cursor/.local-auto-push` exists at the repo root.

When active, after any reply that modified at least one project file (excluding `.cursor/agent-transcripts/**`, `terminals/**`, gitignored paths):

1. Run pre-push hygiene (docs sync, `.gitignore` review, secret-leak scan).
2. Bump SemVer + write a `CHANGELOG.md` entry (see below).
3. `git add -A`, commit with Conventional Commits, `git push origin HEAD` (or `git push -u origin HEAD` if no upstream).
4. Watch CI to green.

Hard stops (no push, report and wait): detached HEAD, in-progress merge/rebase, secret-leak detected, non-fast-forward not cleanly resolvable, push rejected by branch protection. Never `--force` or `--force-with-lease`.

## After push (always — Cloud or Local; whoever pushed watches)

Watch only runs triggered by the latest push on the current branch (`gh run list --branch ... --limit 10`, `gh run watch --exit-status`). Fix red, push, watch again. Stop after 2 identical failures and escalate. **There is no Local opt-out.** (Older versions of this pack honored `.cursor/.local-skip-post-push-ci`; that file is now ignored.)

**Whoever ran `git push` watches CI for that push to a documented end state, before returning to their caller.** This includes Scenario A sub-agents on their own branch. Sub-agents must NOT delegate CI watching back to the parent. If a sub-agent cannot watch CI in its environment, it must NOT push.

## Versioning and changelog (every push)

- `CHANGELOG.md` at repo root, [Keep a Changelog](https://keepachangelog.com) format, [SemVer](https://semver.org).
- Default bump = `PATCH`. `MINOR` for new features. `MAJOR` for breaking changes (require a `Bump reason:` line).
- Each entry must be detailed enough for a handoff agent to understand without reading the diff: summary, `### Added/Changed/Fixed/Removed/Breaking`, `### Files / modules touched`, `### Verify`.
- Banned content: "updated some files", "various improvements", empty subsections, multiple pushes merged into one entry.
- Sync any of these if present: `package.json#version`, `Cargo.toml#package.version`, `pyproject.toml`, `*.csproj#Version`, repo-root `VERSION`.
- Commit messages use [Conventional Commits](https://www.conventionalcommits.org). Type→bump: `feat` = MINOR; `fix`/`perf` = PATCH; `docs`/`refactor`/`test`/`chore`/`build`/`ci` = PATCH; any commit with `BREAKING CHANGE:` footer = MAJOR.
- Write entries in the same language as the project's `README.md`. Don't auto-create git tags.

## Pre-push hygiene (`.md`, `.txt`, `.gitignore`, deletion grep sweep)

Walk **all** project `**/*.md` and `**/*.txt` (excluding `node_modules/`, `dist/`, `bin/`, `obj/`, `.git/`, `vendor/`, large `models/`). Update anything that drifted vs. your changes.

Also review `.gitignore`: build outputs, dependency caches, editor/OS junk, transient logs, local-only Cursor state, secret patterns must be ignored.

**Deletion / rename grep sweep**: when this task deletes or renames any user-visible identifier (file, script, command, flag, env var, marker file, public function, URL, config key), grep the entire project for the old name across `*.md *.txt *.mdc *.yml *.yaml *.json *.toml *.ps1 *.sh *.py *.ts *.tsx *.js *.jsx *.cs *.csproj *.sln`. Each remaining hit is either updated/removed, or explicitly preserved with a one-line reason. Do not push while unjustified hits remain.

**Required output — per-file enumeration (no aggregate-count shortcut).** Output a `Docs review:` block where every project `.md`/`.txt` in scope is accounted for individually with one of `edited: <summary>`, `checked: ok`, or `skipped: <reason>`. You MAY group a subdirectory like `docs/api/ (12 files) — checked: ok` only when every file in that group shares the same status. End with `Total: N reviewed, X edited, Y ok, Z skipped` summing to the actual file count. Plus `.gitignore: <unchanged | updated to add: <patterns>>` and `Deletion-rename grep sweep: <N/A | clean | <intentional carryovers>>`. A bare `Reviewed N docs, no edits needed` is **forbidden**.

## Git

- `.cursor/` at the repo root must be tracked. Remove blanket `.cursor/` / `.cursor/*` ignores from `.gitignore`.
- Never commit secrets under `.cursor/`. Never add the user-level `~/.cursor/` to the repo.

---

Install project rules by copying the rule pack's `rules/` and `skills/` directories into your project's `.cursor/`. See the [cursor-universal-rule README](https://github.com/wangyuanzhong/cursor-universal-rule#安装到新项目) for the exact `cp` / `Copy-Item` invocation.
