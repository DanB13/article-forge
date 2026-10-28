#!/usr/bin/env python3
"""Every piece of test text says where it came from (spec 032).

Test text lives in the eval fixtures (.claude/skills/article-forge/evals/_fixtures/ and
each case's resources/) and in tests/fixtures/. specs/fixture-provenance.yaml must list
each of those folders with its origin:

    - path: tests/fixtures/meters
      origin: fictional             # invented for testing
    - path: tests/fixtures/public-sample
      origin: public                # published text: say where from and its licence
      source: https://example.org/post
      licence: CC BY 4.0

A folder that is not listed, or a public one without a source and licence, fails the
spec check. This keeps any real writer's private text out of the public repo.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REGISTRY = Path("specs/fixture-provenance.yaml")
EVALS = Path(".claude/skills/article-forge/evals")


def fixture_dirs(root: Path) -> list[str]:
    dirs = []
    if (root / EVALS / "_fixtures").is_dir():
        dirs.append((EVALS / "_fixtures").as_posix())
    if (root / EVALS).is_dir():
        dirs += [(EVALS / c.name / "resources").as_posix() for c in sorted((root / EVALS).iterdir())
                 if (c / "resources").is_dir()]
    t = root / "tests" / "fixtures"
    if t.is_dir():
        dirs += [f"tests/fixtures/{d.name}" for d in sorted(t.iterdir()) if d.is_dir() and d.name != "__pycache__"]
    return dirs


def check(root: Path) -> list[str]:
    p = root / REGISTRY
    records = (yaml.safe_load(p.read_text(encoding="utf-8")) or []) if p.exists() else []
    by_path = {str(r.get("path", "")).rstrip("/"): r for r in records if isinstance(r, dict)}
    problems = []
    for d in fixture_dirs(root):
        r = by_path.get(d)
        if r is None:
            problems.append(f"fixture {d} has no provenance mark: add it to {REGISTRY.as_posix()} "
                            "as fictional, or public with its source and licence")
        elif r.get("origin") == "public":
            if not (r.get("source") and r.get("licence")):
                problems.append(f"fixture {d} is marked public but gives no source and licence")
        elif r.get("origin") != "fictional":
            problems.append(f"fixture {d} has an unknown origin {r.get('origin')!r}: use fictional or public")
    return problems


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]) if argv else Path.cwd()
    problems = check(root)
    for p in problems:
        print(f"FAIL {p}")
    if not problems:
        print("OK: every fixture says where it came from")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
