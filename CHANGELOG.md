# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and this project adheres to [Semantic Versioning](https://semver.org).

Versioning policy is defined in `rules/versioning-and-changelog.mdc`. While
this project is pre-`1.0.0`, breaking changes may occur in `MINOR` bumps and
will be called out in `### Breaking`.

## [Unreleased]

(Pending changes; the next push will close this section into a dated entry.)

## [0.8.1] - 2026-05-29

Fixes a stale `skills/github-actions-ci/SKILL.md` that the maintainer
caught immediately after `0.8.0` was pushed.

The skill was inconsistent with the rule pack at three layers:

1. It hard-coded `README` / `docs` / `manifest` filenames in the
   "Common fix patterns" and "Doc conflict guard" sections — `0.7.2`
   refactored every rule file to be naming-agnostic by referencing
   *the project's documentation* (defined in `00-universal-core.mdc`),
   but the skill never got that update.
2. The post-push checklist did not mention the `fix(ci): <reason>`
   Conventional Commits prefix that `post-push-ci-green.mdc` has
   required since `0.7.0`.
3. The skill did not reflect the `0.7.0` "whoever pushed watches CI"
   contract or the `0.8.0` "Who counts as an agent" framing —
   nothing about Scenario A sub-agents watching CI on their own
   branches, or the change-impact grep sweep that `docs-sync-before-
   finish.mdc` §4 now mandates before merging a CI-only fix.

In short: I marked the file `checked: ok` in `0.7.2` / `0.7.3` /
`0.8.0` Docs review enumerations without actually reconciling it
against the rule changes. The change-impact grep sweep introduced in
`0.8.0` wouldn't have caught it either, because the stale references
in the skill predate the identifiers I touched in those rounds — they
are historical debt from `0.7.2` that survived because nobody
re-checked. The real fix is human/agent discipline: when checking a
file as `checked: ok`, the agent should briefly state *why* it is
still ok given the current change set. (Considering this as a follow-
up rule strengthening.)

### Fixed
- `skills/github-actions-ci/SKILL.md` policy header — now references
  both `post-push-ci-green.mdc` (CI watch contract) **and**
  `00-universal-core.mdc` (who counts as an agent; conflict
  priority; project-documentation definition). New explicit line
  that whoever pushed (top-level agent or Scenario A sub-agent)
  owns the playbook execution before returning to the caller.
- `skills/github-actions-ci/SKILL.md` Post-push checklist step 5 —
  now references Conventional Commits and the `fix(ci): <reason>`
  prefix from `versioning-and-changelog.mdc`.
- `skills/github-actions-ci/SKILL.md` "Common fix patterns" `Test
  name / assertion drift` row — was *"Align test with `README` /
  `docs` / manifest"*; now *"Align test with the project's
  documentation (per `00-universal-core.mdc` — discover what the
  project ships, do not assume specific filenames)"*.
- `skills/github-actions-ci/SKILL.md` "Doc conflict guard" — was
  *"grep or read relevant `docs/` and root `README.md`"*; now
  *"run the change-impact grep sweep from `docs-sync-before-finish.mdc`
  §4 over every user-visible identifier the fix touches. Reconcile
  every hit in the project's documentation"*. Closing sentence adds
  the *never weaken docs / tests / UI strings to greenwash CI*
  reminder.

### Added
- `skills/github-actions-ci/SKILL.md` new **Sub-agent note** at the
  end — Scenario A sub-agent runs this playbook on its own branch
  (`gh run list --branch <its-branch>`); the parent verifies CI
  status as part of its Done check.

### Files / modules touched
- `skills/github-actions-ci/SKILL.md` — reauthored to align with the
  v0.8.0 contracts above.
- `CHANGELOG.md` — this entry.

### Verify
- `grep -RIn 'README\.md\|docs/\*\*' skills/` returns no live "treat
  this as the canonical doc name" mentions; the only README/docs
  references in `skills/` are within the new wording that
  explicitly defers to `00-universal-core.mdc` "Project
  documentation".
- `grep -RIn 'fix(ci):' skills/` returns the post-push checklist
  step 5 line.
- `python3 .github/scripts/validate.py` exits 0.

## [0.8.0] - 2026-05-29

Bump reason: two new contracts that broaden agent behavior — every
agent (incl. sub-agents) runs the full rule loop over its own scope
of work; deletion-rename grep sweep is generalized to cover any
change to a user-visible identifier (added, renamed, removed, or
behavior-changed). Together these address the maintainer's two
real-world failure reports: sub-agents skipping the rules ("not
treating themselves as agents"), and docs lagging changes that
weren't deletions. Done in the same push as a deeper compression
pass that nets the rule pack at 438 lines (−22% from 0.7.3's 563)
even after the new content was added.

### Added
- `rules/00-universal-core.mdc` § **Who counts as an agent** (new top
  section, before mode detection). Establishes that every invocation
  of the rules — top-level agent or sub-agent via Task — is a
  complete agent run that executes all applicable rules over its own
  scope of work, as if independent. The agent's "round" ends when it
  returns to its caller; at that moment it MUST have declared
  `MODE: ...`, run pre-push hygiene over the files it touched (even
  if it is not pushing), listed identifiers-touched and run the
  change-impact grep sweep, and output a verbatim Done check. The
  scenario gate (A/B below) only governs commit/push, CHANGELOG, and
  CI ownership — not the four core obligations.
- `rules/docs-sync-before-finish.mdc` § 4 **Change-impact grep sweep**
  (replaces and broadens the earlier "Deletion / rename grep sweep").
  Triggers whenever the change set touches any user-visible
  identifier — added, renamed, removed, or behavior-changed.
  Mandates an "Identifiers touched this task" preamble at the top of
  the `Docs review:` block listing each touched identifier and how it
  was touched, then a project-wide grep across text files for each
  with reconciliation of every hit.
- `rules/00-universal-core.mdc` Done check gains an
  `Identifiers-touched listed + change-impact grep sweep clean`
  item (replaces the old `Deletion-rename grep sweep` item) and a
  Scenario-B-aware CHANGELOG line (`Scenario B sub-agents: N/A —
  parent writes`).
- `rules/00-universal-core.mdc` § **Parent verification** gains an
  explicit MODE-declared check (item 2) and an explicit "Don't
  silently re-run for the sub-agent" failure-mode escalation policy.

### Changed
- `rules/docs-sync-before-finish.mdc` Required-report `Docs review:`
  format now starts with an **Identifiers touched this task**
  preamble before the per-file enumeration, so the agent must list
  what it changed before it walks files.
- `rules/post-push-ci-green.mdc` parent-verification section is now
  a single one-line cross-reference to `00-universal-core.mdc` (the
  policy lives in one place — already true since `0.7.0`, kept that
  way and tightened further).
- `rules/local-auto-push-current-branch.mdc` precondition list
  references "change-impact grep sweep" instead of "deletion grep
  sweep".
- `templates/local-auto-push-marker.md` pre-push hygiene description
  references "change-impact grep sweep" with the broadened scope.
- `README.md` "子 agent 是否可以 push" section retitled to **每个
  agent 都跑完整规则（含子 agent）** and rewritten to reflect the
  new "Who counts as an agent" framing — Scenario B sub-agents now
  explicitly required to run MODE / hygiene / change-impact grep
  sweep / Done check before returning, and the parent verification
  list updated to match the new five-check policy.
- `README.md` 覆盖能力 table line 3 reflects the broadened pre-push
  hygiene scope (per-file enumeration + change-impact grep sweep).
- `user-rules/SUMMARY-for-cursor-settings.md` rewritten end-to-end
  to mirror the new "Who counts as an agent" framing; conflict
  priority unchanged but block ordering updated; Done check item
  list mirrors `00-universal-core.mdc` exactly; sub-agent policy
  block makes Scenario B obligations explicit.

### Compression (refactor; signal-preserving)
On top of the new contracts, this push also compresses prose, format
mocks, and duplicates across all rules. All MUST / MUST NOT items,
canonical `blocked: <reason>` strings, anti-hallucination signals,
and procedural numbered lists are preserved. Per-file before/after:

```
rules/00-universal-core.mdc                  86 → 86 lines  (added "Who counts as an agent" ~12 lines, compressed ~12 lines elsewhere; net 0)
rules/docs-sync-before-finish.mdc           162 → 123 lines  (−24%)
rules/exe-packaging-local-cloud.mdc          52 → 33 lines  (−37%)
rules/git-track-cursor-folder.mdc            41 → 20 lines  (−51%)
rules/local-auto-push-current-branch.mdc     52 → 46 lines  (−12%)
rules/post-push-ci-green.mdc                 61 → 49 lines  (−20%)
rules/versioning-and-changelog.mdc          109 → 81 lines  (−26%)
                                            ───────────────
total                                       563 → 438 lines  (−22%)
```

### What did NOT change
- Done check structure (10 items, output verbatim); only one row's
  wording was replaced (deletion-rename → identifiers-touched +
  change-impact) and one row was clarified for Scenario B
  (CHANGELOG).
- Mode detection algorithm (three signals, three states).
- Conflict priority (4-step).
- Scenario A four return-time obligations.
- Per-file docs review enumeration spec (status set, grouping,
  Total).
- Secret-leak hard stop pattern list.
- Push procedure semantics.
- Type → SemVer mapping table.
- Version bump rules table.
- Initialization priority list for joining mid-project.

### Files / modules touched
- `rules/00-universal-core.mdc` — added "Who counts as an agent" §,
  compressed mode detection + MUST + MUST NOT, restructured sub-
  agent scenario into a thinner gate that defers to the new top §,
  parent verification gains MODE-declared check.
- `rules/docs-sync-before-finish.mdc` — added Identifiers-touched
  preamble to required output, broadened deletion grep sweep into
  change-impact grep sweep, compressed `.gitignore` review +
  secret-leak scan + intro.
- `rules/exe-packaging-local-cloud.mdc` — compressed trigger gate +
  Local + Cloud sections (file lists inline, fence blocks
  consolidated).
- `rules/git-track-cursor-folder.mdc` — compressed steps to inline
  form, dropped the "Tip" duplicate paragraph.
- `rules/local-auto-push-current-branch.mdc` — compressed
  preconditions and push procedure (one-liners), updated grep-sweep
  reference.
- `rules/post-push-ci-green.mdc` — compressed Who-watches and the
  red-CI procedural item.
- `rules/versioning-and-changelog.mdc` — compressed Authoritative
  artifact + Initialization + Conventional Commits + Language +
  Tagging.
- `templates/local-auto-push-marker.md` — sweep reference updated.
- `README.md` — sub-agent section rewritten; coverage table updated.
- `user-rules/SUMMARY-for-cursor-settings.md` — full rewrite to
  mirror new framing.
- `CHANGELOG.md` — this entry.

### Verify
- `wc -l rules/*.mdc` totals 438 (was 563).
- `python3 .github/scripts/validate.py` exits 0.
- `grep -RIn 'Deletion-rename\|Deletion / rename\|deletion grep sweep' .`
  returns hits only inside `CHANGELOG.md` historical entries (intentional).
- `grep -RIn 'Who counts as an agent\|change-impact grep sweep' rules/`
  returns the new section / sweep across the rule files.
- The Done check block in `rules/00-universal-core.mdc` lists 10
  items including `Identifiers-touched listed + change-impact grep
  sweep clean`.

## [0.7.3] - 2026-05-28

Trim pass. After the maintainer pointed out that the rule pack had
grown to 725 lines / ~5840 words across 7 `alwaysApply: true` files,
this iteration removes prose-heavy material that does not change any
contract. All MUST / MUST NOT items, the Done check (verbatim), the
per-file docs enumeration, the deletion-rename grep sweep, the
secret-leak scan, the sub-agent policy, and the who-watches-CI
contract are unchanged.

Net effect: **725 → 563 lines (−22%)**, **5840 → 4398 words (−25%)**.

### Changed
- `rules/00-universal-core.mdc` — "Project documentation" definition
  reduced from a 17-line block (with four illustrative bullet lists)
  to a single-paragraph definition. Sub-agent commit/push policy
  trimmed from a 22-line nested-bullet section to two scenario
  bullets. Parent-verification subsection compressed (kept all four
  checks intact). 110 → 86 lines.
- `rules/post-push-ci-green.mdc` — "Who watches" section compressed
  from 13 lines to 4. Parent-verification section replaced with a
  one-line cross-reference to `00-universal-core.mdc` (consolidation;
  the policy lived in two places and was duplicated). Migration note
  about `.cursor/.local-skip-post-push-ci` removed (the same note is
  in `README.md`). 77 → 61 lines.
- `rules/docs-sync-before-finish.mdc` — intro paragraph compressed
  from 6 lines to 1. "What to do" / "MUST NOT" prose tightened.
  Secret-leak scan rationale paragraph trimmed. Deletion-rename grep
  sweep intro reduced from 4 lines to 1. Required-report section
  loses the second concrete worked example (kept the placeholder
  template, which carries the "filenames are illustrative" message
  more directly). 195 → 162 lines.
- `rules/versioning-and-changelog.mdc` — header preamble trimmed.
  "Joining mid-project — example" worked example deleted (the
  algorithm in the section above was already complete; the example
  duplicated information). Entry shape replaced: was a 28-line
  fenced markdown mock with one-line `- ...` placeholders for every
  subsection; now a 10-line schema listing required section names
  (`### Added | Changed | Fixed | Removed`, `### Breaking`,
  `### Files / modules touched`, `### Verify`) with inline guidance.
  "What 'detailed enough' means" reduced from 9 bullets to a single
  paragraph; "Banned entry content" reduced from 5 bullets to one
  comma-separated line. 160 → 109 lines.
- `rules/local-auto-push-current-branch.mdc` — intro paragraph and
  trigger-gate prose compressed. Preconditions list rewritten as
  five one-liners (was multi-line bullets). Push procedure
  compressed from 26 lines (one fenced bash block per step) to 6
  lines (numbered list with inline commands). "How to enable in a
  repo" section deleted (the same content lives in
  `templates/local-auto-push-marker.md`). MUST NOT list compressed.
  90 → 52 lines.
- `user-rules/SUMMARY-for-cursor-settings.md` — migration note about
  `.cursor/.local-skip-post-push-ci` removed (kept only in
  `README.md`).

### What did NOT change
- Done check in `00-universal-core.mdc` (10 items, verbatim).
- All MUST / MUST NOT bullets in every rule.
- Mode-detection algorithm (three signals, three states).
- Sub-agent four-item return-time obligations (Scenario A).
- Parent verification four checks (Done check / CI / CHANGELOG /
  docs enumeration).
- Per-file docs review enumeration spec (status set, grouping rules,
  `Total:` requirement).
- Deletion-rename grep sweep MUST.
- Secret-leak hard stop list of patterns.
- Push procedure: `add -A` → Conventional Commits → `push -u origin
  HEAD` (first push) or `push origin HEAD` (subsequent), watch CI.
- Type → SemVer mapping table.
- Version bump rules table.
- Initialization priority list for joining mid-project.

### Files / modules touched
- `rules/00-universal-core.mdc` — compressed sections noted above.
- `rules/post-push-ci-green.mdc` — compressed + parent-verif
  consolidated.
- `rules/docs-sync-before-finish.mdc` — compressed prose, dropped
  one example.
- `rules/versioning-and-changelog.mdc` — compressed entry shape,
  dropped Joining example.
- `rules/local-auto-push-current-branch.mdc` — compressed
  throughout, dropped "How to enable" section.
- `user-rules/SUMMARY-for-cursor-settings.md` — dropped migration
  parenthetical.
- `CHANGELOG.md` — this entry.

### Verify
- `wc -l rules/*.mdc` totals 563 (was 725).
- `python3 .github/scripts/validate.py` exits 0 — no rule has
  invalid frontmatter, no cross-reference broken.
- `grep -RIn 'You MUST\|MUST NOT' rules/` shows the same set of
  hard contracts as before; no MUST removed.
- The Done check block in `rules/00-universal-core.mdc` is
  byte-identical to the previous version (10 items).

## [0.7.2] - 2026-05-28

Removes the implicit assumption baked into multiple rules that every
project ships docs called `README.md`, `AGENTS.md`, and `docs/**`.
Different projects use different naming conventions; the rules pack
must not assume any specific filename. Reported on PR #2 by the
maintainer.

### Added
- `rules/00-universal-core.mdc` — new section **"Project documentation
  — what this term means"**. Defines the canonical phrase
  *the project's documentation* as the set of `**/*.md` and `**/*.txt`
  the project actually ships (under the standard scope of
  `docs-sync-before-finish.mdc`). Discovery rule: walk the repo, do
  not assume specific filenames. Examples that may or may not exist:
  root introduction file (`README.md`, `INTRODUCTION.md`,
  non-English equivalents, or none at all), `docs/`/`documentation/`/
  `spec/` subtrees, `AGENTS.md`/`AGENT.md`/`CONTRIBUTING.md`/
  `.cursor/README.md`, internal `.txt` specs anywhere. The only file
  this rules pack pins by name is `CHANGELOG.md`. When several docs
  disagree, prefer the one closer to the project root and the
  user-facing surface.
- `user-rules/SUMMARY-for-cursor-settings.md` — same definition
  block added so workspaces using only the User Rules summary get
  the same naming-agnostic contract.

### Changed
- `rules/00-universal-core.mdc` conflict priority — was hard-coded to
  `README.md`, `docs/**/*.md`, `AGENTS.md`, `CHANGELOG.md`; now reads
  *"Product truth in **the project's documentation** (defined above),
  including `CHANGELOG.md`. Discover what the project ships; do not
  assume specific filenames."*
- `rules/post-push-ci-green.mdc` red-CI cross-check sentence — was
  the same hard-coded list; now references the canonical definition
  in `00-universal-core.mdc`.
- `rules/versioning-and-changelog.mdc` "Language" section — was
  *"same language as the project's main `README.md`"*; now reads
  *"same language as the project's primary user-facing documentation
  (whatever the project's introduction / overview doc is called)"*
  with a fallback to the user's most recent message language.
- `rules/exe-packaging-local-cloud.mdc` "MUST NOT" bullet — was
  *"without updating `README.md` / `docs/**`"*; now references
  *the project's documentation* generically.
- `rules/docs-sync-before-finish.mdc` "MUST NOT" — was
  *"Update only `README.md` and ignore `docs/**` or shipped `.txt`
  specs"*; now reads *"Update only the most obvious doc and silently
  leave other in-scope docs unread"* (naming-agnostic).
- `rules/docs-sync-before-finish.mdc` `.gitignore`-review table —
  dropped `.cursor/README.md` from the must-keep-tracked list.
  `.cursor/README.md` was generated by the installer that was deleted
  in `0.5.0`, so it is no longer guaranteed to exist; if a project
  has one it should be tracked, but it is not required.
- `rules/docs-sync-before-finish.mdc` `Docs review:` format example —
  added a placeholder-style template (`<root-readme>.md`,
  `docs/<some-spec>.md`, `<vendored-or-skipped-path>/**`) before the
  concrete worked example, with an explicit note that filenames are
  illustrative.
- `user-rules/SUMMARY-for-cursor-settings.md` conflict priority —
  mirrored to reference the new definition.
- `README.md` — versioning section bullet about entry language no
  longer says "用项目 `README.md` 的主语言"; now says *"项目主用户
  文档"* (whatever the project's introduction doc is called) with the
  same fallback to the user's recent message language.

### Why this slipped through
The rules pack was originally written with the maintainer's own
project naming conventions in mind, so `README.md`, `docs/**`,
`AGENTS.md` were treated as universal. They are not. A project that
ships `INTRODUCTION.md`, `内部说明.md`, or no agent-facing doc would
silently be told by the rule that those files are *not* product
truth — exactly the wrong outcome. Centralising the definition once
in `00-universal-core.mdc` and having other rules reference it makes
this fixable in one place.

### Files / modules touched
- `rules/00-universal-core.mdc` — new "Project documentation"
  section, conflict priority refactored.
- `rules/post-push-ci-green.mdc` — cross-check sentence refactored.
- `rules/versioning-and-changelog.mdc` — Language section refactored.
- `rules/exe-packaging-local-cloud.mdc` — MUST NOT bullet refactored.
- `rules/docs-sync-before-finish.mdc` — MUST NOT line refactored,
  `.cursor/README.md` dropped from `.gitignore`-review table, format
  example annotated with placeholders.
- `user-rules/SUMMARY-for-cursor-settings.md` — added definition
  block, conflict priority refactored.
- `README.md` — versioning section bullet refactored.
- `CHANGELOG.md` — this entry.

### Verify
- `grep -RIn 'README\.md\|AGENTS\.md\|docs/\*\*' rules/` returns
  hits only in the new "Project documentation" definition (where
  filenames are listed as examples of what *might* exist), in the
  worked example of the docs review format, and in cross-references
  to other rule sections — never as a hard requirement.
- `python3 .github/scripts/validate.py` exits 0.
- The next push reaches CI green.

## [0.7.1] - 2026-05-28

Stale-reference cleanup that the deletion / rename grep sweep should
have caught earlier. Reported on PR #2 by the maintainer.

### Fixed
- `rules/git-track-cursor-folder.mdc` — removed
  `.cursor/.local-skip-post-push-ci` from the list of "targeted ignores
  you may keep". The opt-out file was deactivated in `0.3.0`, so
  recommending it as a kept ignore was inconsistent. The list now shows
  only `.cursor/agent-transcripts/` as an example, with an explicit
  reminder to keep `.cursor/.local-auto-push` tracked (it is the shared
  project-level marker for the auto-push rule).
- `rules/00-universal-core.mdc` Done check item for docs review —
  previously read `(list edited files OR "reviewed N, no edits needed")`,
  which contradicted the `0.7.0` rewrite of `docs-sync-before-finish.mdc`
  that explicitly forbids the aggregate-count shortcut. Now reads
  `Docs review per docs-sync-before-finish.mdc — per-file enumeration
  (every project .md/.txt with edited / checked: ok / skipped: <reason>;
  bare aggregate counts are forbidden)`.
- `user-rules/SUMMARY-for-cursor-settings.md` Done check item for docs
  review — same wording fix to mirror.

### Why this slipped through
`0.6.0` introduced the deletion / rename grep sweep, but did not
require a one-time backfill on identifiers deleted before `0.6.0`
existed. The `.cursor/.local-skip-post-push-ci` reference in
`git-track-cursor-folder.mdc` survived from `0.1.0`. The `0.7.0`
docs-sync rewrite removed `reviewed N, no edits needed` from the
required-output spec but did not update the Done-check parenthetical
in `00-universal-core.mdc` that referenced the same idiom. Both are
exactly the kind of cross-rule consistency bug the grep sweep can
mechanically catch — it just needs to be run.

### Files / modules touched
- `rules/git-track-cursor-folder.mdc` — L18-22 reworded.
- `rules/00-universal-core.mdc` — L85 docs-review Done-check item rewritten.
- `user-rules/SUMMARY-for-cursor-settings.md` — L26 docs-review Done-check item rewritten.
- `CHANGELOG.md` — this entry.

### Verify
- `grep -RIn 'local-skip-post-push-ci' rules/` returns only:
  - `post-push-ci-green.mdc` migration note (intentional historical);
  - `docs-sync-before-finish.mdc` example of a deleted marker file in
    the new rule documentation (intentional).
  No other rule file references it as a live mechanism.
- `grep -RIn 'reviewed N, no edits needed\|Reviewed N project docs' rules/`
  returns no live hits in the rule files (only `CHANGELOG.md`
  historical entries, which are intentional).
- `python3 .github/scripts/validate.py` exits 0.

### Note on AGENTS.md
Some downstream projects keep an `AGENTS.md` at their repo root as a
"product truth" doc (referenced in the conflict-priority list in
`00-universal-core.mdc`). This rules pack itself does **not** ship an
`AGENTS.md`. If a downstream project's `AGENTS.md` still mentions
`.cursor/.local-skip-post-push-ci`, that text is a downstream
artifact, not something this pack can patch — search and replace
locally per the pack's deletion / rename grep sweep guidance.

## [0.7.0] - 2026-05-28

Closes two real-world rule bypass paths reported from a downstream
project:

- A sub-agent ran, pushed, and returned without watching CI. The
  existing `post-push-ci-green.mdc` said "after push, watch CI" but
  did not say **which** agent owns the watch, leaving room for
  sub-agents to assume the parent would do it.
- Not all docs were updated. The existing `docs-sync-before-finish.mdc`
  required output let the agent satisfy its obligation with
  `Reviewed 12 docs, no edits needed` — a single aggregate count that
  did not force the agent to actually visit every file.

This release rewrites both rules so the contracts are mechanical and
unbypassable, and adds an explicit parent-side verification step so
even a misbehaving sub-agent gets caught before the parent declares
its own task done.

### Added
- `rules/post-push-ci-green.mdc` "Who watches" section: **whoever
  ran `git push` watches CI for that push to a documented end state
  before returning to their caller**. Applies to Scenario A
  sub-agents on their own branches. Sub-agents that cannot watch CI
  in their environment (no `gh`, hard time/turn budget) MUST NOT
  push — they leave changes for the parent or return early with
  `blocked: cannot watch CI`. Pushing without watching is treated
  as a hard rule violation.
- `rules/post-push-ci-green.mdc` "Parent verification" section:
  when a sub-agent returns and reports a push, the parent must
  verify (1) sub-agent's Done check is present and not blocked,
  (2) CI on the sub-agent's branch reached `success` or a
  documented stop condition, (3) the sub-agent appended a
  `CHANGELOG.md` entry. Any missing item is `blocked: sub-agent
  did not <X>` and the parent picks it up.
- `rules/00-universal-core.mdc` "Sub-agent commit/push policy" now
  spells out, for Scenario A: the sub-agent owns its own
  `CHANGELOG.md` entry, pre-push hygiene incl. docs enumeration and
  deletion-rename grep sweep, **CI watching for its own push**, and
  its own verbatim Done check, all before returning.
- `rules/00-universal-core.mdc` new "Parent verification when a
  sub-agent returns" subsection: parent's Done check covers the
  union of (parent's own work) and (verification of every
  sub-agent's work). A bare `Reviewed N docs, no edits needed` from
  a sub-agent is explicitly listed as not acceptable.

### Changed
- `rules/docs-sync-before-finish.mdc` required output is now a
  per-file enumeration. The aggregate-count shortcut
  (`Reviewed N project docs, no edits needed`) is **removed**.
  Every project `.md`/`.txt` in scope must be listed with exactly
  one of `edited: <summary>`, `checked: ok`, or
  `skipped: <reason>`. Subdirectory grouping (`docs/api/ (12 files)
  — checked: ok`) is allowed only when every file in the group
  shares the same status. A `Total: N reviewed, X edited, Y ok, Z
  skipped` summary line is required and must add up to the actual
  scoped file count.
- `rules/docs-sync-before-finish.mdc` "What to do" and "MUST NOT"
  sections updated to call out the enumeration requirement and
  ban the count-shortcut explicitly.
- `user-rules/SUMMARY-for-cursor-settings.md` mirrors all three
  rule-level changes: who-watches CI, parent verification, and
  per-file docs enumeration.

### Files / modules touched
- `rules/post-push-ci-green.mdc` — added "Who watches" and "Parent
  verification" sections.
- `rules/00-universal-core.mdc` — expanded sub-agent policy with
  return-time obligations; added "Parent verification when a
  sub-agent returns" subsection.
- `rules/docs-sync-before-finish.mdc` — replaced aggregate-count
  required output with per-file enumeration; updated "What to do"
  and "MUST NOT" to bar the shortcut.
- `user-rules/SUMMARY-for-cursor-settings.md` — three sections
  rewritten to mirror the rule changes.
- `CHANGELOG.md` — this entry.

### Verify
- `rules/post-push-ci-green.mdc` contains a section titled
  "Who watches — MUST" stating the pushing agent owns CI watching.
- `rules/00-universal-core.mdc` contains "Parent verification when
  a sub-agent returns — MUST" and lists the four checks (Done
  check, CI status, CHANGELOG, docs enumeration).
- `rules/docs-sync-before-finish.mdc` "Required report" no longer
  contains the string `Reviewed N project docs, no edits needed`
  as a permitted output.
- `python3 .github/scripts/validate.py` exits 0.
- The next push reaches CI green.

## [0.6.0] - 2026-05-28

Mechanical defense against the failure mode that just hit this repo:
after `0.5.0` deleted `scripts/install-universal-rules.ps1`, two stale
references to "安装脚本" / "安装到项目" survived in `README.md`'s
upper sections because the per-file documentation walk in
`docs-sync-before-finish.mdc` did not require a project-wide grep on
deleted identifiers. This release fixes the immediate doc miss and
adds a hard MUST grep-sweep step so future deletions are caught.

This push contains two commits, one `fix` and one `feat`. Per the
type-to-SemVer mapping, the highest-impact commit determines the bump,
so this is `MINOR`.

### Added
- `rules/docs-sync-before-finish.mdc` §4 **Deletion / rename grep
  sweep** — a hard MUST step that fires whenever the change set
  deletes, renames, or removes any user-visible identifier (file,
  script, command, flag, env var, marker file, public symbol, URL,
  config key). The agent must run a project-wide grep across
  `*.md *.txt *.mdc *.yml *.yaml *.json *.toml *.ps1 *.sh *.py *.ts
  *.tsx *.js *.jsx *.cs *.csproj *.sln` for the old name and
  reconcile every hit (update, remove, or explicitly preserve with a
  one-line reason). Push and "task done" are blocked while
  unjustified hits remain.
- `Deletion-rename grep sweep` row added to the Done check in
  `00-universal-core.mdc` and the user-rules summary, with explicit
  options `clean | <intentional carryovers> | N/A: nothing
  deleted/renamed`.

### Fixed
- `README.md` L3 — project description now says "把 `rules/` 和
  `skills/` 复制到目标项目的 `.cursor/`" instead of "安装到项目的
  `.cursor/`", aligning the header with the no-installer reality
  introduced in `0.5.0`.
- `README.md` L95 — the "重要说明（必读）" paragraph no longer lists
  "安装脚本" as a companion to skills; it now reads "配合 **skills**
  （如 `github-actions-ci`）".

### Changed
- `rules/docs-sync-before-finish.mdc` frontmatter `description` and
  intro paragraph updated to mention the new fourth concern.
- `user-rules/SUMMARY-for-cursor-settings.md` "Pre-push hygiene"
  section retitled to include the grep sweep, with command summary
  and required-report addition.

### Files / modules touched
- `README.md` — two header-section rewordings.
- `rules/docs-sync-before-finish.mdc` — new §4 (~30 lines), updated
  frontmatter and intro, expanded required report.
- `rules/00-universal-core.mdc` — Done check gains the
  `Deletion-rename grep sweep` row.
- `user-rules/SUMMARY-for-cursor-settings.md` — Done check + Pre-push
  hygiene section updated to mirror.
- `CHANGELOG.md` — this entry.

### Verify
- `grep -RIn 'install-universal-rules\|安装脚本' . --include='*.md'`
  returns hits only in `CHANGELOG.md` (historical entries) and one
  intentional example reference inside
  `rules/docs-sync-before-finish.mdc`. Both are documented as
  intentional carryovers per the new rule.
- `python3 .github/scripts/validate.py` exits 0.
- The next push reaches CI green on `rules-and-changelog` and
  `templates`.

## [0.5.0] - 2026-05-28

Drops the PowerShell installer in favor of plain `cp` / `Copy-Item`
instructions, on the grounds that the script does little beyond copying
two directories and was Windows-only.

### Removed
- `scripts/install-universal-rules.ps1` — deleted. The script copied
  `rules/*.mdc` and `skills/`, wrote a small `.cursor/README.md`,
  patched blanket `.cursor/` ignores out of `.gitignore`, and could put
  the user-rules summary on the clipboard. None of these are operations
  worth a Windows-only dependency: rule installation is now a plain
  `cp -r` (or `Copy-Item -Recurse`), the `.gitignore` cleanup is
  enforced by `git-track-cursor-folder.mdc`, and the user-rules summary
  can be copied directly from `user-rules/SUMMARY-for-cursor-settings.md`.
- `scripts/` directory — empty after the file removal, so removed too.
- `.github/workflows/validate-rules-pack.yml` `powershell-syntax` job —
  no longer relevant; the workflow now runs only `rules-and-changelog`
  and `templates`.

### Changed
- `README.md` — "安装到新项目" section rewritten with concrete
  `git clone` + `cp` (and PowerShell `Copy-Item`) commands, plus an
  explicit note that `.gitignore` blanket `.cursor/` ignores must be
  removed manually (also enforced by `git-track-cursor-folder.mdc`).
  Directory-structure diagram updated.
- `user-rules/SUMMARY-for-cursor-settings.md` — final line points at
  the README's install section instead of the deleted script.
- `rules/git-track-cursor-folder.mdc` — "Tip" section no longer
  references the installer; states explicitly that there is no
  installer.

### Breaking
- Anyone who relied on `scripts/install-universal-rules.ps1` will need
  to copy `rules/` and `skills/` manually instead. Migration is the
  three lines of `cp -r` / `Copy-Item -Recurse` shown in the README.
  The `-InstallUserRulesClipboard` convenience is gone — paste the
  contents of `user-rules/SUMMARY-for-cursor-settings.md` directly.

### Files / modules touched
- `scripts/install-universal-rules.ps1` — deleted.
- `scripts/` — directory removed (now empty).
- `.github/workflows/validate-rules-pack.yml` — removed
  `powershell-syntax` job.
- `README.md` — install section rewrite + structure diagram.
- `user-rules/SUMMARY-for-cursor-settings.md` — last line updated.
- `rules/git-track-cursor-folder.mdc` — Tip section reworded.
- `CHANGELOG.md` — this entry.

### Verify
- `ls scripts/ 2>/dev/null` returns nothing.
- `python3 .github/scripts/validate.py` exits 0.
- The CI run for this push has only two jobs: `rules-and-changelog`
  and `templates`. Both green.

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
