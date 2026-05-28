# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

Versioning policy is defined in `rules/versioning-and-changelog.mdc`. While
this project is pre-`1.0.0`, breaking changes may occur in `MINOR` bumps and
will be called out in `### Breaking`.

## [Unreleased]

(Pending changes; the next push will close this section into a dated entry.)

## [0.3.0] - 2026-05-28

Second iteration of the rule rewrite. Adds two new universal rules
(`local-auto-push-current-branch.mdc`, `versioning-and-changelog.mdc`),
extends `00-universal-core.mdc` with deterministic Cloud/Local detection
and a sub-agent commit/push policy, folds `.gitignore` maintenance and a
secret-leak scan into `docs-sync-before-finish.mdc`, and removes the Local
opt-out from `post-push-ci-green.mdc`.

### Added
- `rules/local-auto-push-current-branch.mdc` — opt-in via the marker file
  `.cursor/.local-auto-push`. When present and `MODE: Local`, after any
  reply that modified at least one project file the agent runs pre-push
  hygiene, bumps the version, commits with Conventional Commits, and
  pushes the **current branch** (never to `main` automatically). Hard
  stops on detached HEAD, in-progress merge/rebase, secret-leak detected,
  non-fast-forward not cleanly resolvable, or branch-protection rejection.
  Never `--force` / `--force-with-lease`.
- `rules/versioning-and-changelog.mdc` — every push bumps SemVer and
  appends a detailed entry to `CHANGELOG.md` (Keep a Changelog format).
  Each entry must include `### Files / modules touched` and `### Verify`
  so a handoff agent can understand the change without reading the diff.
  Commits use Conventional Commits; type → SemVer mapping is defined.
  Synced version fields: `package.json`, `Cargo.toml`, `pyproject.toml`,
  `*.csproj`, repo-root `VERSION`.
- `templates/CHANGELOG-initial.md` — starter template for projects
  initializing the changelog.
- `templates/local-auto-push-marker.md` — explains how to enable / disable
  the local auto-push marker, what it does, and what it does not do.
- `00-universal-core.mdc` — deterministic Cloud/Local detection algorithm
  using the `<cloud_task_instructions>` system-prompt marker, `/workspace`
  cwd, env `CI`, and `.cursor/cloud-agent-marker`. Adds a third state
  `MODE: ambiguous — blocking` (e.g. WSL) instead of defaulting to Local.
- `00-universal-core.mdc` — sub-agent commit/push policy. Scenario A
  (worktree-isolated, e.g. `best-of-n-runner`) MAY commit and push its
  own branch and maintains its own CHANGELOG entries. Scenario B (shared
  workspace, default) MUST NOT commit or push.
- This `CHANGELOG.md`, retroactively covering `0.1.0` (initial publish)
  and `0.2.0` (first rule rewrite).

### Changed
- `00-universal-core.mdc` Done check now includes `.gitignore` review,
  CHANGELOG/version bump, and Local auto-push items.
- `docs-sync-before-finish.mdc` extended from "documentation sync" to
  full pre-push hygiene: docs review **plus** `.gitignore` review (build
  outputs, dep caches, OS junk, transient logs, secret patterns, local
  Cursor state) **plus** a secret-leak hard-stop scan over staged paths.
- `post-push-ci-green.mdc` adds explicit guidance that CI fixes use
  `fix(ci): <reason>` per Conventional Commits, so they are visually
  distinct from product fixes in `CHANGELOG.md`.
- `user-rules/SUMMARY-for-cursor-settings.md` and `README.md` updated to
  cover all of the above and to document the new opt-in marker file.

### Breaking
- **`post-push-ci-green.mdc` no longer honors `.cursor/.local-skip-post-push-ci`.**
  CI watching is mandatory in both Cloud and Local. Migration: if your
  repo has `.cursor/.local-skip-post-push-ci`, you can delete it; the
  rule no longer reads it. Rationale: with Local auto-push available,
  letting Local push without watching CI causes silent red main / branch.

### Files / modules touched
- `rules/00-universal-core.mdc` — Mode detection algorithm, sub-agent push
  policy, expanded Done check.
- `rules/docs-sync-before-finish.mdc` — added `.gitignore` review + secret
  scan sections, expanded required report.
- `rules/post-push-ci-green.mdc` — removed Local opt-out, added Conventional
  Commits guidance for CI fixes.
- `rules/local-auto-push-current-branch.mdc` — new file.
- `rules/versioning-and-changelog.mdc` — new file.
- `templates/CHANGELOG-initial.md` — new file.
- `templates/local-auto-push-marker.md` — new file.
- `user-rules/SUMMARY-for-cursor-settings.md` — synced to new policy.
- `README.md` — new sections for mode detection, auto-push, versioning,
  sub-agent policy, CI watch removal of opt-out.
- `CHANGELOG.md` — new file (this).

### Verify
- Read `rules/00-universal-core.mdc`: it should declare three modes (Cloud,
  Local, ambiguous) and require `MODE: ...` in the plan and a verbatim
  Done check at end of task.
- Read `rules/local-auto-push-current-branch.mdc`: trigger should require
  both `MODE: Local` and the marker file.
- Read `rules/versioning-and-changelog.mdc`: every push must produce a new
  dated entry in `CHANGELOG.md`.
- `grep -R "local-skip-post-push-ci" rules/` should return only the
  migration mention in `post-push-ci-green.mdc`, not a live opt-out.

## [0.2.0] - 2026-05-28

First iteration of the rule rewrite. Tightens all five rules into a
hard-contract style (`When this rule fires` / `You MUST` / `You MUST NOT`
/ `Required output`), introduces explicit `MODE: Local | Cloud` mode
declaration, and adds a verbatim Done-check checklist required at end of
every task.

### Added
- `MODE: Local | Cloud` declaration requirement in `00-universal-core.mdc`.
- Verbatim Done-check checklist that the agent must output with
  `done` / `N/A: <reason>` / `blocked: <reason>` per item.
- Trigger gate in `exe-packaging-local-cloud.mdc` so non-EXE repos cleanly
  mark the rule as `N/A` instead of partially executing it.

### Changed
- All five rule files rewritten to a uniform, scannable structure with
  imperative MUST/MUST NOT lists.
- Conflict priority moved to `00-universal-core.mdc` only; other rules
  reference it instead of restating it.
- `user-rules/SUMMARY-for-cursor-settings.md` rewritten to mirror the new
  contract.
- `README.md` adds a "规则风格 (v2)" section documenting the new
  structure and the Mode / Done-check requirements.

### Files / modules touched
- `rules/00-universal-core.mdc`
- `rules/docs-sync-before-finish.mdc`
- `rules/exe-packaging-local-cloud.mdc`
- `rules/git-track-cursor-folder.mdc`
- `rules/post-push-ci-green.mdc`
- `user-rules/SUMMARY-for-cursor-settings.md`
- `README.md`

### Verify
- Each rule file under 60 lines and uses the
  `When this rule fires / You MUST / You MUST NOT / Required output`
  structure.
- `00-universal-core.mdc` contains a `Done check` block the agent is
  expected to output verbatim.

## [0.1.0] - 2025

Initial publish: five universal rules (`00-universal-core`,
`docs-sync-before-finish`, `exe-packaging-local-cloud`,
`git-track-cursor-folder`, `post-push-ci-green`), the
`github-actions-ci` skill, the user-rules summary, and the
`install-universal-rules.ps1` installer.

### Added
- `rules/00-universal-core.mdc` — definition of done, conflict priority,
  Local vs Cloud notion (originally without explicit MODE declaration).
- `rules/docs-sync-before-finish.mdc` — review and update all `.md`/`.txt`
  before push or task end.
- `rules/exe-packaging-local-cloud.mdc` — Local release build; Cloud CI
  builds the release `.exe` on `windows-latest`.
- `rules/git-track-cursor-folder.mdc` — `.cursor/` must be tracked in git.
- `rules/post-push-ci-green.mdc` — after push, watch GitHub Actions until
  green; honored `.cursor/.local-skip-post-push-ci` opt-out (later
  removed in `0.3.0`).
- `skills/github-actions-ci/SKILL.md` — playbook for post-push CI triage.
- `user-rules/SUMMARY-for-cursor-settings.md` — paste-into-Settings
  summary mirroring the project rules.
- `templates/github-workflow-build-release-exe.yml` — starter Windows
  workflow for EXE projects.
- `scripts/install-universal-rules.ps1` — installer that copies rules and
  skills into a target repo's `.cursor/` and patches blanket `.cursor/`
  ignores out of `.gitignore`.

### Files / modules touched
- (initial publish)

### Verify
- `git log --oneline` shows the initial `feat: universal Cursor rules
  pack` commit.
