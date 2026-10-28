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
  - each scenario has one `@id:NNN-NN` tag whose number matches its spec file,
    and no two scenarios share an ID
  - a scenario recorded in the release ledger (specs/ledger.json) still exists,
    or has a retire record in specs/retired.yaml with a reason and an approver
  - each feature records who approved its scenarios: `# approved: <name> YYYY-MM-DD`
  - a test the last release recorded (scenario wording, grader, eval case, fixture,
    pass rules) is unchanged, or has a record in specs/test-changes.yaml
  - grading metadata, rule tracing and the guard registry (see tools/integrity.py)
  - a provenance mark for every fixture folder (tools/fixture_provenance.py, spec 032)

WARN (exit 0; exit 1 with --strict, used before a release)
  - retire candidate: a spec that a newer spec supersedes still exists
  - an @eval scenario in a shipped feature has no `# last-verified: YYYY-MM-DD`
    line above it, or that date is more than 90 days old

Private specs, tests and evals live under local/ in a user's repo. Upstream
never ships local/, so engine updates cannot conflict with them. Private specs
use IDs like L001-01 and their own ledger, local/specs/ledger.json.

Release commands:
  --release VERSION        fail unless every ledger is at VERSION
  --update-ledger VERSION  record every current scenario ID in the ledger(s);
                           refuses if a recorded ID vanished without a retire record
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
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
SCENARIO_ID = re.compile(r"^@id:(L?\d{3})-(\d{2})$")
RETIRE_FIELDS = ("id", "reason", "approved_by", "date")
APPROVED = re.compile(r"^#\s*approved:\s*\S.*\d{4}-\d{2}-\d{2}", re.M)

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fixture_provenance  # noqa: E402
import integrity  # noqa: E402


@dataclass
class Report:
    fails: list[str] = field(default_factory=list)
    warns: list[str] = field(default_factory=list)
    retire: list[str] = field(default_factory=list)
    features: int = 0
    ids: dict[str, dict] = field(default_factory=dict)  # scenario ID -> {title, spec, folder}
    eval_scenarios: dict[str, set] = field(default_factory=dict)  # eval case -> scenario IDs


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


def ledger_path(spec_dir: Path) -> Path:
    return spec_dir / "ledger.json"


def load_ledger(spec_dir: Path) -> dict | None:
    p = ledger_path(spec_dir)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def load_retired(spec_dir: Path) -> tuple[dict[str, dict], list[str]]:
    """Retire records from retired.yaml next to the ledger. Returns (records by ID, problems)."""
    p = spec_dir / "retired.yaml"
    if not p.exists():
        return {}, []
    import yaml  # only needed when retire records exist

    data = yaml.safe_load(p.read_text(encoding="utf-8")) or []
    records, problems = {}, []
    for i, rec in enumerate(data if isinstance(data, list) else []):
        missing = [f for f in RETIRE_FIELDS if not (isinstance(rec, dict) and rec.get(f))]
        if missing:
            problems.append(f"{p.name} entry {i + 1}: missing {', '.join(missing)}")
            continue
        records[str(rec["id"])] = rec
    return records, problems


def _ledger_check(report: Report, spec_dir: Path) -> None:
    ledger = load_ledger(spec_dir)
    if ledger is None:
        return
    retired, problems = load_retired(spec_dir)
    report.fails += problems
    for sid, entry in sorted(ledger.get("scenarios", {}).items()):
        if entry.get("status") == "retired" or sid in report.ids:
            continue
        if sid in retired:
            report.warns.append(f"{sid} is retired ({retired[sid]['reason']}); the next ledger update records it")
            continue
        report.fails.append(
            f"{sid} disappeared: it was in release {ledger.get('released')} ('{entry.get('title')}'). "
            f"Restore it, or add a retire record to {spec_dir.name}/retired.yaml with a reason and an approver"
        )


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
        if not APPROVED.search(text):
            report.fails.append(f"{name}: no approval record ('# approved: <name> YYYY-MM-DD')")

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
            ids = [t for t in tags if t.startswith("@id:")]
            spec_no = SPEC_NO.match(name).group(1) if SPEC_NO.match(name) else None
            if len(ids) != 1:
                report.fails.append(f"{name}: scenario '{title}' has no @id:NNN-NN tag" if not ids
                                    else f"{name}: scenario '{title}' has more than one @id tag")
            else:
                idm = SCENARIO_ID.match(ids[0])
                sid = ids[0].split(":", 1)[1]
                if not idm or idm.group(1) != spec_no:
                    report.fails.append(f"{name}: scenario '{title}' has @id:{sid}; IDs in this file look like {spec_no}-01")
                elif sid in report.ids:
                    report.fails.append(f"{name}: duplicate @id:{sid} (also on '{report.ids[sid]['title']}')")
                else:
                    end = i + 1
                    while end < len(lines) and not SCENARIO.match(lines[end]) and not lines[end].strip().startswith("@"):
                        end += 1
                    while end > i + 1 and (not lines[end - 1].strip() or VERIFIED.match(lines[end - 1])):
                        end -= 1
                    block = "\n".join(sorted(t for t in tags)) + "\n" + "\n".join(lines[i:end])
                    report.ids[sid] = {"title": title, "spec": name, "folder": feature.parent,
                                       "hash": integrity.hash_text(block)}
            test_tags = [t for t in tags if t == "@code" or t.startswith("@eval:")]
            if len(test_tags) != 1:
                report.fails.append(f"{name}: scenario '{title}' needs exactly one of @code or @eval:<case>")
                continue
            tag = test_tags[0]
            for sid_tag in ids[:1]:
                entry = report.ids.get(sid_tag.split(":", 1)[1])
                if entry is not None and entry["spec"] == name and entry["title"] == title:
                    entry["kind"] = "code" if tag == "@code" else "eval"
                    entry["upstream_only"] = "@upstream" in tags
            if tag == "@code":
                has_code = True
                continue
            case = tag.split(":", 1)[1]
            used_cases.add(case)
            if ids and SCENARIO_ID.match(ids[0]):
                report.eval_scenarios.setdefault(case, set()).add(ids[0].split(":", 1)[1])
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

    for d in dirs["specs"]:
        _ledger_check(report, d)

    report.fails += integrity.check_grading(root, report.eval_scenarios)
    report.fails += integrity.check_rules(root, set(report.ids))
    report.fails += integrity.check_guards(root, {s for s, v in report.ids.items() if v.get("kind") == "code"})
    if (root / fixture_provenance.REGISTRY).exists():
        report.fails += fixture_provenance.check(root)
    ledger = load_ledger(root / "specs") if (root / "specs").is_dir() else None
    if ledger and ledger.get("fingerprints"):
        current = integrity.fingerprints(root, {s: v["hash"] for s, v in report.ids.items()})
        report.fails += integrity.check_changes(root, ledger["fingerprints"], current)

    report.warns += [f"retire candidate: {r}" for r in report.retire]
    return report


def release_check(root: Path, version: str) -> list[str]:
    """Problems that block releasing VERSION: every ledger must already be at VERSION."""
    problems = []
    for d in _dirs(root)["specs"]:
        ledger = load_ledger(d)
        if ledger is None:
            if d == root / "specs":
                problems.append("specs/ledger.json is missing: run --update-ledger before releasing")
            continue
        if ledger.get("released") != version:
            problems.append(f"{d.relative_to(root).as_posix()}/ledger.json is at {ledger.get('released')}, "
                            f"not {version}: run --update-ledger {version}")
    return problems


def update_ledger(root: Path, version: str, today: dt.date | None = None) -> list[str]:
    """Record every current scenario ID in each ledger. Returns problems; writes nothing if any."""
    report = check(root, today)
    blocking = [f for f in report.fails if "disappeared" in f or "duplicate @id" in f or "no @id" in f
                or "since the last release" in f]
    if blocking:
        return blocking
    today = today or dt.date.today()
    for d in _dirs(root)["specs"]:
        old = load_ledger(d) or {"scenarios": {}}
        retired, _ = load_retired(d)
        scenarios = dict(old.get("scenarios", {}))
        for sid, rec in retired.items():
            if sid in scenarios and sid not in report.ids:
                scenarios[sid] = {**scenarios[sid], "status": "retired", "retired_in": version,
                                  "reason": rec["reason"], "approved_by": rec["approved_by"]}
        for sid, info in report.ids.items():
            if info["folder"] != d:
                continue
            prev = scenarios.get(sid, {})
            scenarios[sid] = {"title": info["title"], "spec": info["spec"], "status": "active",
                              "since": prev.get("since", version)}
        data = {"released": version, "updated": today.isoformat(), "scenarios": dict(sorted(scenarios.items()))}
        if d == root / "specs":
            data["fingerprints"] = integrity.fingerprints(
                root, {s: v["hash"] for s, v in report.ids.items() if v["folder"] == d})
        ledger_path(d).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true", help="fail on warnings too (use before a release)")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--today", type=dt.date.fromisoformat, default=None, help=argparse.SUPPRESS)
    ap.add_argument("--release", metavar="VERSION", help="also fail unless every ledger is at VERSION")
    ap.add_argument("--update-ledger", metavar="VERSION", help="record current scenario IDs as released in VERSION")
    args = ap.parse_args(argv)

    if args.update_ledger:
        problems = update_ledger(args.root, args.update_ledger, args.today)
        for p in problems:
            print(f"FAIL {p}")
        if not problems:
            print(f"OK: ledger updated to {args.update_ledger}")
        return 1 if problems else 0

    report = check(args.root, args.today)
    if args.release:
        report.fails += release_check(args.root, args.release)
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
