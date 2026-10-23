"""Test integrity checks used by check_specs.py (specs 020, 021, 022, 024, 025, 026).

- Fingerprints of every test: scenario wording, graders, eval cases (prompt, setup,
  resources, grading metadata), fixtures and the pass rules. A change to one that
  the last release recorded needs a test-change record (specs/test-changes.yaml).
- Grading metadata (evals/<case>/grading.yaml): every grader names the scenario it
  checks and a tier; AI judges state why no exact check works; every "must not"
  grader has a "did the work" partner; every case names its mutant.
- Every numbered rule in SKILL.md names the scenarios that test it.
- Every guard in tools/guards.yaml names a scenario proving it fails on bad input.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import yaml

SKILL = Path(".claude/skills/article-forge")
POLICY = "grading-policy.yaml"
RECORD_FIELDS = ("item", "reason", "approved_by", "date")
RULES_HEADING = "## Non-negotiable rules"
RULE_LINE = re.compile(r"^(\d+)\. \*\*")
RULE_SPECS = re.compile(r"<!--\s*specs:\s*([^>]*?)\s*-->")


def _hash_bytes(*parts: bytes) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p + b"\0")
    return h.hexdigest()[:16]


def hash_text(text: str) -> str:
    return _hash_bytes(text.strip().encode())


def hash_tree(path: Path) -> str:
    if path.is_file():
        return _hash_bytes(path.read_bytes())
    parts = []
    for p in sorted(path.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            parts += [p.relative_to(path).as_posix().encode(), p.read_bytes()]
    return _hash_bytes(*parts)


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    return (yaml.safe_load(parts[1]) or {}) if len(parts) >= 3 else {}


def eval_dirs(root: Path) -> list[Path]:
    return [d for d in (root / SKILL / "evals", root / "local" / "evals") if d.is_dir()]


def eval_cases(root: Path) -> dict[str, Path]:
    return {c.name: c for d in eval_dirs(root) for c in sorted(d.iterdir())
            if c.is_dir() and ((c / "prompt.md").exists() or (c / "case.yaml").exists())}


def policy(root: Path) -> dict | None:
    p = root / SKILL / "evals" / POLICY
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else None


def fingerprints(root: Path, scenario_hashes: dict[str, str]) -> dict[str, str]:
    """Every test item the ledger tracks, keyed 'scenario:ID', 'grader:case/name', 'case:case',
    'fixture:name', 'steps:test_file.py' (pytest step definitions) and 'policy'."""
    out = {f"scenario:{sid}": h for sid, h in scenario_hashes.items()}
    for name, case in eval_cases(root).items():
        for g in sorted((case / "graders").glob("*.md")):
            out[f"grader:{name}/{g.stem}"] = hash_tree(g)
        parts = []
        for p in sorted(case.rglob("*")):
            if p.is_file() and "graders" not in p.relative_to(case).parts and "__pycache__" not in p.parts:
                parts += [p.relative_to(case).as_posix().encode(), p.read_bytes()]
        out[f"case:{name}"] = _hash_bytes(*parts)
    for d in eval_dirs(root):
        fx = d / "_fixtures"
        if fx.is_dir():
            for f in sorted(fx.iterdir()):
                out[f"fixture:{f.name}"] = hash_tree(f)
    for step_file in sorted((root / "tests").glob("test_*.py")) if (root / "tests").is_dir() else []:
        out[f"steps:{step_file.name}"] = hash_tree(step_file)
    if (root / "tests" / "fixtures").is_dir():
        out["fixture:tests"] = hash_tree(root / "tests" / "fixtures")
    pol = root / SKILL / "evals" / POLICY
    if pol.exists():
        out["policy"] = hash_tree(pol)
    return out


def load_records(root: Path, name: str) -> tuple[list[dict], list[str]]:
    p = root / "specs" / name
    if not p.exists():
        return [], []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or []
    good, problems = [], []
    for i, rec in enumerate(data if isinstance(data, list) else []):
        missing = [f for f in RECORD_FIELDS if not (isinstance(rec, dict) and rec.get(f))]
        if missing:
            problems.append(f"{name} entry {i + 1}: missing {', '.join(missing)}")
        else:
            good.append(rec)
    return good, problems


def check_changes(root: Path, recorded: dict[str, str], current: dict[str, str]) -> list[str]:
    """A tracked test item whose fingerprint changed needs a test-change record."""
    records, problems = load_records(root, "test-changes.yaml")
    approved = {str(r["item"]) for r in records}
    for item, old in sorted(recorded.items()):
        new = current.get(item)
        if new is None or new == old or item in approved:
            continue  # removals are the retire rule's job (spec 018)
        what = "policy changed (pass rules)" if item == "policy" else f"{item} changed"
        problems.append(f"{what} since the last release: add a test-change record to "
                        "specs/test-changes.yaml with the reason and who approved it")
    return problems


def is_negative(fm: dict) -> bool:
    return (fm.get("match") == "not_contains" or fm.get("exists") is False
            or (fm.get("type") == "tool_used" and fm.get("max") == 0))


def check_grading(root: Path, eval_scenarios: dict[str, set[str]]) -> list[str]:
    """eval_scenarios maps a case name to the scenario IDs that use it."""
    pol = policy(root)
    if pol is None:
        return []
    tiers = set((pol.get("tiers") or {}).keys())
    problems = []
    for name, case in eval_cases(root).items():
        gfile = case / "grading.yaml"
        if not gfile.exists():
            problems.append(f"{name} has no grading.yaml: it names no mutant and no grader metadata")
            continue
        meta = yaml.safe_load(gfile.read_text(encoding="utf-8")) or {}
        graders = {g.stem: _frontmatter(g) for g in sorted((case / "graders").glob("*.md"))}
        entries = meta.get("graders") or {}
        case_tier = meta.get("tier")
        for g in sorted(set(graders) - set(entries)):
            problems.append(f"{name}/{g} names no scenario: add it to {name}/grading.yaml with checks: NNN-NN")
        for g in sorted(set(entries) - set(graders)):
            problems.append(f"{name}/grading.yaml lists '{g}', which is not a grader of this case")
        for g, fm in graders.items():
            e = entries.get(g) or {}
            sid = str(e.get("checks", ""))
            if g in entries and not sid:
                problems.append(f"{name}/{g} names no scenario (checks: NNN-NN)")
            elif sid and sid not in eval_scenarios.get(name, set()):
                problems.append(f"{name}/{g} checks {sid}, which is not a scenario of this case")
            tier = e.get("tier", case_tier)
            if tier not in tiers:
                problems.append(f"{name}/{g} has no tier" if tier is None else f"{name}/{g} has unknown tier '{tier}'")
            if fm.get("type") in ("llm", "baseline") and not e.get("reason"):
                problems.append(f"{name}/{g} is an AI judge and needs a reason: why no exact check can do this")
            if is_negative(fm):
                pair = e.get("pair")
                pfm = graders.get(pair) if pair else None
                if not pair or pfm is None or is_negative(pfm) or (pfm.get("type") == "tool_used" and pfm.get("tool") == "Skill"):
                    problems.append(f"{name}/{g} is a 'must not' check with no did-the-work partner (pair: <positive grader>)")
        mutant = meta.get("mutant") or []
        if not mutant:
            problems.append(f"{name} names no mutant: the engine text this case depends on")
        for m in mutant:
            target = root / SKILL / str(m.get("file", ""))
            text = str(m.get("text", ""))
            count = target.read_text(encoding="utf-8").count(text) if target.is_file() and text else 0
            if count != 1:
                problems.append(f"{name} mutant text not found exactly once in {m.get('file')} (found {count})")
    return problems


def check_rules(root: Path, ids: set[str]) -> list[str]:
    skill_md = root / SKILL / "SKILL.md"
    if not skill_md.exists():
        return []
    text = skill_md.read_text(encoding="utf-8")
    if RULES_HEADING not in text:
        return ["SKILL.md has no '## Non-negotiable rules' section"]
    section = text.split(RULES_HEADING, 1)[1].split("\n## ", 1)[0]
    problems = []
    for line in section.splitlines():
        m = RULE_LINE.match(line)
        if not m:
            continue
        found = RULE_SPECS.search(line)
        named = [s.strip() for s in found.group(1).split(",") if s.strip()] if found else []
        if not named:
            problems.append(f"rule {m.group(1)} in SKILL.md names no scenario (<!-- specs: NNN-NN -->)")
        for sid in named:
            if sid not in ids:
                problems.append(f"rule {m.group(1)} in SKILL.md names unknown scenario {sid}")
    return problems


def check_guards(root: Path, code_ids: set[str]) -> list[str]:
    reg = root / "tools" / "guards.yaml"
    if not reg.exists():
        return []
    problems = []
    for g in yaml.safe_load(reg.read_text(encoding="utf-8")) or []:
        named = [str(s) for s in (g.get("failure_scenarios") or [])]
        if not named:
            problems.append(f"guard '{g.get('name')}' has no failure scenario")
        for sid in named:
            if sid not in code_ids:
                problems.append(f"guard '{g.get('name')}' names {sid}, which is not a code scenario")
    return problems
