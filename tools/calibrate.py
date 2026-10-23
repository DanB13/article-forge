#!/usr/bin/env python3
"""Calibrate the AI judges against the maintainer's own labels (spec 023).

  export --from run.json --version 1.3.2 [--n 20]
      Writes evals/calibration/v<version>.yaml: a sample of AI-judged verdicts from
      the run, each with the rubric, what the judge read, and its verdict. Judges
      whose verdicts varied between runs or votes come first; then every judge is
      covered in turn. Fill in each `label:` with pass or fail and set `labelled_by`.
  score --labels evals/calibration/v1.3.2.yaml
      Reports agreement per judge. A judge you disagreed with twice or more is
      flagged, and a flagged judge blocks a final release.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FLAG_AT = 2
EXCERPT = 2500


def _items(run: dict) -> list[dict]:
    items = []
    for case in run.get("cases", []):
        rubrics = {g.get("name"): g for g in case.get("graders", []) if isinstance(g, dict)}
        for i, r in enumerate(case.get("arms", {}).get("with", [])):
            for g in r.get("graders", []):
                if not g.get("judgeVotes"):
                    continue  # only AI-judged graders carry votes
                votes = g.get("judgeVotes") or []
                rubric = rubrics.get(g["name"], {})
                items.append({"case": case["name"], "grader": g["name"], "run": i + 1,
                              "judge": "pass" if g.get("passed") else "fail",
                              "split_votes": len(set(map(bool, votes))) > 1,
                              "rubric": str(rubric.get("graderMarkdown") or (rubric.get("config") or {}).get("criteria") or "").strip(),
                              "judged_text": str(g.get("evidence") or "")[:EXCERPT]})
    return items


def select(items: list[dict], n: int) -> list[dict]:
    """Disagreement first (split votes, or a judge that varied across runs), then round-robin by judge."""
    by_judge = defaultdict(list)
    for it in items:
        by_judge[(it["case"], it["grader"])].append(it)
    varied = {k for k, v in by_judge.items() if len({x["judge"] for x in v}) > 1}
    first = [it for it in items if it["split_votes"] or (it["case"], it["grader"]) in varied]
    chosen = first[:n]
    queues = [list(v) for k, v in sorted(by_judge.items())]
    while len(chosen) < n and any(queues):
        for q in queues:
            while q and q[0] in chosen:
                q.pop(0)
            if q and len(chosen) < n:
                chosen.append(q.pop(0))
    return chosen


def export(run_json: Path, version: str, out: Path, n: int = 20) -> dict:
    run = json.loads(run_json.read_text(encoding="utf-8"))
    chosen = select(_items(run), n)
    doc = {"version": version, "labelled_by": "",
           "instructions": "For each item, read the rubric and the judged text, then set label to pass or fail.",
           "items": [{"id": i + 1, **{k: v for k, v in it.items() if k != "split_votes"}, "label": ""}
                     for i, it in enumerate(chosen)]}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=100), encoding="utf-8")
    return doc


def score(labels: Path) -> dict:
    doc = yaml.safe_load(labels.read_text(encoding="utf-8")) or {}
    agree, disagree = Counter(), Counter()
    unlabelled = []
    for it in doc.get("items", []):
        label = str(it.get("label") or "").strip().lower()
        judge = f"{it['case']}/{it['grader']}"
        if label not in ("pass", "fail"):
            unlabelled.append(it.get("id"))
            continue
        (agree if label == it.get("judge") else disagree)[judge] += 1
    if doc.get("items") and not str(doc.get("labelled_by") or "").strip():
        unlabelled.append("labelled_by")
    judges = sorted(set(agree) | set(disagree))
    return {"agreement": {j: {"agree": agree[j], "disagree": disagree[j]} for j in judges},
            "flagged": {j: disagree[j] for j in judges if disagree[j] >= FLAG_AT},
            "unlabelled": unlabelled}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--from", dest="run", type=Path, required=True)
    e.add_argument("--version", required=True)
    e.add_argument("--n", type=int, default=20)
    s = sub.add_parser("score")
    s.add_argument("--labels", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.cmd == "export":
        out = ROOT / ".claude/skills/article-forge/evals/calibration" / f"v{args.version}.yaml"
        doc = export(args.run, args.version, out, args.n)
        print(f"Wrote {len(doc['items'])} items to {out}")
        return 0
    result = score(args.labels)
    for j, a in result["agreement"].items():
        print(f"{'FLAGGED ' if j in result['flagged'] else 'OK      '} {j}: agree {a['agree']}, disagree {a['disagree']}")
    for u in result["unlabelled"]:
        print(f"UNLABELLED {u}")
    return 1 if result["flagged"] or result["unlabelled"] else 0


if __name__ == "__main__":
    sys.exit(main())
