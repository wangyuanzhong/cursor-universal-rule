# GitHub Actions CI — playbook (generic)

Policy: [`.cursor/rules/post-push-ci-green.mdc`](../../rules/post-push-ci-green.mdc) (CI watch contract) + [`.cursor/rules/00-universal-core.mdc`](../../rules/00-universal-core.mdc) (who counts as an agent; conflict priority; project documentation definition).

Use this skill for commands and triage after `git push`. Whoever ran `git push` (top-level agent **or** Scenario A sub-agent) is responsible for following this playbook to a documented end state before returning to their caller. Do **not** treat this file as optional when the rule applies.

## Post-push checklist

1. Branch and SHA: `git rev-parse --abbrev-ref HEAD`, `git rev-parse HEAD`.
2. List runs: `gh run list --branch "$(git rev-parse --abbrev-ref HEAD)" --limit 10`.
3. Watch: `gh run watch --exit-status` (or watch each in-progress id).
4. Failed logs: `gh run view <run-id> --log-failed` — read the last 80 lines, then locate the first `FAIL` / `##[error]`.
5. Fix → commit (Conventional Commits per `versioning-and-changelog.mdc`; CI fixes use `fix(ci): <reason>` so they are visually distinct from product fixes in `CHANGELOG.md`) → push → watch again.
6. Report: run IDs, root cause, files changed.

## Discover workflows in *this* repo

```bash
ls .github/workflows/
```

Read each YAML for `on.push` paths, job names, and `runs-on` (especially `windows-latest` for desktop tests / EXE build).

## EXE packaging repos

Expect at least:

- A **CI** workflow with tests (often split per project on Windows).
- A **build-release-exe** (or similar) on `windows-latest` calling `scripts/build-release.ps1`.

If push changed `src/` or `ui/` but the exe workflow did not run, check path filters.

## Common fix patterns

| Symptom | Things to try |
|---------|----------------|
| Test name / assertion drift | Align test with the project's documentation (per `00-universal-core.mdc` "Project documentation" — discover what the project ships, do not assume specific filenames). If behavior intentionally changed, update the doc in the same change set. |
| `robocopy` exit code 1 on success | Reset `$global:LASTEXITCODE = 0` after robocopy in PowerShell build scripts. |
| npm / frontend | `cd ui && npm ci && npm run build`. |
| dotnet | Match CI's `dotnet test` project paths locally on Windows when possible. |
| Workflow syntax | Validate `on`, `paths`, job `needs`. |

## Doc conflict guard

Before merging a "CI-only" fix, run the change-impact grep sweep from `docs-sync-before-finish.mdc` §4 over every user-visible identifier the fix touches. Reconcile every hit in the project's documentation (per `00-universal-core.mdc` — discover what the project ships, do not assume specific filenames).

If the fix would contradict documented behavior, update the doc in the same commit, or fix the code to match the doc — never weaken docs / tests / UI strings to greenwash CI.

## Stop conditions

Same as `post-push-ci-green.mdc`: all triggered runs success; infra blocked (secrets / billing / permissions); same failure after 2 fix-and-push rounds; required Windows job cannot run in this environment.

## Sub-agent note

A Scenario A sub-agent that pushed its own branch follows this playbook on its own branch (`gh run list --branch <its-branch>`) and watches CI to a documented end state before returning. The parent agent verifies the sub-agent's CI status as part of its Done check (see `00-universal-core.mdc` § Parent verification).
