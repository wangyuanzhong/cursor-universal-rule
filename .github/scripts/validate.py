#!/usr/bin/env python3
"""Validate the cursor-universal-rule pack.

Three checks, all must pass:

1. Every `rules/*.mdc` has valid frontmatter:
   - first non-blank line is `---`
   - matching closing `---`
   - non-empty `description:` field
   - at least one of `alwaysApply: true|false` OR `globs:` is present
   - non-empty body after the frontmatter

2. Cross-references between rule files resolve:
   - any token of shape `<name>.mdc` mentioned inside a rule body must
     correspond to an actual file in `rules/`.

3. CHANGELOG.md is well-formed:
   - starts with `# Changelog`
   - has an `## [Unreleased]` section
   - has at least one dated `## [X.Y.Z] - YYYY-MM-DD` entry
   - all `## [X.Y.Z]` headers parse as SemVer.

Designed to run on stock `python3` with no third-party deps.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RULES_DIR = REPO_ROOT / "rules"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
DATED_ENTRY_RE = re.compile(
    r"^##\s+\[(?P<ver>[^\]]+)\]\s+-\s+(?P<date>\d{4}-\d{2}-\d{2})\s*$"
)
UNRELEASED_RE = re.compile(r"^##\s+\[Unreleased\]\s*$", re.IGNORECASE)
MDC_REF_RE = re.compile(r"\b([a-z0-9][a-z0-9._-]+)\.mdc\b")


class Failure(Exception):
    """A check failed; carries a list of human-readable error lines."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("\n".join(errors))


def parse_simple_yaml(text: str) -> dict[str, object]:
    """Parse a flat 'key: value' YAML subset used in rule frontmatter."""
    result: dict[str, object] = {}
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith(("'", '"')) and value.endswith(("'", '"')):
            value = value[1:-1]
        if value.lower() == "true":
            result[key] = True
        elif value.lower() == "false":
            result[key] = False
        else:
            result[key] = value
    return result


def split_frontmatter(text: str) -> tuple[str | None, str | None]:
    lines = text.splitlines()
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines) or lines[i].strip() != "---":
        return None, None
    start = i + 1
    j = start
    while j < len(lines) and lines[j].strip() != "---":
        j += 1
    if j >= len(lines):
        return None, None
    fm = "\n".join(lines[start:j])
    body = "\n".join(lines[j + 1 :])
    return fm, body


def check_rules() -> list[str]:
    errors: list[str] = []
    if not RULES_DIR.is_dir():
        return [f"rules/ directory not found at {RULES_DIR}"]

    rule_files = sorted(RULES_DIR.glob("*.mdc"))
    if not rule_files:
        return ["No *.mdc files found under rules/"]

    rule_filenames = {p.name for p in rule_files}

    for path in rule_files:
        text = path.read_text(encoding="utf-8")
        fm, body = split_frontmatter(text)
        if fm is None or body is None:
            errors.append(f"{path.relative_to(REPO_ROOT)}: missing or unterminated frontmatter (`---` ... `---`)")
            continue
        meta = parse_simple_yaml(fm)
        desc = meta.get("description")
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{path.relative_to(REPO_ROOT)}: frontmatter must define a non-empty `description:`")
        if "alwaysApply" not in meta and "globs" not in meta:
            errors.append(
                f"{path.relative_to(REPO_ROOT)}: frontmatter must include `alwaysApply: true|false` or `globs: ...`"
            )
        if "alwaysApply" in meta and not isinstance(meta["alwaysApply"], bool):
            errors.append(f"{path.relative_to(REPO_ROOT)}: `alwaysApply:` must be `true` or `false` (got {meta['alwaysApply']!r})")
        if not body.strip():
            errors.append(f"{path.relative_to(REPO_ROOT)}: rule body is empty")

        for ref in MDC_REF_RE.finditer(body):
            name = ref.group(0)
            if name in rule_filenames:
                continue
            errors.append(
                f"{path.relative_to(REPO_ROOT)}: references unknown rule file `{name}` (no such file in rules/)"
            )

    return errors


def check_changelog() -> list[str]:
    errors: list[str] = []
    if not CHANGELOG.is_file():
        return [f"{CHANGELOG.relative_to(REPO_ROOT)} not found"]

    text = CHANGELOG.read_text(encoding="utf-8")
    lines = text.splitlines()

    first_heading = next((ln for ln in lines if ln.strip()), "")
    if first_heading.strip() != "# Changelog":
        errors.append("CHANGELOG.md: first non-blank line must be `# Changelog`")

    has_unreleased = any(UNRELEASED_RE.match(ln) for ln in lines)
    if not has_unreleased:
        errors.append("CHANGELOG.md: missing `## [Unreleased]` section")

    dated = []
    for ln in lines:
        m = DATED_ENTRY_RE.match(ln)
        if m:
            ver = m.group("ver")
            if not SEMVER_RE.match(ver):
                errors.append(f"CHANGELOG.md: version `{ver}` in `{ln.strip()}` is not valid SemVer")
            dated.append(ver)

    if not dated:
        errors.append(
            "CHANGELOG.md: must contain at least one dated entry like `## [X.Y.Z] - YYYY-MM-DD`"
        )

    return errors


def main() -> int:
    sections = [
        ("Rule files (rules/*.mdc)", check_rules),
        ("CHANGELOG.md", check_changelog),
    ]
    overall_failed = False
    for title, fn in sections:
        print(f"==> {title}")
        errors = fn()
        if errors:
            overall_failed = True
            for e in errors:
                print(f"  FAIL: {e}")
        else:
            print("  ok")
    if overall_failed:
        print()
        print("Validation FAILED — see errors above.")
        return 1
    print()
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
