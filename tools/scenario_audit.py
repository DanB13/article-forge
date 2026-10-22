"""Audit a pytest run against the specs (spec 018): only eval scenarios may be skipped,
and on a full run every code scenario must have run.

tests/conftest.py calls this at the end of every pytest session.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

ENGINE_REPO = "DanB13/article-forge"

Key = tuple[str, str]  # (feature file name, scenario title)


def is_engine_repo(root: Path) -> bool:
    """True in the public engine repo; False in a writer's copy. @upstream checks run only here."""
    if os.environ.get("ARTICLE_FORGE_ENGINE_REPO") in ("1", "0"):
        return os.environ["ARTICLE_FORGE_ENGINE_REPO"] == "1"
    if os.environ.get("GITHUB_REPOSITORY"):
        return os.environ["GITHUB_REPOSITORY"].lower() == ENGINE_REPO.lower()
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=root, capture_output=True,
                             text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return False
    return bool(re.search(rf"[:/]{re.escape(ENGINE_REPO)}(\.git)?$", url, re.I))


def expected_scenarios(report_ids: dict[str, dict]) -> dict[Key, dict]:
    return {(info["spec"], info["title"]): info for info in report_ids.values() if "kind" in info}


def audit(expected: dict[Key, dict], collected: set[Key], skipped: dict[Key, str],
          full_run: bool, engine_repo: bool) -> list[str]:
    problems = []
    for key, reason in sorted(skipped.items()):
        info = expected.get(key)
        if info is None or info.get("kind") == "eval":
            continue
        if info.get("upstream_only") and not engine_repo:
            continue
        problems.append(f"code scenario '{key[1]}' ({key[0]}) was skipped ({reason}); "
                        "only eval scenarios may be skipped")
    if full_run:
        for key, info in sorted(expected.items()):
            if info.get("kind") == "code" and key not in collected:
                problems.append(f"code scenario '{key[1]}' ({key[0]}) never ran: no test collected it")
    return problems
