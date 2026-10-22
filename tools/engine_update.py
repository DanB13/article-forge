#!/usr/bin/env python3
"""Bring a newer engine release into a writer's repo, on a branch, for review (specs 014 and 016).

The engine-update workflow runs this in the writer's repo. It:
  1. picks the target release tag from upstream: the newest final release, or on
     the "rc" channel the newest release or release candidate;
  2. stops if that release is already merged;
  3. if the update branch was pushed before but has no open pull request, asks
     for one (a half-finished update) and stops;
  4. merges the release on a new branch (the first merge into a template copy
     needs --allow-unrelated-histories and -X theirs);
  5. refuses the update if it would change profile/ or articles/;
  6. pushes the branch and asks for a pull request.

Results go to GITHUB_OUTPUT (when set) as action=none|open_pr|conflict|refused,
plus branch, tag, version and files. Pushing uses the checkout's credentials
(the ENGINE_UPDATE_TOKEN secret); the workflow opens pull requests and issues
with its own token.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

PROTECTED = ("profile/", "articles/")
TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:-rc(\d+))?$")
VERSION_FILE = ".claude/skills/article-forge/VERSION"


def tag_key(tag: str) -> tuple[int, int, int, int, int]:
    """Sort key: a final release ranks above its own candidates."""
    m = TAG.match(tag)
    if not m:
        raise ValueError(tag)
    major, minor, patch, rc = m.groups()
    return (int(major), int(minor), int(patch), 0 if rc else 1, int(rc or 0))


def pick_target(tags: list[str], channel: str = "release") -> str | None:
    """The tag to update to. channel 'release' ignores candidates; 'rc' takes the newest of either."""
    valid = [t for t in tags if TAG.match(t)]
    if channel != "rc":
        valid = [t for t in valid if TAG.match(t).group(4) is None]
    return max(valid, key=tag_key) if valid else None


def protected_files(paths: list[str]) -> list[str]:
    return sorted(p for p in paths if p.startswith(PROTECTED))


@dataclass
class Result:
    action: str  # none | open_pr | conflict | refused
    message: str
    branch: str = ""
    tag: str = ""
    version: str = ""
    files: list[str] = field(default_factory=list)


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=repo, check=check, capture_output=True, text=True)


def _gh_pr_open(repo: Path, branch: str) -> bool:
    out = subprocess.run(["gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number"],
                         cwd=repo, check=True, capture_output=True, text=True).stdout
    return bool(json.loads(out or "[]"))


def _remove_files_upstream_deleted(repo: Path, target: str) -> None:
    """After a first (unrelated-histories) merge, git keeps every file only the writer's side
    has, including engine files that upstream deleted after the template was made. Remove
    those: files that came with the template (the writer's first commit), are gone from the
    release, and are outside the writer's own folders."""
    roots = _git(repo, "rev-list", "--max-parents=0", "HEAD^1").stdout.split()
    from_template = {f for r in roots for f in _git(repo, "ls-tree", "-r", "--name-only", r).stdout.splitlines()}
    in_release = set(_git(repo, "ls-tree", "-r", "--name-only", target).stdout.splitlines())
    present = set(_git(repo, "ls-tree", "-r", "--name-only", "HEAD").stdout.splitlines())
    stale = sorted(f for f in (from_template & present) - in_release
                   if not f.startswith(PROTECTED + ("local/",)))
    if stale:
        _git(repo, "rm", "-q", "--", *stale)
        _git(repo, "commit", "-q", "--amend", "--no-edit")


def run(repo: Path, upstream: str, channel: str = "release", remote: str = "origin",
        pr_is_open=_gh_pr_open) -> Result:
    if "upstream" not in _git(repo, "remote").stdout.split():
        _git(repo, "remote", "add", "upstream", upstream)
    else:
        _git(repo, "remote", "set-url", "upstream", upstream)
    _git(repo, "fetch", "--quiet", "--tags", "--force", "upstream")
    tags = [line.split("refs/tags/")[1] for line in _git(repo, "ls-remote", "--tags", "--refs", "upstream").stdout.splitlines()]
    tag = pick_target(tags, channel)
    if tag is None:
        return Result("none", f"No {'release or candidate' if channel == 'rc' else 'final release'} found upstream.")
    target = _git(repo, "rev-parse", f"{tag}^{{commit}}").stdout.strip()
    version = _git(repo, "show", f"{target}:{VERSION_FILE}").stdout.strip()

    if _git(repo, "merge-base", "--is-ancestor", target, "HEAD", check=False).returncode == 0:
        return Result("none", f"Engine is up to date ({tag}).", tag=tag, version=version)

    branch = f"engine-update/{tag}"
    if _git(repo, "ls-remote", "--exit-code", "--heads", remote, branch, check=False).returncode == 0:
        if pr_is_open(repo, branch):
            return Result("none", f"A pull request for {branch} is already open.", branch, tag, version)
        return Result("open_pr", f"{branch} was pushed earlier without a pull request; opening one now.",
                      branch, tag, version)

    base = _git(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "checkout", "-q", "-b", branch)
    args = ["merge", "--no-edit", "-m", f"Engine update to {tag}"]
    first_merge = _git(repo, "merge-base", "HEAD", target, check=False).returncode != 0
    if first_merge:
        # A copy made from the template shares no history with upstream. Its first
        # merge takes the engine files from upstream; profile/ and articles/ are
        # never shipped upstream, so they are not affected.
        args += ["--allow-unrelated-histories", "-X", "theirs"]
    if _git(repo, *args, target, check=False).returncode != 0:
        files = _git(repo, "diff", "--name-only", "--diff-filter=U").stdout.splitlines()
        _git(repo, "merge", "--abort", check=False)
        _git(repo, "checkout", "-q", "-")
        _git(repo, "branch", "-q", "-D", branch)
        return Result("conflict", f"The merge of {tag} stopped on conflicts.", branch, tag, version, files)
    if first_merge:
        _remove_files_upstream_deleted(repo, target)

    changed = _git(repo, "diff", "--name-only", base, "HEAD").stdout.splitlines()
    refused = protected_files(changed)
    if refused:
        _git(repo, "checkout", "-q", "-")
        _git(repo, "branch", "-q", "-D", branch)
        return Result("refused", f"{tag} would change your own folders, so nothing was pushed.",
                      branch, tag, version, refused)

    _git(repo, "push", "--quiet", remote, branch)
    return Result("open_pr", f"Merged {tag} on {branch}.", branch, tag, version)


def pr_body(repo: Path, tag: str) -> str:
    changelog = _git(repo, "show", f"{tag}:CHANGELOG.md", check=False).stdout
    sections = re.split(r"(?m)^(?=## )", changelog)
    top = next((s for s in sections if s.startswith("## ")), "")
    return (top.rstrip() + "\n\n---\nOpened automatically by the engine-update workflow. "
            "Review the diff, then merge with **Create a merge commit** (never squash).\n"
            "This update changes no file in profile/ or articles/: the workflow refuses any that would.\n")


def write_outputs(result: Result, path: str | None) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"action={result.action}\nbranch={result.branch}\ntag={result.tag}\nversion={result.version}\n")
        f.write("files<<EOF\n" + "\n".join(f"- {x}" for x in result.files) + "\nEOF\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--upstream", default="https://github.com/DanB13/article-forge.git")
    ap.add_argument("--channel", default="release", choices=["release", "rc"])
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--body-file", type=Path, default=Path("pr-body.md"))
    args = ap.parse_args(argv)
    result = run(args.repo, args.upstream, args.channel)
    print(result.message)
    for f in result.files:
        print(f"  - {f}")
    if result.action == "open_pr":
        args.body_file.write_text(pr_body(args.repo, result.tag), encoding="utf-8")
    write_outputs(result, os.environ.get("GITHUB_OUTPUT"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
