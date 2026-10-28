#!/usr/bin/env python3
"""Edit distance: how much the writer changed between the first draft and the published text (spec 031).

    python <skill-dir>/scripts/edit_distance.py articles/<slug>            measure and record
    python <skill-dir>/scripts/edit_distance.py --baseline                  median across articles

The first draft is articles/<slug>/draft-v1.md. The published text is
articles/<slug>/published.md (or pass --published FILE). The result goes into
articles/<slug>/metrics.yaml with the date and the engine version.

Edit distance is the share of words changed: word-level edits (insert, delete,
replace) divided by the longer text's word count. Identical texts score 0%;
texts with no word in common score 100%.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import statistics
import sys
from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))
from meters import strip_markup  # noqa: E402

METRICS = "metrics.yaml"


def tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?", strip_markup(text).lower())


def word_edits(a: list[str], b: list[str]) -> int:
    """Levenshtein distance over words, in O(len(a) * len(b)) time and O(len(b)) memory."""
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, wa in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        for j, wb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (wa != wb))
        prev = cur
    return prev[-1]


def edit_distance(first: str, published: str) -> float:
    a, b = tokens(first), tokens(published)
    longest = max(len(a), len(b))
    return word_edits(a, b) / longest if longest else 0.0


def _version() -> str:
    p = SKILL_DIR / "VERSION"
    return p.read_text(encoding="utf-8").strip() if p.exists() else "?"


def record(article: Path, published: Path | None = None) -> dict:
    first = article / "draft-v1.md"
    pub = published or article / "published.md"
    for f in (first, pub):
        if not f.exists():
            raise SystemExit(f"Missing {f}: edit distance needs the first draft and the published text")
    d = edit_distance(first.read_text(encoding="utf-8"), pub.read_text(encoding="utf-8"))
    path = article / METRICS
    data = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}) if path.exists() else {}
    data["edit_distance"] = {"value": round(d, 4), "percent": f"{d:.0%}", "first_draft": first.name,
                             "published": pub.name, "date": dt.date.today().isoformat(),
                             "engine_version": _version()}
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return data["edit_distance"]


def baseline(root: Path) -> float | None:
    values = []
    for m in sorted((root / "articles").glob(f"*/{METRICS}")):
        data = yaml.safe_load(m.read_text(encoding="utf-8")) or {}
        v = (data.get("edit_distance") or {}).get("value")
        if v is not None:
            values.append(float(v))
    return statistics.median(values) if values else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("article", type=Path, nargs="?")
    ap.add_argument("--published", type=Path)
    ap.add_argument("--baseline", action="store_true")
    ap.add_argument("--root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    if args.article:
        r = record(args.article, args.published)
        print(f"Edit distance: {r['percent']} of words changed (recorded in {args.article.as_posix()}/{METRICS})")
    b = baseline(args.root)
    if args.baseline or args.article:
        print("Baseline: no articles recorded yet" if b is None else f"Baseline: {b:.0%} (median across articles)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
