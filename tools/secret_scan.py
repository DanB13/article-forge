#!/usr/bin/env python3
"""Scan tracked files for keys and tokens (spec 019).

GitHub push protection covers the public repo; this check also runs in every
writer's copy, where push protection may be off.

  python tools/secret_scan.py            scan every file git tracks
  python tools/secret_scan.py FILE...    scan these files
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = {
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{50,})\b"),
    "Anthropic API key": re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}"),
    "OpenAI-style API key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9]{32,}\b"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Key or token assignment": re.compile(
        r"(?i)\b(?:api[_-]?key|secret|token|password)\b[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_\-/+=]{24,}[\"']"),
}


def tracked_files(root: Path = ROOT) -> list[Path]:
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout
    return [root / p for p in out.decode().split("\0") if p]


def scan(paths: list[Path]) -> list[str]:
    findings = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue  # binary or unreadable: images, ZIPs
        for name, pat in PATTERNS.items():
            for m in pat.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                findings.append(f"{path}:{line}: looks like a {name}")
    return findings


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    findings = scan([Path(a) for a in args] if args else tracked_files())
    for f in findings:
        print(f"FOUND {f}")
    if not findings:
        print("OK: no keys or tokens found")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
