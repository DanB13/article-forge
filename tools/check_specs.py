#!/usr/bin/env python3
"""Check that every spec scenario is covered by a test, and list specs to retire.

Rules (see specs/README.md):

FAIL (exit 1)
  - each *.feature has a `# status: proposed|in-progress|shipped` line and a `Feature:` line
  - each Scenario / Scenario Outline has exactly one tag: @code or @eval:<case>
  - @eval:<case> needs an eval case folder (engine evals or local/evals)
  - a feature with @code scenarios must be loaded by a test file (tests/ or local/tests/)
  - every eval case folder is used by at least one scenario (no orphans)
  - `# supersedes:` names spec numbers, e.g. `# supersedes: 002, 005`

WARN (exit 0; exit 1 with --strict, used before a release)
  - retire candidate: a spec that a newer spec supersedes still exists
  - an @eval scenario in a shipped feature has no `# last-verified: YYYY-MM-DD`
    line above it, or that date is more than 90 days old

Private specs, tests and evals live under local/ in a user's repo. Upstream
never ships local/, so engine updates cannot conflict with them.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE_EVALS = Path(".claude/skills/article-forge/evals")
STALE_DAYS = 90

SCENARIO = re.compile(r"^\s*Scenario( Outline)?:\s*(.+)$")
STATUS = re.compile(r"^#\s*status:\s*(proposed|in-progress|shipped)\b", re.M)
SHIPPED = re.compile(r"^#\s*status:\s*shipped\b", re.M)
SUPERSEDES = re.compile(r"^#\s*supersedes:\s*(.+)$", re.M)
VERIFIED = re.compile(r"^\s*#\s*last-verified:\s*(\d{4}-\d{2}-\d{2})\s*$")
SPEC_NO = re.compile(r"^(L?\d{3})-")


@dataclass
class Report:
    fails: list[str] = field(default_factory=list)
    warns: list[str] = field(default_factory=list)
    retire: list[str] = field(default_factory=list)
    features: int = 0


def _dirs(root: Path) -> dict[str, list[Path]]:
    return {
        "specs": [d for d in (root / "specs", root / "local" / "specs") if d.is_dir()],
        "tests": [d for d in (root / "tests", root / "local" / "tests") if d.is_dir()],
        "evals": [d for d in (root / ENGINE_EVALS, root / "local" / "evals") if d.is_dir()],
    }


def _eval_cases(eval_dirs: list[Path]) -> dict[str, Path]:
    cases = {}
    for d in eval_dirs:
        for case in sorted(p for p in d.iterdir() if p.is_dir()):
            if (case / "prompt.md").exists() or (case / "case.yaml").exists():
                cases[case.name] = case
    return cases


def check(root: Path = ROOT, today: dt.date | None = None) -> Report:
    today = today or dt.date.today()
    dirs = _dirs(root)
    report = Report()
    test_text = "\n".join(p.read_text(encoding="utf-8") for d in dirs["tests"] for p in d.glob("*.py"))
    cases = _eval_cases(dirs["evals"])
    used_cases: set[str] = set()
    features = sorted(f for d in dirs["specs"] for f in d.glob("*.feature"))
    numbers = {m.group(1): f.name for f in features if (m := SPEC_NO.match(f.name))}
    report.features = len(features)

    for feature in features:
        name = feature.name
        rel = feature.relative_to(root).as_posix()
        text = feature.read_text(encoding="utf-8")
        if not STATUS.search(text):
            report.fails.append(f"{name}: missing '# status: proposed|in-progress|shipped' line")
        if "Feature:" not in text:
            report.fails.append(f"{name}: missing 'Feature:' line")
        shipped = bool(SHIPPED.search(text))

        for m in SUPERSEDES.finditer(text):
            for ref in [r.strip() for r in m.group(1).split(",") if r.strip()]:
                if not re.fullmatch(r"L?\d{3}", ref):
                    report.fails.append(f"{name}: '# supersedes:' expects spec numbers like 002, got '{ref}'")
                elif ref in numbers:
                    report.retire.append(f"{numbers[ref]} (superseded by {name})")

        lines = text.splitlines()
        has_code = False
        for i, line in enumerate(lines):
            m = SCENARIO.match(line)
            if not m:
                continue
            title = m.group(2).strip()
            tags: list[str] = []
            verified: str | None = None
            j = i - 1
            while j >= 0 and (lines[j].strip().startswith("@") or VERIFIED.match(lines[j])):
                if (v := VERIFIED.match(lines[j])):
                    verified = v.group(1)
                else:
                    tags += lines[j].split()
                j -= 1
            test_tags = [t for t in tags if t == "@code" or t.startswith("@eval:")]
            if len(test_tags) != 1:
                report.fails.append(f"{name}: scenario '{title}' needs exactly one of @code or @eval:<case>")
                continue
            tag = test_tags[0]
            if tag == "@code":
                has_code = True
                continue
            case = tag.split(":", 1)[1]
            used_cases.add(case)
            if case not in cases:
                report.fails.append(f"{name}: scenario '{title}' points at missing eval case '{case}'")
            if shipped:
                if verified is None:
                    report.warns.append(f"{name}: @eval scenario '{title}' has never been verified")
                else:
                    age = (today - dt.date.fromisoformat(verified)).days
                    if age > STALE_DAYS:
                        report.warns.append(f"{name}: @eval scenario '{title}' last verified {age} days ago")

        if has_code and rel not in test_text and f"specs/{name}" not in test_text:
            report.fails.append(f"{name}: has @code scenarios but no test file loads it with scenarios()")

    for case in sorted(set(cases) - used_cases):
        report.fails.append(f"eval case '{case}' is not used by any scenario (orphan): retire it or add a scenario")

    report.warns += [f"retire candidate: {r}" for r in report.retire]
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="fail on warnings too (use before a release)")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--today", type=dt.date.fromisoformat, default=None, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    report = check(args.root, args.today)
    for f in report.fails:
        print(f"FAIL {f}")
    for w in report.warns:
        print(f"WARN {w}")
    if not report.fails:
        print(f"OK: {report.features} feature files, every scenario has a test"
              + (f" ({len(report.warns)} warnings)" if report.warns else ""))
    if report.fails or (args.strict and report.warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
