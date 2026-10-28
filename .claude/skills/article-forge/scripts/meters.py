#!/usr/bin/env python3
"""Rule-based meters and the scorecard (specs 029, 030, 028).

Run from the repo root on a draft:

    python <skill-dir>/scripts/meters.py articles/<slug>/draft.md

It prints the scorecard and, for a file under articles/<slug>/, writes
articles/<slug>/scorecard.md. Every meter gives a traffic light (green, amber,
red, or grey when it cannot run) and a reason. A poor score is a warning, never a
stop: the script always exits 0 once it has read the draft.

Meters:
  overused words  common AI tells; the writer's allowed words are never flagged
  antithesis      "not X but Y" and "X, not Y"; 2 to 3 is rhetoric, more is a rhythm
  rhythm          how much sentence length varies
  is it me?       distance from the writer's written samples (pronouns, contractions, word and
                  sentence length, punctuation habits)
  informality     signature phrases against the informality dial; phrases to leave out
  AI detector     Pangram, only when switched on, with a key, and only on published text
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import os
import re
import statistics
import sys
import time
import urllib.request
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import samples as samples_mod  # noqa: E402
import settings as settings_mod  # noqa: E402

SKILL_DIR = Path(__file__).resolve().parents[1]

# (label, pattern). Patterns match common inflections. Allowed words are matched on the label.
OVERUSED = [
    ("delve", r"\bdelv(?:e|es|ed|ing)\b"),
    ("tapestry", r"\btapestr(?:y|ies)\b"),
    ("landscape", r"\blandscapes?\b"),
    ("navigate", r"\bnavigat(?:e|es|ed|ing)\b"),
    ("robust", r"\brobust(?:ly|ness)?\b"),
    ("seamless", r"\bseamless(?:ly)?\b"),
    ("leverage", r"\bleverag(?:e|es|ed|ing)\s+(?:the|our|your|their|this|these|that|its|it|ai|data)\b"),
    ("inflection point", r"\binflection points?\b"),
    ("realm", r"\brealms?\b"),
    ("testament", r"\btestament\b"),
    ("pivotal", r"\bpivotal\b"),
    ("foster", r"\bfoster(?:s|ed|ing)?\b"),
    ("underscore", r"\bunderscor(?:e|es|ed|ing)\b"),
    ("elevate", r"\belevat(?:e|es|ed|ing)\b"),
    ("intricate", r"\bintricat(?:e|ies)\b"),
    ("multifaceted", r"\bmultifaceted\b"),
    ("holistic", r"\bholistic(?:ally)?\b"),
    ("synergy", r"\bsynerg(?:y|ies|istic)\b"),
    ("paradigm", r"\bparadigms?\b"),
    ("embark", r"\bembark(?:s|ed|ing)?\b"),
    ("unleash", r"\bunleash(?:es|ed|ing)?\b"),
    ("game-changing", r"\bgame[- ]chang(?:ing|er|ers)\b"),
    ("in today's fast-paced", r"\bin today['’]s (?:fast-paced|digital|ever-changing)\b"),
    ("ever-evolving", r"\bever[- ]evolving\b"),
    ("furthermore", r"\bfurthermore\b"),
    ("moreover", r"\bmoreover\b"),
    ("utilise", r"\butili[sz](?:e|es|ed|ing|ation)\b"),
    ("worth noting", r"\bworth noting\b"),
    ("crucial", r"\bcrucial(?:ly)?\b"),
    ("vibrant", r"\bvibrant\b"),
    ("thrilled", r"\bthrilled\b"),
    ("touch base", r"\btouch(?:ing)? base\b"),
    ("circle back", r"\bcircl(?:e|ing) back\b"),
]

ANTITHESIS = [
    re.compile(r"\bnot\s+(?:just|only|merely|simply)?\s*[^.,;:!?\n]{1,60}?[,;]?\s+but\s+", re.I),
    re.compile(r"[A-Za-z][^.;:!?\n]{2,80},\s+not\s+[^.;:!?\n]{1,60}[.;!?]", re.I),
    re.compile(r"\bisn['’]t about [^.;!?\n]{1,60}[.;]\s+it['’]s about\b", re.I),
]

# "Is it me?" compares interpretable style rates, each divided by a typical spread so that
# no single feature dominates. Rates are per word unless named otherwise.
STYLE_FEATURES = {
    "first person (I, me, my, we, our)": 0.03,
    "second person (you, your)": 0.015,
    "contractions": 0.02,
    "long words (9+ letters)": 0.04,
    "mean word length": 0.4,
    "mean sentence length": 6.0,
    "sentence length spread": 0.2,
    "commas": 0.02,
    "brackets": 0.006,
    "questions": 0.006,
    "exclamations": 0.006,
    "spaced hyphens and ampersands": 0.006,
    '"the" and "of"': 0.02,
}
_FIRST = {"i", "me", "my", "mine", "we", "us", "our", "ours", "i'm", "i've", "i'll", "i'd", "we're", "we've"}
_SECOND = {"you", "your", "yours", "you're", "you've", "you'll", "you'd"}
LIGHTS = ("green", "amber", "red", "grey")


def strip_markup(md: str) -> str:
    md = re.sub(r"(?s)<!--.*?-->", " ", md)
    md = re.sub(r"(?s)\A---\n.*?\n---\n", "", md)
    return samples_mod.clean(md)


def prose_lines(md: str) -> list[str]:
    """Lines of running prose: no headings, list items, tables, quotes or rules."""
    out = []
    for line in strip_markup(md).splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "|", ">", "---", "```")) or re.match(r"^([-*•]|\d+[.)])\s", s):
            continue
        out.append(s)
    return out


def sentences(md: str) -> list[str]:
    text = " ".join(prose_lines(md))
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[\"'“‘(A-Z0-9])", text) if len(s.split()) >= 2]


def words(text: str) -> list[str]:
    return re.findall(r"[a-z]+(?:['’][a-z]+)?", text.lower())


def _meter(name: str, light: str, reason: str, flags: list[str] | None = None, value=None) -> dict:
    return {"meter": name, "light": light, "reason": reason, "flags": flags or [], "value": value}


def overused(md: str, allowed: list[str], banned: list[str]) -> dict:
    text = strip_markup(md).lower()
    allowed = {a.lower() for a in allowed}
    found = {}
    for label, pat in OVERUSED:
        if label in allowed:
            continue
        n = len(re.findall(pat, text))
        if n:
            found[label] = n
    for w in banned:
        if w in allowed or w in found:
            continue
        n = len(re.findall(r"\b" + re.escape(w) + r"\b", text))
        if n:
            found[w] = n
    total = sum(found.values())
    flags = [f'"{k}" ({v})' for k, v in sorted(found.items(), key=lambda kv: (-kv[1], kv[0]))]
    if not total:
        return _meter("overused words", "green", "none found", value=0)
    light = "amber" if total <= 3 else "red"
    return _meter("overused words", light, "flags " + ", ".join(flags), flags, total)


def antithesis(md: str) -> dict:
    text = " ".join(prose_lines(md))
    spans = []
    for pat in ANTITHESIS:
        for m in pat.finditer(text):
            if not any(m.start() < e and s < m.end() for s, e in spans):
                spans.append((m.start(), m.end()))
    n = len(spans)
    flags = [text[s:e].strip()[:90] for s, e in sorted(spans)]
    light = "green" if n <= 3 else "amber" if n <= 5 else "red"
    reason = f"{n} found; 2 to 3 reads as rhetoric, more as a rhythm"
    return _meter("antithesis", light, reason, flags if light != "green" else [], n)


def spread(lengths: list[int]) -> float:
    return statistics.pstdev(lengths) / statistics.mean(lengths) if lengths else 0.0


def rhythm(md: str, reference: list[str]) -> dict:
    lengths = [len(s.split()) for s in sentences(md)]
    if len(lengths) < 6:
        return _meter("rhythm", "grey", "too few sentences to judge (fewer than 6)")
    cv = spread(lengths)
    ref = [len(s.split()) for t in reference for s in sentences(t)]
    target = f"your written samples spread {spread(ref):.2f}" if len(ref) >= 6 else \
        "human writing usually spreads 0.4 or more"
    light = "red" if cv < 0.25 else "amber" if cv < 0.4 else "green"
    reason = f"sentences run {min(lengths)} to {max(lengths)} words (spread {cv:.2f}); {target}"
    return _meter("rhythm", light, reason, [reason] if light != "green" else [], round(cv, 3))


def style_profile(text: str) -> dict[str, float]:
    ws = words(text)
    n = max(len(ws), 1)
    sents = [len(s.split()) for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) >= 2] or [0]
    return {
        "first person (I, me, my, we, our)": sum(w in _FIRST for w in ws) / n,
        "second person (you, your)": sum(w in _SECOND for w in ws) / n,
        "contractions": sum(("'" in w or "’" in w) for w in ws) / n,
        "long words (9+ letters)": sum(len(w) >= 9 for w in ws) / n,
        "mean word length": sum(len(w) for w in ws) / n,
        "mean sentence length": statistics.mean(sents),
        "sentence length spread": spread(sents) if len(sents) > 1 else 0.0,
        "commas": text.count(",") / n,
        "brackets": text.count("(") / n,
        "questions": text.count("?") / n,
        "exclamations": text.count("!") / n,
        "spaced hyphens and ampersands": (text.count(" - ") + text.count("&")) / n,
        '"the" and "of"': sum(w in ("the", "of") for w in ws) / n,
    }


def style_vector(text: str) -> list[float]:
    prof = style_profile(text)
    return [prof[k] / scale for k, scale in STYLE_FEATURES.items()]


def distance(a: list[float], b: list[float]) -> float:
    """Root-mean-square difference of the scaled style rates: 0 is identical; about 1 is
    one typical spread on every feature."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)) / max(len(a), 1))


def _centroid(vecs: list[list[float]]) -> list[float]:
    return [sum(col) / len(vecs) for col in zip(*vecs)]


def is_it_me(md: str, written: list[str]) -> dict:
    if not written:
        return _meter("is it me?", "grey", "no samples yet")
    vecs = [style_vector(" ".join(prose_lines(t)) or strip_markup(t)) for t in written]
    draft_vec = style_vector(" ".join(prose_lines(md)))
    centre = _centroid(vecs)
    d = distance(draft_vec, centre)
    if len(vecs) >= 2:
        own = statistics.median(distance(v, _centroid(vecs[:i] + vecs[i + 1:])) for i, v in enumerate(vecs))
        green, amber = max(own, 1.0), max(own * 1.6, 1.6)
        basis = f"your own samples sit at {own:.2f} from each other"
    else:
        green, amber, basis = 1.0, 1.6, "one sample, so fixed limits of 1.0 and 1.6"
    light = "green" if d <= green else "amber" if d <= amber else "red"
    gaps = sorted(zip(STYLE_FEATURES, draft_vec, centre), key=lambda r: -abs(r[1] - r[2]))[:2]
    biggest = ", ".join(f"{name} {'higher' if a > b else 'lower'}" for name, a, b in gaps)
    reason = f"distance {d:.2f} from your written samples ({basis}); biggest gaps: {biggest}"
    return _meter("is it me?", light, reason, [reason] if light != "green" else [], round(d, 4))


def _count_phrase(text: str, phrase: str) -> int:
    return len(re.findall(r"(?<![A-Za-z])" + re.escape(phrase.lower()) + r"(?![A-Za-z])", text))


def informality(md: str, fp: dict, dial: str) -> dict:
    text = " ".join(prose_lines(md)).lower()
    cap = settings_mod.PHRASE_CAP[dial]
    used = sum(_count_phrase(text, p) for p in fp.get("signature", []))
    leave = [p for p in fp.get("leave_out", []) if _count_phrase(text, p)]
    if not fp.get("signature") and not fp.get("leave_out"):
        return _meter("informality", "grey", "no phrase fingerprint yet")
    flags, parts = [], [f"{used} used; the cap is {cap}"]
    light = "green"
    if used > cap:
        light = "amber"
        flags.append(parts[0])
    if leave:
        light = "amber"
        msg = "phrases to leave out: " + ", ".join(f'"{p}"' for p in leave)
        parts.append(msg)
        flags.append(msg)
    return _meter("informality", light, "; ".join(parts), flags, used)


# --- AI detector (spec 028) -------------------------------------------------------------

Transport = Callable[[str, str, dict | None, dict], dict]  # (method, url, json_body, headers) -> json


def _http(method: str, url: str, body: dict | None, headers: dict) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:  # noqa: S310 (fixed https URL)
        return json.loads(r.read().decode() or "{}")


PANGRAM_URL = "https://text.external-api.pangram.com/task"


def pangram_score(text: str, key: str, transport: Transport = _http, poll_seconds: float = 2.0,
                  max_polls: int = 30) -> float:
    """AI share = fraction_ai + 0.5 x fraction_ai_assisted (as in the bake-off)."""
    headers = {"x-api-key": key, "Content-Type": "application/json"}
    task = transport("POST", PANGRAM_URL, {"text": text}, headers)["task_id"]
    for _ in range(max_polls):
        r = transport("GET", f"{PANGRAM_URL}/{task}", None, headers)
        if r.get("stage") == "STAGE_SUCCESS":
            return float(r.get("fraction_ai", 0)) + 0.5 * float(r.get("fraction_ai_assisted", 0))
        if r.get("stage") == "STAGE_FAILED":
            raise RuntimeError("Pangram could not score the text")
        time.sleep(poll_seconds)
    raise RuntimeError("Pangram did not finish in time")


def is_published(root: Path, path: Path) -> bool:
    try:
        rel = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return False
    return rel.startswith("profile/corpus/") or path.name == "published.md"


def ai_detector(root: Path, path: Path, md: str, on: bool, env: dict,
                transport: Transport = _http, poll_seconds: float = 2.0) -> dict:
    if not on:
        return _meter("AI detector", "grey", "AI detector: off")
    key = env.get("PANGRAM_API_KEY")
    if not key:
        return _meter("AI detector", "grey", "Pangram key not set (set PANGRAM_API_KEY on this machine)")
    if not is_published(root, path):
        return _meter("AI detector", "grey", "AI detector: published text only")
    try:
        share = pangram_score(strip_markup(md), key, transport, poll_seconds)
    except Exception as e:  # any failure is a warning, never a stop
        return _meter("AI detector", "grey", f"Pangram could not be reached ({type(e).__name__}); scored without it")
    light = "green" if share < 0.2 else "amber" if share < 0.5 else "red"
    return _meter("AI detector", light, f"Pangram AI share {share:.0%}", value=round(share, 3))


# --- the scorecard ----------------------------------------------------------------------

def score(root: Path, path: Path, env: dict | None = None, transport: Transport = _http,
          poll_seconds: float = 2.0) -> list[dict]:
    env = os.environ if env is None else env
    md = path.read_text(encoding="utf-8")
    s = settings_mod.load(root)
    if not s["modules"]["meters"]:
        return [_meter("meters", "grey", "meters are switched off in profile/settings.yaml")]
    written = [x.text for x in samples_mod.references(root, "written")]
    fp = samples_mod.fingerprint(root)
    return [
        overused(md, s["allowed_words"], s["banned_words"]),
        antithesis(md),
        rhythm(md, rhythm_reference(root)),
        is_it_me(md, written),
        informality(md, fp, s["informality"]),
        ai_detector(root, path, md, s["modules"]["pangram"], env, transport, poll_seconds),
    ]


def rhythm_reference(root: Path) -> list[str]:
    """Spec 027-02: only written samples judge sentence rhythm."""
    return [x.text for x in samples_mod.references(root, "written")]


def phrasing_reference(root: Path) -> list[str]:
    """Written and spoken samples both count for phrasing."""
    return [x.text for x in samples_mod.references(root) if x.kind in ("written", "spoken")]


def _version() -> str:
    p = SKILL_DIR / "VERSION"
    return p.read_text(encoding="utf-8").strip() if p.exists() else "?"


def render(results: list[dict], draft: str) -> str:
    lines = ["# Scorecard", "",
             f"Scored: `{draft}` on {dt.date.today().isoformat()} (engine {_version()}).",
             "Lights are warnings, never stops. Reasons say what each meter saw.", "",
             "| Meter | Light | Reason |", "|---|---|---|"]
    lines += [f"| {r['meter']} | {r['light']} | {r['reason']} |" for r in results]
    flags = [(r["meter"], f) for r in results for f in r["flags"]]
    lines += ["", "## Flags", "",
              "Your call on each flag: `accepted` (you changed the line) or `ignored` (you kept it).",
              "After three articles, these calls tune the meters (spec 029-09).", "",
              "| # | Meter | Flag | Your call |", "|---|---|---|---|"]
    lines += [f"| {i} | {m} | {f} | open |" for i, (m, f) in enumerate(flags, 1)] or ["| - | - | none | - |"]
    return "\n".join(lines) + "\n"


def scorecard_path(root: Path, path: Path) -> Path | None:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 3 and parts[0] == "articles":
        return root / "articles" / parts[1] / "scorecard.md"
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("draft", type=Path)
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true", help="print the results as JSON")
    args = ap.parse_args(argv)
    if not args.draft.exists():
        print(f"No such file: {args.draft}")
        return 2
    results = score(args.root, args.draft)
    rel = args.draft.resolve()
    try:
        rel = rel.relative_to(args.root.resolve())
    except ValueError:
        pass
    text = render(results, Path(rel).as_posix())
    out = scorecard_path(args.root, args.draft)
    if out:
        out.write_text(text, encoding="utf-8")
    print(json.dumps(results, indent=2) if args.json else text)
    if out:
        print(f"Saved to {out.relative_to(args.root).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
