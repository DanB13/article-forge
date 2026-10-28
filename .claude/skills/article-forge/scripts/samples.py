#!/usr/bin/env python3
"""Read the writer's human samples and phrase fingerprint (spec 027).

Samples live in profile/samples/*.md. A file holds one or more samples; each starts
with its own header between '---' lines:

    ---
    kind: written            # written | spoken | description
    source: "LinkedIn article"
    date: 2020-09
    register: article         # free text, e.g. article, work message, podcast
    published: true           # false keeps it away from any outside service (spec 028)
    human_only: true          # written without AI help
    ---
    <the text, word for word>

Only complete, human-only written and spoken samples are references. A description
(a summary of the writer's style) is kept for reference and never measured.

The fingerprint, profile/samples/fingerprint.md, lists signature phrases and phrases
to leave out in its header:

    ---
    signature_phrases: [have a crack, fair play]
    leave_out: [I mean, you know]
    ---

Without those lists, it falls back to the table under '## 1.' and the quoted phrases
under '## 5.'.

Run: python <skill-dir>/scripts/samples.py [--root .]   lists what is used and why.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

SAMPLES_DIR = Path("profile/samples")
FINGERPRINT = SAMPLES_DIR / "fingerprint.md"
KINDS = ("written", "spoken", "description")
REQUIRED = ("kind", "source", "date", "human_only")
_HEADER = re.compile(r"(?ms)^---\n(.*?)\n---\n")
# Redaction placeholders such as [PERSON] and emoji codes such as :grin: are not the writer's words.
PLACEHOLDER = re.compile(r"\[[A-Z][A-Z_ ]*\]")
EMOJI_CODE = re.compile(r":[a-z0-9_+\-]+:")


@dataclass
class Sample:
    path: Path
    header: dict
    text: str
    problems: list[str] = field(default_factory=list)

    @property
    def kind(self) -> str:
        return str(self.header.get("kind", ""))

    @property
    def published(self) -> bool:
        return self.header.get("published") is True

    @property
    def is_reference(self) -> bool:
        return not self.problems and self.kind in ("written", "spoken")

    def status(self) -> str:
        if self.problems:
            return "not used, because " + "; ".join(self.problems)
        if self.kind == "description":
            return "kept for reference, not used to measure"
        return "used"


def clean(text: str) -> str:
    """The writer's own words: no redaction placeholders, emoji codes or links."""
    text = PLACEHOLDER.sub(" ", text)
    text = EMOJI_CODE.sub(" ", text)
    text = re.sub(r"https?://\S+", " ", text)
    return re.sub(r"[ \t]+", " ", text)


def _check(header: dict) -> list[str]:
    problems = []
    kind = header.get("kind")
    if kind not in KINDS:
        problems.append("the kind is unknown" if kind else "the kind is missing")
    for key in ("source", "date"):
        if not header.get(key):
            problems.append(f"the {key} is missing")
    if header.get("human_only") is not True:
        problems.append("it is not human-only")
    return problems


def parse_file(path: Path) -> list[Sample]:
    text = path.read_text(encoding="utf-8")
    heads = list(_HEADER.finditer(text))
    out = []
    for i, m in enumerate(heads):
        try:
            header = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            header = {}
        if not isinstance(header, dict) or header.get("kind") in ("selection-log", "notes"):
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[m.end():end].strip()
        out.append(Sample(path, header, body, _check(header)))
    return out


def load(root: Path) -> list[Sample]:
    d = root / SAMPLES_DIR
    if not d.is_dir():
        return []
    return [s for p in sorted(d.glob("*.md")) if p.name not in ("README.md", FINGERPRINT.name)
            for s in parse_file(p)]


def references(root: Path, kind: str | None = None) -> list[Sample]:
    return [s for s in load(root) if s.is_reference and (kind is None or s.kind == kind)]


def fingerprint(root: Path) -> dict[str, list[str]]:
    """{'signature': [...], 'leave_out': [...]} from profile/samples/fingerprint.md."""
    p = root / FINGERPRINT
    if not p.exists():
        return {"signature": [], "leave_out": []}
    text = p.read_text(encoding="utf-8")
    head = _HEADER.match(text)
    meta = (yaml.safe_load(head.group(1)) or {}) if head else {}
    if isinstance(meta, dict) and ("signature_phrases" in meta or "leave_out" in meta):
        return {"signature": [str(x) for x in meta.get("signature_phrases") or []],
                "leave_out": [str(x) for x in meta.get("leave_out") or []]}
    sig_sec = re.search(r"(?ms)^## 1\..*?(?=^## |\Z)", text)
    out_sec = re.search(r"(?ms)^## 5\..*?(?=^## |\Z)", text)
    signature = []
    if sig_sec:
        for row in re.findall(r"(?m)^\|\s*([^|]+?)\s*\|", sig_sec.group(0)):
            if row.lower() in ("phrase",) or set(row) <= set("-: "):
                continue
            signature += [p.strip() for p in re.split(r"\s*/\s*", re.sub(r"\(.*?\)", "", row)) if p.strip()]
    leave_out = []
    if out_sec:
        leave_out = [q.strip() for q in re.findall(r'"([^"]+)"', out_sec.group(0))]
    return {"signature": signature, "leave_out": leave_out}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    found = load(args.root)
    if not found:
        print("No samples yet: add your own unaided writing to profile/samples/")
    for s in found:
        print(f"{s.path.name} [{s.kind or '?'}, {s.header.get('source', '?')}]: {s.status()}")
    fp = fingerprint(args.root)
    print(f"Fingerprint: {len(fp['signature'])} signature phrases, {len(fp['leave_out'])} to leave out")
    return 0


if __name__ == "__main__":
    sys.exit(main())
