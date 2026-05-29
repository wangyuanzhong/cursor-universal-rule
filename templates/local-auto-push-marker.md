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
  1. Run pre-push hygiene per `docs-sync-before-finish.mdc`: per-file
     enumeration of every project `.md`/`.txt`, `.gitignore` review,
     secret-leak hard-stop scan, and a change-impact grep sweep for
     every user-visible identifier this task touched (added, renamed,
     removed, or behavior-changed).
  2. Bump SemVer + write a `CHANGELOG.md` entry per
     `.cursor/rules/versioning-and-changelog.mdc`.
  3. `git add -A`, `git commit` (Conventional Commits), and
     `git push origin HEAD` to the **current branch** — never to a different
     branch.
  4. Watch GitHub Actions to green per `post-push-ci-green.mdc` (no opt-out).
     **Whoever ran `git push` watches CI** — the agent that pushed does
     not return until CI is green or hits a documented stop condition.

## What it will NOT do

- Push to `main` automatically. It pushes to whatever branch you are on.
- Force-push. If the push is rejected (non-fast-forward, branch protection),
  the agent stops and reports.
- Push if the secret-leak scan finds a likely-secret file. That is a hard
  stop.
- Push from a sub-agent that shares your workspace (Scenario B). Only the
  top-level agent pushes. A Scenario A sub-agent (isolated worktree) MAY
  push its own branch, but it must own the full pre-push hygiene, the
  CHANGELOG entry, **CI watching to green on its own branch**, and a
  verbatim Done check before returning to the parent. If the sub-agent's
  environment cannot do all of that, it MUST NOT push.

## How to disable

Delete the marker:

```bash
git rm .cursor/.local-auto-push
git commit -m "chore(cursor): disable local auto-push"
```

Or to disable only for yourself locally (without affecting teammates),
rename it to `.cursor/.local-auto-push.off`. The agent will treat the
marker as absent.
