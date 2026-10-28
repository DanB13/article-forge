#!/usr/bin/env python3
"""The writer's settings and the optional modules (spec 028).

profile/settings.yaml holds switches only. Keys never go in it: each module that
needs one reads it from an environment variable.

Run: python <skill-dir>/scripts/settings.py [--root .]   lists every module, whether it
is on, and whether it sends the writer's text off this machine.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

SETTINGS = Path("profile/settings.yaml")
DIAL = ("off", "light", "warm")
PHRASE_CAP = {"off": 0, "light": 3, "warm": 6}

# Every optional module: what it does, whether text leaves the machine, its key, its default.
MODULES = {
    "meters": {"what": "rule-based meters and the scorecard", "leaves_machine": False,
               "key_env": None, "default": True},
    "pangram": {"what": "Pangram AI-text detector, on published text only", "leaves_machine": True,
                "key_env": "PANGRAM_API_KEY", "default": False},
}

DEFAULTS = {"informality": "light", "allowed_words": [], "banned_words": [],
            "modules": {name: m["default"] for name, m in MODULES.items()}}

_KEYISH_NAME = re.compile(r"(?i)(api[_-]?key|token|secret|password)")
_KEYISH_VALUE = re.compile(r"^[A-Za-z0-9_\-\.]{24,}$")


def _onoff(v) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("on", "true", "yes", "1")


def _dial(v) -> str:
    if v is False:
        return "off"  # YAML reads a bare off as false
    v = str(v).strip().lower()
    return v if v in DIAL else "light"


def load(root: Path) -> dict:
    """Settings with defaults filled in. A missing file means every default."""
    p = root / SETTINGS
    raw = (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}
    modules = dict(DEFAULTS["modules"])
    for name, val in (raw.get("modules") or {}).items():
        if name in MODULES:
            modules[name] = _onoff(val)
    if "meters" in raw:
        modules["meters"] = _onoff(raw["meters"])
    return {
        "informality": _dial(raw.get("informality", DEFAULTS["informality"])),
        "allowed_words": [str(w).lower() for w in raw.get("allowed_words") or []],
        "banned_words": [str(w).lower() for w in raw.get("banned_words") or []],
        "modules": modules,
    }


def key_problems(root: Path) -> list[str]:
    """Spec 028-06: a key written into the settings file is refused."""
    p = root / SETTINGS
    if not p.exists():
        return []
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    found = []

    def walk(node, path=""):
        if isinstance(node, dict):
            for k, v in node.items():
                here = f"{path}.{k}" if path else str(k)
                if isinstance(v, (str, int)) and v != "" and (_KEYISH_NAME.search(str(k))
                                                             or _KEYISH_VALUE.match(str(v))):
                    found.append(here)
                walk(v, here)
        elif isinstance(node, list):
            for v in node:
                if isinstance(v, str) and _KEYISH_VALUE.match(v):
                    found.append(path)

    walk(raw)
    return [f"{SETTINGS.as_posix()} holds what looks like a key ({f}): keys belong in environment "
            f"variables, not profile/settings.yaml" for f in sorted(set(found))]


def module_status(root: Path, env: dict | None = None) -> list[dict]:
    env = os.environ if env is None else env
    on = load(root)["modules"]
    rows = []
    for name, m in MODULES.items():
        key = m["key_env"]
        rows.append({"module": name, "on": on[name], "what": m["what"], "leaves_machine": m["leaves_machine"],
                     "key_env": key, "key_set": bool(env.get(key)) if key else None})
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    s = load(args.root)
    print(f"Informality: {s['informality']} (signature phrases per article: at most {PHRASE_CAP[s['informality']]})")
    for r in module_status(args.root):
        leaves = "sends your text off this machine" if r["leaves_machine"] else "stays on this machine"
        key = "" if not r["key_env"] else f"; key {r['key_env']} {'set' if r['key_set'] else 'not set'}"
        print(f"{r['module']}: {'on' if r['on'] else 'off'}. {r['what']}; {leaves}{key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
