#!/usr/bin/env python3
"""Check that a writer's profile has what the engine reads.

Run from the repo root: python <skill-dir>/scripts/check_profile.py
Exits 1 and lists the problems if something the engine needs is missing.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import settings  # noqa: E402

REQUIRED_FILES = ("profile/voice-profile.md", "profile/context.md")
VOICE_SECTIONS = ("Registers", "Learned from published diffs")


def problems(root: Path) -> list[str]:
    found = []
    for rel in REQUIRED_FILES:
        p = root / rel
        if not p.exists() or not p.read_text(encoding="utf-8").strip():
            found.append(f"{rel} is missing or empty")
    voice = root / REQUIRED_FILES[0]
    if voice.exists():
        text = voice.read_text(encoding="utf-8")
        headings = [h.strip() for h in re.findall(r"(?m)^## (.+)$", text)]
        for section in VOICE_SECTIONS:
            if not any(h.startswith(section) for h in headings):
                found.append(f"{REQUIRED_FILES[0]} has no '## {section}' section")
        registers = re.search(r"(?ms)^## Registers.*?(?=^## |\Z)", text)
        if registers and not re.search(r"(?m)^### \S", registers.group(0)):
            found.append(f"{REQUIRED_FILES[0]} names no register under '## Registers' (for example '### default')")
    found += settings.key_problems(root)
    return found


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    found = problems(args.root)
    for p in found:
        print(f"PROBLEM {p}")
    if not found:
        print("OK: the profile has everything the engine reads")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
