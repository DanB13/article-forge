#!/usr/bin/env python3
"""Apply profile format changes (migrations), in order, only with the writer's approval.

Run from the repo root:
  python <skill-dir>/scripts/migrate.py status      list migrations that have not run yet
  python <skill-dir>/scripts/migrate.py plan        show the change each waiting migration would make
  python <skill-dir>/scripts/migrate.py apply       the same as plan: nothing is written without --yes
  python <skill-dir>/scripts/migrate.py apply --yes apply them, after the writer has said yes

Migrations live in <skill-dir>/migrations/ (engine) and local/migrations/ (private to
this repo). Each is a file NNNN_name.py (private: LNNNN_name.py) that defines:
  ID = "0001"
  DESCRIPTION = "one line the writer can understand"
  def plan(root: Path) -> dict[str, str]: {relative path: new file content}; {} if nothing to do

Applied migrations are recorded in profile/.engine-migrations.json. A profile with
no record counts as being before the first migration. Before a file changes, a
copy goes to profile/.backups/<time>-<id>/<path>, so every change can be undone.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
RECORD = Path("profile/.engine-migrations.json")
BACKUPS = Path("profile/.backups")
NAME = re.compile(r"^(L?\d{4})_[a-z0-9_]+\.py$")


@dataclass
class Migration:
    id: str
    description: str
    path: Path
    module: object

    def plan(self, root: Path) -> dict[str, str]:
        return self.module.plan(root)  # type: ignore[attr-defined]


def _load(path: Path) -> Migration:
    spec = importlib.util.spec_from_file_location(f"af_migration_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return Migration(str(mod.ID), str(mod.DESCRIPTION), path, mod)


def discover(root: Path, dirs: list[Path] | None = None) -> list[Migration]:
    dirs = dirs if dirs is not None else [SKILL_DIR / "migrations", root / "local" / "migrations"]
    found = [_load(p) for d in dirs if d.is_dir() for p in sorted(d.iterdir()) if NAME.match(p.name)]
    ids = [m.id for m in found]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise SystemExit(f"Two migrations share an ID: {', '.join(sorted(dupes))}")
    # Engine migrations (0001...) run before private ones (L0001...), each in number order.
    return sorted(found, key=lambda m: (m.id.startswith("L"), m.id))


def read_record(root: Path) -> list[dict]:
    p = root / RECORD
    return json.loads(p.read_text(encoding="utf-8")).get("applied", []) if p.exists() else []


def write_record(root: Path, applied: list[dict]) -> None:
    p = root / RECORD
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"applied": applied}, indent=2) + "\n", encoding="utf-8")


def waiting(root: Path, migrations: list[Migration]) -> list[Migration]:
    done = {a["id"] for a in read_record(root)}
    return [m for m in migrations if m.id not in done]


def mark_all_applied(root: Path, migrations: list[Migration] | None = None) -> None:
    """For a brand-new profile: it already has the latest format, so nothing should wait."""
    migrations = discover(root) if migrations is None else migrations
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    write_record(root, [{"id": m.id, "at": now, "note": "new profile"} for m in migrations])


def _diff(rel: str, old: str, new: str) -> str:
    return "".join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), f"a/{rel}", f"b/{rel}"))


def apply(root: Path, migrations: list[Migration], yes: bool) -> tuple[list[str], list[str]]:
    """Returns (report lines, changed paths). Without yes, only reports; with yes, applies in order."""
    lines, changed = [], []
    record = read_record(root)
    pending = waiting(root, migrations)
    if not pending:
        return ["No migrations are waiting."], []
    if not yes:
        # Rehearse on a copy, so each change shows against the state the earlier ones leave.
        lines.append(f"{len(pending)} migration(s) waiting. Nothing has been changed.")
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp)
            for folder in ("profile", "articles"):
                if (root / folder).is_dir():
                    shutil.copytree(root / folder, sandbox / folder)
            for m in pending:
                lines.append(f"\n{m.id}: {m.description}")
                changes = m.plan(sandbox)
                for rel, new in sorted(changes.items()):
                    target = sandbox / rel
                    old = target.read_text(encoding="utf-8") if target.exists() else ""
                    lines.append(_diff(rel, old, new) or f"  {rel}: no change")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(new, encoding="utf-8")
                if not changes:
                    lines.append("  no change needed")
        lines.append("\nAfter the writer approves, run: migrate.py apply --yes")
        return lines, []
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for m in pending:
        changes = m.plan(root)
        for rel, new in sorted(changes.items()):
            target = root / rel
            old = target.read_text(encoding="utf-8") if target.exists() else None
            if old == new:
                continue
            if old is not None:
                backup = root / BACKUPS / f"{stamp}-{m.id}" / rel
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup.write_text(old, encoding="utf-8")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(new, encoding="utf-8")
            changed.append(rel)
        record.append({"id": m.id, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
        write_record(root, record)
        lines.append(f"Applied {m.id}: {m.description}")
    if changed:
        lines.append(f"Backups of the original files are in {BACKUPS.as_posix()}/{stamp}-*/")
    return lines, changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["status", "plan", "apply"])
    ap.add_argument("--yes", action="store_true", help="apply the changes (only after the writer approves)")
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--migrations-dir", type=Path, action="append", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    migrations = discover(args.root, args.migrations_dir)
    if args.command == "status":
        pending = waiting(args.root, migrations)
        if not pending:
            print("No migrations are waiting.")
        for m in pending:
            print(f"WAITING {m.id}: {m.description}")
        return 0
    lines, _ = apply(args.root, migrations, yes=args.command == "apply" and args.yes)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
