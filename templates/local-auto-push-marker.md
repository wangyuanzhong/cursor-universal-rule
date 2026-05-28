# How to enable Local auto-push in a project

The rule `local-auto-push-current-branch.mdc` is **opt-in per repo**. To turn it on:

```bash
mkdir -p .cursor
touch .cursor/.local-auto-push
git add .cursor/.local-auto-push
git commit -m "chore(cursor): enable local auto-push for current branch"
```

The marker file is committed so all developers on the repo share the same policy.

## What it does (when enabled)

- After any complete agent reply that modified at least one project file
  (excluding `.cursor/agent-transcripts/**`, `terminals/**`, `.gitignore`d paths),
  the agent will:
  1. Run pre-push hygiene (docs sync, `.gitignore` review, secret-leak scan).
  2. Bump SemVer + write a `CHANGELOG.md` entry per
     `.cursor/rules/versioning-and-changelog.mdc`.
  3. `git add -A`, `git commit` (Conventional Commits), and
     `git push origin HEAD` to the **current branch** — never to a different
     branch.
  4. Watch GitHub Actions to green per `post-push-ci-green.mdc` (no opt-out).

## What it will NOT do

- Push to `main` automatically. It pushes to whatever branch you are on.
- Force-push. If the push is rejected (non-fast-forward, branch protection),
  the agent stops and reports.
- Push if the secret-leak scan finds a likely-secret file. That is a hard
  stop.
- Push from a sub-agent that shares your workspace (Scenario B). Only the
  top-level agent pushes; sub-agents in isolated worktrees push their own
  branches.

## How to disable

Delete the marker:

```bash
git rm .cursor/.local-auto-push
git commit -m "chore(cursor): disable local auto-push"
```

Or to disable only for yourself locally (without affecting teammates),
rename it to `.cursor/.local-auto-push.off`. The agent will treat the
marker as absent.
