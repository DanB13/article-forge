#!/usr/bin/env python3
"""Make and check the eval summary that every final release needs (specs 013 and 018).

A summary records which eval cases ran, whether each passed, and a fingerprint
of the engine files it ran against. It lives in
.claude/skills/article-forge/evals/summaries/v<version>.json and is committed
with the release.

  make   --version 1.3.1 --from run1.json [--from rerun.json ...]
         Builds the summary from `claude plugin eval --json` output. A later
         --from file replaces earlier results for the same case.
         --mutants mutants.json adds the mutant results (tools/mutant_check.py).
  check  --version 1.3.1 [--tag v1.3.1-rc1]
         The release gate. Fails when the summary is missing, was made for
         different engine content, has a failed case, or leaves out a case
         that exists now or that the last release's summary covered (unless a
         retire record in specs/retired.yaml names that case). With grading
         metadata (spec 024) a case passes when each safety grader passed every
         run and each style grader enough runs (evals/grading-policy.yaml).
         It also fails when a case's mutant survived without an approved guard
         record (spec 022), or when the calibration labels are missing,
         incomplete or flag a judge (spec 023). A release candidate tag (-rcN)
         needs only the free tests, so it passes here.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path(".claude/skills/article-forge")
EXCLUDED_DIRS = {"__pycache__"}
EXCLUDED_PREFIXES = ("evals/results/", "evals/summaries/", "evals/calibration/")
VERSION_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:-rc(\d+))?$")


def fingerprint(skill_dir: Path) -> str:
    """SHA-256 over every file the model runs against: the skill and its eval cases.
    Excludes eval results, summaries and calibration labels, and the grading metadata
    (grading.yaml, grading-policy.yaml), which the eval tool never reads; changes to that
    metadata are guarded by the ledger's test-change control (spec 020) instead."""
    h = hashlib.sha256()
    for p in sorted(skill_dir.rglob("*")):
        if not p.is_file() or EXCLUDED_DIRS & set(p.parts) or p.suffix == ".pyc" or p.name == ".DS_Store":
            continue
        if p.name in ("grading.yaml", "grading-policy.yaml"):
            continue
        rel = p.relative_to(skill_dir).as_posix()
        if rel.startswith(EXCLUDED_PREFIXES):
            continue
        h.update(rel.encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()


def eval_cases(skill_dir: Path) -> list[str]:
    d = skill_dir / "evals"
    if not d.is_dir():
        return []
    return sorted(c.name for c in d.iterdir()
                  if c.is_dir() and ((c / "prompt.md").exists() or (c / "case.yaml").exists()))


def _version_key(v: str) -> tuple[int, int, int]:
    return tuple(int(x) for x in v.split("."))  # type: ignore[return-value]


def summaries_dir(skill_dir: Path) -> Path:
    return skill_dir / "evals" / "summaries"


def _grading(skill_dir: Path, case: str) -> tuple[dict, dict]:
    """(policy, grading metadata) for a case; ({}, {}) when the engine has no grading policy."""
    pol_path = skill_dir / "evals" / "grading-policy.yaml"
    meta_path = skill_dir / "evals" / case / "grading.yaml"
    if not pol_path.exists() or not meta_path.exists():
        return {}, {}
    import yaml

    return (yaml.safe_load(pol_path.read_text(encoding="utf-8")) or {},
            yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {})


def judge_case(runs_with: list[dict], policy: dict, meta: dict) -> dict:
    """Pass rules (spec 024): each grader needs as many passing runs as its tier asks for.
    Without grading metadata, every run must pass."""
    n = len(runs_with)
    passes = sum(1 for r in runs_with if r.get("passed"))
    if not meta:
        return {"passed": bool(runs_with) and passes == n, "runs": n, "passes": passes}
    need_by_tier = policy.get("tiers", {})
    graders = {}
    for name, entry in (meta.get("graders") or {}).items():
        tier = entry.get("tier", meta.get("tier"))
        need = min(int(need_by_tier.get(tier, n)), n)
        ok = sum(1 for r in runs_with if not r.get("error") and
                 any(g.get("name") == name and g.get("passed") for g in r.get("graders", [])))
        graders[name] = {"tier": tier, "passes": ok, "needs": need, "passed": n > 0 and ok >= need}
    return {"passed": bool(graders) and all(g["passed"] for g in graders.values()),
            "runs": n, "passes": passes, "graders": graders}


def make(root: Path, version: str, runs: list[Path], mutants: Path | None = None) -> dict:
    skill = root / SKILL
    cases: dict[str, dict] = {}
    tool: dict = {}
    for path in runs:
        data = json.loads(path.read_text(encoding="utf-8"))
        tool = {"claude_code": data.get("claudeVersion"), "threshold": data.get("suite", {}).get("threshold")}
        for case in data.get("cases", []):
            policy, meta = _grading(skill, case["name"])
            result = judge_case(case.get("arms", {}).get("with", []), policy, meta)
            cases[case["name"]] = {**result, "source": path.name}
    summary = {"version": version, "engine_fingerprint": fingerprint(skill),
               "created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "tool": tool, "cases": dict(sorted(cases.items()))}
    if mutants:
        m = json.loads(mutants.read_text(encoding="utf-8"))
        if m.get("engine_fingerprint") != summary["engine_fingerprint"]:
            raise SystemExit("the mutant results were made for a different engine: rerun tools/mutant_check.py")
        summary["mutants"] = m.get("cases", {})
    out = summaries_dir(skill) / f"v{version}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def _retired_cases(root: Path) -> set[str]:
    p = root / "specs" / "retired.yaml"
    if not p.exists():
        return set()
    import yaml

    data = yaml.safe_load(p.read_text(encoding="utf-8")) or []
    return {str(r["id"]).removeprefix("eval:") for r in data if isinstance(r, dict) and str(r.get("id", "")).startswith("eval:")}


def previous_summary(skill_dir: Path, version: str) -> dict | None:
    older = []
    for p in summaries_dir(skill_dir).glob("v*.json"):
        v = p.stem[1:]
        if re.fullmatch(r"\d+\.\d+\.\d+", v) and _version_key(v) < _version_key(version):
            older.append((_version_key(v), p))
    if not older:
        return None
    return json.loads(max(older)[1].read_text(encoding="utf-8"))


def _guard_cases(root: Path) -> set[str]:
    p = root / "specs" / "guard-cases.yaml"
    if not p.exists():
        return set()
    import yaml

    data = yaml.safe_load(p.read_text(encoding="utf-8")) or []
    return {str(r["case"]) for r in data
            if isinstance(r, dict) and all(r.get(k) for k in ("case", "reason", "approved_by", "date"))}


def _mutant_problems(root: Path, skill: Path, summary: dict) -> list[str]:
    if not (skill / "evals" / "grading-policy.yaml").exists():
        return []
    mutants = summary.get("mutants")
    if mutants is None:
        return ["no mutant results in the summary: run tools/mutant_check.py and pass --mutants to make"]
    guards = _guard_cases(root)
    problems = []
    for name in eval_cases(skill):
        res = mutants.get(name)
        if res is None:
            problems.append(f"{name} has no mutant result")
        elif not res.get("killed") and name not in guards:
            problems.append(f"{name}'s mutant survived: the case still passed with its engine text removed. "
                            "Strengthen the case, or record it as a guard in specs/guard-cases.yaml with your approval")
    return problems


def _calibration_problems(root: Path, skill: Path, version: str) -> list[str]:
    if not (skill / "evals" / "grading-policy.yaml").exists():
        return []
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import calibrate

    path = skill / "evals" / "calibration" / f"v{version}.yaml"
    if not path.exists():
        return [f"no calibration labels for v{version}: run tools/calibrate.py export, label it, then commit it"]
    result = calibrate.score(path)
    problems = [f"calibration item {i} is not labelled" for i in result["unlabelled"]]
    problems += [f"judge {g} is flagged: you disagreed with it {n} times; rewrite it or replace it with an exact check"
                 for g, n in sorted(result["flagged"].items())]
    return problems


def check(root: Path, version: str, tag: str | None = None) -> tuple[list[str], list[str]]:
    """Returns (problems, notes). No problems means the release may go ahead."""
    skill = root / SKILL
    if tag:
        m = VERSION_TAG.match(tag)
        if m and m.group(4):
            return [], [f"{tag} is a release candidate: only the free tests apply; "
                        f"the eval gate applies to the final release v{version}"]
    path = summaries_dir(skill) / f"v{version}.json"
    if not path.exists():
        return [f"no eval summary for v{version}: run the evals, then "
                f"`python tools/eval_summary.py make --version {version} --from <eval json>`"], []
    summary = json.loads(path.read_text(encoding="utf-8"))
    problems: list[str] = []
    if summary.get("engine_fingerprint") != fingerprint(skill):
        problems.append("engine changed since the eval run: rerun the evals on this exact engine and remake the summary")
    cases = summary.get("cases", {})
    for name, res in sorted(cases.items()):
        if not res.get("passed"):
            problems.append(f"{name} failed ({res.get('passes')}/{res.get('runs')} runs passed)")
    retired = _retired_cases(root)
    for name in eval_cases(skill):
        if name not in cases:
            problems.append(f"{name} was not run: every current eval case must be in the summary")
    problems += _mutant_problems(root, skill, summary)
    problems += _calibration_problems(root, skill, version)
    prev = previous_summary(skill, version)
    if prev:
        for name in sorted(prev.get("cases", {})):
            if name not in cases and name not in retired:
                problems.append(f"{name} was not run: it was in the v{prev.get('version')} summary "
                                f"(retire it in specs/retired.yaml as eval:{name} if it is gone on purpose)")
    return sorted(set(problems)), []


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["make", "check", "fingerprint"])
    ap.add_argument("--version")
    ap.add_argument("--tag", help="the git tag being released, e.g. v1.3.1-rc1")
    ap.add_argument("--from", dest="runs", action="append", type=Path, default=[])
    ap.add_argument("--mutants", type=Path, help="mutant results from tools/mutant_check.py")
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    version = args.version or (args.root / SKILL / "VERSION").read_text(encoding="utf-8").strip()

    if args.command == "fingerprint":
        print(fingerprint(args.root / SKILL))
        return 0
    if args.command == "make":
        if not args.runs:
            ap.error("make needs at least one --from file")
        s = make(args.root, version, args.runs, args.mutants)
        failed = [n for n, r in s["cases"].items() if not r["passed"]]
        print(f"Wrote summary for v{version}: {len(s['cases'])} cases, {len(failed)} failed")
        return 0
    problems, notes = check(args.root, version, args.tag)
    for n in notes:
        print(f"NOTE {n}")
    for p in problems:
        print(f"FAIL {p}")
    if not problems:
        print(f"OK: release gate passed for v{version}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
