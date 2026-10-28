#!/usr/bin/env python3
"""Check that engine updates can reach this repo (spec 017).

Run from your repo root: python .claude/skills/article-forge/scripts/check_setup.py

It uses the GitHub CLI (gh) to read two settings:
  1. "Allow GitHub Actions to create and approve pull requests" must be on,
     or the weekly engine-update workflow cannot open its pull request.
  2. The ENGINE_UPDATE_TOKEN secret is optional. Without it, an update that
     changes workflow files opens an issue with the commands to merge it by hand.
It also reports the update channel (ENGINE_CHANNEL: release or rc).
If gh is missing or not signed in, it explains how to check by hand.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from typing import Callable

Runner = Callable[[list[str]], "tuple[int, str]"]

FIX_PRS = ("  Fix: Settings > Actions > General > Workflow permissions > tick "
           "'Allow GitHub Actions to create and approve pull requests' > Save.")
FIX_TOKEN = ("  To add it: create a fine-grained token (Settings > Developer settings > Personal access tokens > "
             "Fine-grained tokens) for this repo only, with Contents and Workflows set to Read and write.\n"
             "  Then save it in this repo: Settings > Secrets and variables > Actions > New repository secret, "
             "named ENGINE_UPDATE_TOKEN.")
MANUAL = """The GitHub CLI (gh) is not installed or not signed in, so check these by hand
in your repo on github.com:

  1. Settings > Actions > General > Workflow permissions:
     'Allow GitHub Actions to create and approve pull requests' is ticked.
  2. Settings > Secrets and variables > Actions > Secrets:
     optional: a secret named ENGINE_UPDATE_TOKEN exists. Without it, updates that change
     workflow files open an issue with the commands to merge them by hand.
  3. Optional, same page > Variables: ENGINE_CHANNEL is 'rc' to get release candidates.

To let this script check for you: install gh (https://cli.github.com) and run `gh auth login`."""


def _run(cmd: list[str]) -> tuple[int, str]:
    if not shutil.which(cmd[0]):
        return 127, ""
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout


def check(run: Runner = _run) -> tuple[list[str], bool]:
    """Returns (report lines, all_ok)."""
    rc, _ = run(["gh", "auth", "status"])
    if rc != 0:
        return [MANUAL], True  # cannot tell; not an error
    rc, slug = run(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"])
    slug = slug.strip()
    if rc != 0 or not slug:
        return ["Could not tell which GitHub repo this is. Run the check from your repo folder.", MANUAL], True
    lines, ok = [f"Checking {slug}"], True

    rc, out = run(["gh", "api", f"repos/{slug}/actions/permissions/workflow"])
    if rc != 0:
        lines.append("? Update PRs: could not read the setting (you may need admin access).\n" + FIX_PRS)
        ok = False
    elif json.loads(out or "{}").get("can_approve_pull_request_reviews"):
        lines.append("OK Update PRs: on")
    else:
        lines.append("MISSING Update PRs: off\n" + FIX_PRS)
        ok = False

    rc, out = run(["gh", "api", f"repos/{slug}/actions/secrets", "--jq", ".secrets[].name"])
    if rc != 0:
        lines.append("? Token: could not list secrets.\n" + FIX_TOKEN)
        ok = False
    elif "ENGINE_UPDATE_TOKEN" in out.split():
        lines.append("OK Token: ENGINE_UPDATE_TOKEN present")
    else:
        lines.append("OPTIONAL Token: no ENGINE_UPDATE_TOKEN secret. Updates that change workflow files "
                     "will open an issue with the commands to merge them by hand.\n" + FIX_TOKEN)

    rc, out = run(["gh", "api", f"repos/{slug}/actions/variables/ENGINE_CHANNEL", "--jq", ".value"])
    channel = out.strip() if rc == 0 and out.strip() else "release"
    lines.append(f"INFO Update channel: {channel}"
                 + (" (final releases only)" if channel != "rc" else " (release candidates too)"))
    return lines, ok


def main() -> int:
    lines, ok = check()
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
