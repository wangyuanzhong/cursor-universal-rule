# Universal Cursor rules (paste into Settings → Rules → User Rules)

Optional supplement to **project** rules installed from [cursor-universal-rule](https://github.com/wangyuanzhong/cursor-universal-rule). Project rules under `.cursor/rules/` are authoritative; this summary keeps every workspace consistent even before the project pack is installed.

---

Treat the items below as a **hard contract**. Do not paraphrase into softer commitments.

## Every task — MUST

1. State `MODE: Local` or `MODE: Cloud` in your plan, once per task.
   - Cloud = Cursor Cloud Agent or any remote/Linux agent without the project's native desktop toolchain.
   - Local = Cursor Desktop on the dev machine with full repo checkout.
2. Before declaring done or opening/updating a PR, output this Done check verbatim with `done`, `N/A: <reason>`, or `blocked: <reason>` per item:

   ```
   [ ] MODE declared
   [ ] Code/build matches user intent; tests pass
   [ ] All project **/*.md and **/*.txt reviewed and updated as needed
   [ ] EXE packaging (Local build OR Cloud Windows CI) — or N/A
   [ ] .cursor/ tracked in git (only if commit/push happened)
   [ ] CI watched and green (only if push happened, not opted out)
   ```

3. If any item is `blocked`, stop and tell the user — do not push past it.

## Conflict priority (when code, docs, tests, CI disagree)

1. Product truth in `README.md`, `docs/**/*.md`, `AGENTS.md`, `CHANGELOG.md`, shipped `.txt` specs.
2. Explicit user messages in this conversation.
3. Implementation code (update code **or** docs deliberately).
4. CI / workflow YAML (must reflect 1 + 3).

Never weaken docs, tests, or documented UI strings just to make CI green.

## EXE / desktop repos

- Trigger: any of `scripts/build-release.ps1`, `scripts/watch-build-release.ps1`, `scripts/build_exe.ps1`, `scripts/pack-ready.ps1`, `scripts/ci_and_build.ps1`, or a `.csproj` shipping a desktop `.exe`.
- **Local** after `src/`/`ui/`/packaging changes: run `.\scripts\watch-build-release.ps1 -Once` (or fallback). Report `.exe` full path + LastWriteTime.
- **Cloud**: ensure `.github/workflows/` has a `windows-latest` workflow that builds the release `.exe`, then verify it goes green after push.

## After push (default on Cloud)

Watch only runs triggered by the latest push on the current branch (`gh run list --branch ... --limit 10`, `gh run watch --exit-status`). Fix red, push, watch again. Stop after 2 identical failures and escalate. **Local opt-out**: presence of `.cursor/.local-skip-post-push-ci` skips the watch only on Local.

## Before push or task end

Walk **all** project `**/*.md` and `**/*.txt` (excluding `node_modules/`, `dist/`, `bin/`, `obj/`, `.git/`, `vendor/`, large `models/`). Update anything that drifted vs. your changes. Report edited files or `Reviewed N docs, no edits needed`.

## Git

- `.cursor/` at the repo root must be tracked. Remove blanket `.cursor/` / `.cursor/*` ignores from `.gitignore`.
- Never commit secrets under `.cursor/`. Never add the user-level `~/.cursor/` to the repo.

---

Install project rules: `install-universal-rules.ps1 -ProjectRoot <repo>` from the cursor-universal-rule repository.
