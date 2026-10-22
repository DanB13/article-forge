"""Steps for specs/013-release-gate.feature: tools/eval_summary.py on throwaway engines."""

import json
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import eval_summary

scenarios("../specs/013-release-gate.feature")


def make_engine(root: Path, version: str, cases: list[str]) -> Path:
    skill = root / eval_summary.SKILL
    (skill / "evals").mkdir(parents=True)
    (skill / "VERSION").write_text(version + "\n", encoding="utf-8")
    (skill / "SKILL.md").write_text("# Engine\n", encoding="utf-8")
    for case in cases:
        (skill / "evals" / case).mkdir()
        (skill / "evals" / case / "prompt.md").write_text("Do the thing.", encoding="utf-8")
    return skill


def eval_run(tmp: Path, results: dict[str, bool], name: str = "run.json") -> Path:
    """A minimal `claude plugin eval --json` result: 3 runs per case."""
    data = {"claudeVersion": "test", "suite": {"threshold": 1},
            "cases": [{"name": c, "arms": {"with": [{"passed": ok}] * 3}} for c, ok in results.items()]}
    p = tmp / name
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


@pytest.fixture
def gate(tmp_path):
    return {"root": tmp_path / "repo", "tmp": tmp_path}


@given(parsers.parse('an engine at version "{version}" with eval cases "{cases}"'))
def engine(gate, version, cases):
    gate["version"] = version
    gate["cases"] = [c.strip() for c in cases.split(",")]
    make_engine(gate["root"], version, gate["cases"])


@given("a passing eval summary for that engine")
def passing_summary(gate):
    eval_summary.make(gate["root"], gate["version"], [eval_run(gate["tmp"], {c: True for c in gate["cases"]})])


@given(parsers.parse('an eval summary for that engine where "{case}" failed'))
def failing_summary(gate, case):
    results = {c: c != case for c in gate["cases"]}
    eval_summary.make(gate["root"], gate["version"], [eval_run(gate["tmp"], results)])


@given("the engine changes after the summary is made")
def engine_changes(gate):
    (gate["root"] / eval_summary.SKILL / "SKILL.md").write_text("# Engine, edited after the run\n", encoding="utf-8")


@when("I run the release gate")
def run_gate(gate):
    gate["problems"], gate["notes"] = eval_summary.check(gate["root"], gate["version"])


@when(parsers.parse('I run the release gate for the tag "{tag}"'))
def run_gate_tag(gate, tag):
    gate["problems"], gate["notes"] = eval_summary.check(gate["root"], gate["version"], tag)


@then(parsers.parse('it fails mentioning "{text}"'))
def fails_with(gate, text):
    assert any(text in p for p in gate["problems"]), gate["problems"]


@then("it passes")
def passes(gate):
    assert gate["problems"] == [], gate["problems"]


@then("it says the eval gate applies to the final release")
def rc_note(gate):
    assert any("final release" in n for n in gate["notes"]), gate["notes"]
