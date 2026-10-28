#!/usr/bin/env python3
"""Compare the links as published with the link map (spec 038).

    python <skill-dir>/scripts/check_links.py articles/<slug>

The link map is the table or list in articles/<slug>/evidence.md that pairs each
anchor phrase with a URL. The published list is articles/<slug>/links-published.md,
saved on publish day. Both are read as lines holding a quoted anchor phrase and a URL,
in markdown links ([phrase](url)) or table rows (| phrase | url |).

Reports links in the map that were not published, and anchor phrases published with
a different URL. Exits 1 when it finds either.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

URL = re.compile(r"https?://[^\s|)>\]]+")


def link_pairs(text: str) -> dict[str, str]:
    """{anchor phrase (lower case, trimmed): url}."""
    pairs = {}
    for anchor, url in re.findall(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", text):
        pairs[_norm(anchor)] = url
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        urls = [c for c in cells if URL.fullmatch(c.strip("<>`"))]
        texts = [c for c in cells if c and not URL.search(c) and not set(c) <= set("-: ")]
        if urls and texts:
            pairs.setdefault(_norm(texts[0]), urls[0].strip("<>`"))
    return pairs


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().strip('"“”').lower())


def compare(link_map: str, published: str) -> list[str]:
    want, got = link_pairs(link_map), link_pairs(published)
    problems = []
    for anchor, url in sorted(want.items()):
        if anchor not in got:
            problems.append(f'not published: "{anchor}" ({url})')
        elif got[anchor].rstrip("/") != url.rstrip("/"):
            problems.append(f'different URL for "{anchor}": link map {url}, published {got[anchor]}')
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("article", type=Path)
    args = ap.parse_args(argv)
    ev, pub = args.article / "evidence.md", args.article / "links-published.md"
    for f in (ev, pub):
        if not f.exists():
            print(f"Missing {f}")
            return 2
    problems = compare(ev.read_text(encoding="utf-8"), pub.read_text(encoding="utf-8"))
    for p in problems:
        print(f"CHECK {p}")
    if not problems:
        print("OK: every link in the link map went live as mapped")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
