#!/usr/bin/env python3
"""Make and check the eval summary that every final release needs (specs 013 and 018).

A summary records which eval cases ran, whether each passed, and a fingerprint
of the engine files it ran against. It lives in
.claude/skills/article-forge/evals/summaries/v<version>.json and is committed
with the release.

  make   --version 1.3.1 --from run1.json [--from rerun.json ...]
         Builds the summary from `claude plugin eval --json` output. A later
         --from file replaces earlier results for the same case.
  check  --version 1.3.1 [--tag v1.3.1-rc1]
         The release gate. Fails when the summary is missing, was made for
         different engine content, has a failed case, or leaves out a case
         that exists now or that the last release's summary covered (unless a
         retire record in specs/retired.yaml names that case). A release
         candidate tag (-rcN) needs only the free tests, so it passes here.
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
EXCLUDED_PREFIXES = ("evals/results/", "evals/summaries/")
VERSION_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:-rc(\d+))?$")


def fingerprint(skill_dir: Path) -> str:
    """SHA-256 over every engine file's path and bytes, excluding eval results and summaries."""
    h = hashlib.sha256()
    for p in sorted(skill_dir.rglob("*")):
        if not p.is_file() or EXCLUDED_DIRS & set(p.parts) or p.suffix == ".pyc" or p.name == ".DS_Store":
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


def make(root: Path, version: str, runs: list[Path]) -> dict:
    skill = root / SKILL
    cases: dict[str, dict] = {}
    tool: dict = {}
    for path in runs:
        data = json.loads(path.read_text(encoding="utf-8"))
        tool = {"claude_code": data.get("claudeVersion"), "threshold": data.get("suite", {}).get("threshold")}
        for case in data.get("cases", []):
            runs_with = case.get("arms", {}).get("with", [])
            passes = sum(1 for r in runs_with if r.get("passed"))
            cases[case["name"]] = {"passed": bool(runs_with) and passes == len(runs_with),
                                   "runs": len(runs_with), "passes": passes,
                                   "source": path.name}
    summary = {"version": version, "engine_fingerprint": fingerprint(skill),
               "created": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "tool": tool, "cases": dict(sorted(cases.items()))}
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
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    version = args.version or (args.root / SKILL / "VERSION").read_text(encoding="utf-8").strip()

    if args.command == "fingerprint":
        print(fingerprint(args.root / SKILL))
        return 0
    if args.command == "make":
        if not args.runs:
            ap.error("make needs at least one --from file")
        s = make(args.root, version, args.runs)
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
