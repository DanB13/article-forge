#!/usr/bin/env python3
"""
Create the user's profile/ and articles/ folders from the skill's templates.

Never overwrites: a file that already exists is left exactly as it is and
reported as kept. Safe to run on every onboarding and after every update.

Usage:
  python scaffold_profile.py [repo_root]        # default: current directory
  python scaffold_profile.py --dry-run [repo_root]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parent.parent / "assets" / "templates"


def scaffold(root: Path, dry_run: bool = False, templates: Path = TEMPLATES) -> dict[str, list[str]]:
    created, kept = [], []
    for src in sorted(p for p in templates.rglob("*") if p.is_file()):
        rel = src.relative_to(templates)
        dest = root / rel
        if dest.exists():
            kept.append(str(rel))
            continue
        created.append(str(rel))
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    return {"created": created, "kept": kept}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", nargs="?", default=".", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    out = scaffold(args.root.resolve(), dry_run=args.dry_run)
    verb = "would create" if args.dry_run else "created"
    for f in out["created"]:
        print(f"{verb}: {f}")
    for f in out["kept"]:
        print(f"kept (already exists): {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
