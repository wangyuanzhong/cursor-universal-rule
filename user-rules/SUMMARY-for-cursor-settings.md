# Universal Cursor rules (paste into Settings → Rules → User Rules)

Optional supplement to **project** rules installed from [cursor-universal-rule](https://github.com/wangyuanzhong/cursor-universal-rule). Project rules in `.cursor/rules/` are authoritative; this summary reminds every workspace.

---

## Core

- Finish only when code, **all project `.md`/`.txt`**, exe/CI (if applicable), and push/CI rules are satisfied.
- **Docs define product/UI truth** unless the user overrides in this chat. CI fixes must not contradict README/docs.
- **Local vs cloud** is defined inside each project `.cursor/rules/*.mdc` — follow the Local or Cloud section.

## EXE repos

If the repo has `scripts/build-release.ps1` or similar: **Local** → run `watch-build-release.ps1 -Once` (or fallback) after app/UI changes. **Cloud** → ensure CI builds exe on Windows; verify green after push.

## After push (cloud / when pushing)

Monitor GitHub Actions for the latest push until triggered workflows are green; fix and re-push. Skip on local machine if the project has `.cursor/.local-skip-post-push-ci`.

## Before push / task end

Traverse and update **all** project `**/*.md` and `**/*.txt` so docs match the change.

## Git

Never leave `.cursor/` gitignored; `git add .cursor/` before push.

---

Install project rules: `install-universal-rules.ps1 -ProjectRoot <repo>` from the universal-rule repository.
