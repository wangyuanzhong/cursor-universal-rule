# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

Versioning policy is defined in `rules/versioning-and-changelog.mdc`. While
this project is pre-`1.0.0`, breaking changes may occur in `MINOR` bumps and
will be called out in `### Breaking`.

## [Unreleased]

(Pending changes; the next push will close this section into a dated entry.)

## [0.4.1] - 2026-05-28

CI deprecation warning fix.

### Fixed
- `.github/workflows/validate-rules-pack.yml` — set
  `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"` at the workflow level so
  `actions/checkout@v4` (and any other JavaScript action that still
  declares `runs.using: node20`) runs on Node.js 24. GitHub forces the
  Node.js 24 default on June 2, 2026; opting in early avoids the
  workflow starting to warn or fail at the cutover.

### Files / modules touched
- `.github/workflows/validate-rules-pack.yml` — added top-level `env:`
  block with `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: "true"`.

### Verify
- `gh run view <id>` for the next CI run shows no
  `Node.js 20 actions are deprecated` annotations.
- All three jobs still green.

## [0.4.0] - 2026-05-28

Adds a CI workflow that validates the rules pack itself, and documents
how to start versioning when the rules are added to a project that
already has commits.

### Added
- `.github/workflows/validate-rules-pack.yml` — three jobs:
  1. `rules-and-changelog` — runs `.github/scripts/validate.py` to check
     every `rules/*.mdc` has valid frontmatter (non-empty `description:`,
     `alwaysApply` is boolean if present, at least one of `alwaysApply`
     or `globs` is set, non-empty body) and that any cross-reference of
     shape `<name>.mdc` inside a rule body resolves to a real file in
     `rules/`. Also checks `CHANGELOG.md` starts with `# Changelog`, has
     an `## [Unreleased]` section, and has at least one dated
     `## [X.Y.Z] - YYYY-MM-DD` entry with valid SemVer.
  2. `powershell-syntax` — parses `scripts/install-universal-rules.ps1`
     with `[System.Management.Automation.Language.Parser]` to catch
     syntax errors without running the script.
  3. `templates` — confirms each shipped template file exists and is
     non-empty.
- `.github/scripts/validate.py` — pure-stdlib Python validator used by
  the workflow. Importable / runnable locally with `python3
  .github/scripts/validate.py` for fast feedback before push.
- `rules/versioning-and-changelog.mdc` — new "Joining mid-project"
  subsection. When the rule is added to an existing repo, the starting
  version is inferred in priority order: language metadata
  (`package.json`/`Cargo.toml`/`pyproject.toml`/`*.csproj`), then a
  repo-root `VERSION` file, then the latest `v?X.Y.Z` git tag, then a
  SemVer-shaped string in any pre-existing `CHANGELOG.md`, then a
  hidden `0.0.0` baseline that bumps to `0.1.0` on first push.
  Retroactive entries are explicitly forbidden — the changelog starts
  from this push forward; pre-existing changelogs in other formats are
  preserved untouched below the new Keep a Changelog header.

### Changed
- `CHANGELOG.md` `[0.1.0]` entry now uses the actual initial commit date
  (`2026-05-28`) instead of a year-only approximation, so all entries
  conform to the validator's `YYYY-MM-DD` requirement.

### Files / modules touched
- `.github/workflows/validate-rules-pack.yml` — new file.
- `.github/scripts/validate.py` — new file.
- `rules/versioning-and-changelog.mdc` — new "Joining mid-project"
  section under Initialization, with worked example.
- `CHANGELOG.md` — fix `[0.1.0]` date format; this entry.

### Verify
- `python3 .github/scripts/validate.py` exits 0 with `All checks passed.`
- After this push, the GitHub Actions run on the branch reaches
  success across all three jobs (`rules-and-changelog`,
  `powershell-syntax`, `templates`).
- `rules/versioning-and-changelog.mdc` contains a section
  "Joining mid-project" and a "Joining mid-project — example" with a
  worked example showing `package.json` 2.5.3 → 2.5.4.

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

## [0.1.0] - 2026-05-28

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
