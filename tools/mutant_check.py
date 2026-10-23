#!/usr/bin/env python3
"""Mutant checks (spec 022): prove each eval case can fail.

For each case, copy the skill, remove the engine text the case names as its
mutant (evals/<case>/grading.yaml), and run the case once against that copy.
The mutant is "killed" when the case fails, which proves the case depends on that
text. A case whose mutant survives tests the model's own behaviour, not the
engine: strengthen it, or record it in specs/guard-cases.yaml with approval.

  python tools/mutant_check.py --out mutants.json [--case NAME ...] [-j 4]

Each run is a real model call (about $0.10 to $0.20 per case).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import eval_summary  # noqa: E402

Runner = Callable[[Path, str, Path], Path]  # (mutant skill dir, case, work dir) -> eval json path


def apply_mutant(skill: Path, dest: Path, removals: list[dict]) -> Path:
    """Copy the skill to dest and remove each mutant text (it must occur exactly once)."""
    shutil.copytree(skill, dest, ignore=shutil.ignore_patterns("results", "summaries", "calibration", "__pycache__"))
    for r in removals:
        target = dest / r["file"]
        text = target.read_text(encoding="utf-8")
        if text.count(r["text"]) != 1:
            raise ValueError(f"mutant text not found exactly once in {r['file']}")
        target.write_text(text.replace(r["text"], "", 1), encoding="utf-8")
    return dest


def claude_runner(mutant_skill: Path, case: str, work: Path) -> Path:
    out = work / f"{case}.json"
    subprocess.run(["claude", "plugin", "eval", str(mutant_skill), "--case", case, "--runs", "1",
                    "--ablation", "none", "--judge-model", "sonnet", "--scaffold", "--trust-plugin",
                    "--allow-tools", "Bash", "Write", "Edit", "--max-cost-usd", "1", "--json", str(out)],
                   capture_output=True, text=True)
    return out


def check_case(skill: Path, case: str, runner: Runner, work: Path) -> dict:
    meta = yaml.safe_load((skill / "evals" / case / "grading.yaml").read_text(encoding="utf-8")) or {}
    removals = meta.get("mutant") or []
    mutant_dir = apply_mutant(skill, work / case / "article-forge", removals)
    result = runner(mutant_dir, case, work / case)
    data = json.loads(result.read_text(encoding="utf-8")) if result.exists() else {}
    runs = next((c["arms"]["with"] for c in data.get("cases", []) if c["name"] == case), [])
    passed = bool(runs) and all(r.get("passed") for r in runs)
    return {"killed": bool(runs) and not passed, "runs": len(runs),
            "removed": sorted({r["file"] for r in removals}),
            "cost_usd": round(float(data.get("costUsd", 0)), 3),
            **({} if runs else {"error": "the mutant run produced no result"})}


def run(root: Path, cases: list[str] | None = None, runner: Runner = claude_runner, jobs: int = 4) -> dict:
    skill = root / eval_summary.SKILL
    names = cases or eval_summary.eval_cases(skill)
    with tempfile.TemporaryDirectory() as tmp:
        with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
            results = dict(zip(names, pool.map(lambda c: check_case(skill, c, runner, Path(tmp)), names)))
    return {"engine_fingerprint": eval_summary.fingerprint(skill), "cases": dict(sorted(results.items()))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--case", action="append")
    ap.add_argument("-j", "--jobs", type=int, default=4)
    ap.add_argument("--root", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    result = run(args.root, args.case, jobs=args.jobs)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, r in result["cases"].items():
        print(f"{'KILLED  ' if r['killed'] else 'SURVIVED'} {name}" + (f" ({r['error']})" if r.get("error") else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
