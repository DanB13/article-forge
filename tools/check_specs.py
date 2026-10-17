#!/usr/bin/env python3
"""Check that every spec scenario is covered by a test. Runs in CI.

Rules (see specs/README.md):
  - each specs/*.feature has a `# status:` line and a `Feature:` line
  - each Scenario / Scenario Outline has exactly one tag: @code or @eval:<case>
  - @eval:<case> needs .claude/skills/article-forge/evals/<case>/
  - a feature with @code scenarios must be loaded by a tests/*.py file
Exit 0 when clean, 1 with a list of problems otherwise.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = ROOT / "specs"
TESTS = ROOT / "tests"
EVALS = ROOT / ".claude" / "skills" / "article-forge" / "evals"

SCENARIO = re.compile(r"^\s*Scenario( Outline)?:\s*(.+)$")
TAG_LINE = re.compile(r"^\s*@")
STATUS = re.compile(r"^#\s*status:\s*(proposed|in-progress|shipped)\b", re.M)


def check(root: Path = ROOT) -> list[str]:
    specs, tests, evals = root / "specs", root / "tests", root / ".claude/skills/article-forge/evals"
    problems: list[str] = []
    test_text = "\n".join(p.read_text(encoding="utf-8") for p in tests.glob("*.py")) if tests.exists() else ""

    for feature in sorted(specs.glob("*.feature")):
        name = feature.name
        text = feature.read_text(encoding="utf-8")
        if not STATUS.search(text):
            problems.append(f"{name}: missing '# status: proposed|in-progress|shipped' line")
        if "Feature:" not in text:
            problems.append(f"{name}: missing 'Feature:' line")

        lines = text.splitlines()
        has_code = False
        for i, line in enumerate(lines):
            m = SCENARIO.match(line)
            if not m:
                continue
            tags: list[str] = []
            j = i - 1
            while j >= 0 and TAG_LINE.match(lines[j]):
                tags += lines[j].split()
                j -= 1
            test_tags = [t for t in tags if t == "@code" or t.startswith("@eval:")]
            title = m.group(2).strip()
            if len(test_tags) != 1:
                problems.append(f"{name}: scenario '{title}' needs exactly one of @code or @eval:<case>")
                continue
            tag = test_tags[0]
            if tag == "@code":
                has_code = True
            else:
                case = tag.split(":", 1)[1]
                if not (evals / case).is_dir():
                    problems.append(f"{name}: scenario '{title}' points at missing eval case '{case}'")
        if has_code and f"specs/{name}" not in test_text:
            problems.append(f"{name}: has @code scenarios but no tests/*.py loads it with scenarios()")
    return problems


def main() -> int:
    problems = check()
    for p in problems:
        print(f"FAIL {p}")
    if not problems:
        print(f"OK: {len(list(SPECS.glob('*.feature')))} feature files, every scenario has a test")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
