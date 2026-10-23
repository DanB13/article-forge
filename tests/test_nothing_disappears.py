"""Steps for specs/018-nothing-disappears.feature: IDs, the ledger, the release run and the test audit."""

import json
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import check_specs
import eval_summary
import scenario_audit

ROOT = Path(__file__).resolve().parents[1]
scenarios("../specs/018-nothing-disappears.feature")


@pytest.fixture
def repo(tmp_path):
    for d in ("specs", "tests"):
        (tmp_path / d).mkdir()
    return {"root": tmp_path}


def feature(root: Path, name: str, scenarios_text: str) -> None:
    (root / "specs" / name).write_text(f"# status: shipped\n# approved: Test 2026-10-23\nFeature: Demo\n\n{scenarios_text}\n", encoding="utf-8")
    (root / "tests" / f"test_{Path(name).stem}.py").write_text(f'scenarios("../specs/{name}")\n', encoding="utf-8")


def scenario(tags: str, title: str) -> str:
    return f"  {tags}\n  Scenario: {title}\n    Given x\n"


@given(parsers.parse('a spec "{name}" with a scenario that has no ID'))
def no_id(repo, name):
    feature(repo["root"], name, scenario("@code", "Something happens"))


@given(parsers.parse('a spec "{name}" with two scenarios that both have "{tag}"'))
def dup_ids(repo, name, tag):
    feature(repo["root"], name, scenario(f"@code {tag}", "First") + scenario(f"@code {tag}", "Second"))


@given(parsers.parse('a ledger from release "{version}" that lists scenario "{sid}"'))
def ledger(repo, version, sid):
    data = {"released": version, "scenarios": {sid: {"title": "Old behaviour", "spec": "004-demo.feature",
                                                     "status": "active", "since": version}}}
    (repo["root"] / "specs" / "ledger.json").write_text(json.dumps(data), encoding="utf-8")


@given(parsers.parse('no spec contains scenario "{sid}"'))
def spec_without(repo, sid):
    feature(repo["root"], "005-other.feature", scenario("@code @id:005-01", "Unrelated"))


@given(parsers.parse('a spec contains scenario "{sid}"'))
def spec_with(repo, sid):
    feature(repo["root"], "004-demo.feature", scenario(f"@code @id:{sid}", "Old behaviour"))


@given(parsers.parse('a retire record for "{sid}" approved by "{who}"'))
def retire(repo, sid, who):
    (repo["root"] / "specs" / "retired.yaml").write_text(
        f'- id: "{sid}"\n  reason: "Replaced by 005-01"\n  approved_by: "{who}"\n  date: "2026-10-22"\n',
        encoding="utf-8")


@when("I run the spec check")
def spec_check(repo):
    repo["problems"] = check_specs.check(repo["root"]).fails


@when(parsers.parse('I run the release check for "{version}"'))
def release_check(repo, version):
    repo["problems"] = check_specs.check(repo["root"]).fails + check_specs.release_check(repo["root"], version)


# 018-05: the release run covers every case from the last release.

def _write_summary(skill: Path, version: str, cases: list[str]) -> None:
    d = eval_summary.summaries_dir(skill)
    d.mkdir(parents=True, exist_ok=True)
    data = {"version": version, "engine_fingerprint": eval_summary.fingerprint(skill),
            "cases": {c: {"passed": True, "runs": 3, "passes": 3} for c in cases}}
    (d / f"v{version}.json").write_text(json.dumps(data), encoding="utf-8")


@given(parsers.parse('the last release\'s eval summary covers "{cases}"'))
def last_summary(repo, cases):
    skill = repo["root"] / eval_summary.SKILL
    (skill / "evals" / "case-a").mkdir(parents=True)
    (skill / "evals" / "case-a" / "prompt.md").write_text("Do it.", encoding="utf-8")
    (skill / "VERSION").write_text("1.4.0\n", encoding="utf-8")
    _write_summary(skill, "1.3.0", [c.strip() for c in cases.split(",")])
    repo["skill"] = skill


@given(parsers.parse('this release\'s eval summary covers only "{case}"'))
def this_summary(repo, case):
    _write_summary(repo["skill"], "1.4.0", [case])


@when("I run the release gate")
def release_gate(repo):
    repo["problems"], _ = eval_summary.check(repo["root"], "1.4.0")


# 018-06 and 018-07: the test-run audit, against the real specs.

@pytest.fixture
def audit_ctx():
    expected = scenario_audit.expected_scenarios(check_specs.check(ROOT).ids)
    code = {k for k, v in expected.items() if v["kind"] == "code"}
    return {"expected": expected, "collected": set(code), "skipped": {}}


def _key(audit_ctx, title):
    return next(k for k in audit_ctx["expected"] if k[1] == title)


@given(parsers.parse('a code scenario "{title}" that was skipped'))
def skipped(audit_ctx, title):
    audit_ctx["skipped"][_key(audit_ctx, title)] = "zip is not installed"


@given(parsers.parse('a code scenario "{title}" that no test collected'))
def not_collected(audit_ctx, title):
    audit_ctx["collected"].discard(_key(audit_ctx, title))


@when("I audit the test run")
def run_audit(audit_ctx, repo):
    repo["problems"] = scenario_audit.audit(audit_ctx["expected"], audit_ctx["collected"], audit_ctx["skipped"],
                                            full_run=True, engine_repo=True)


@then(parsers.parse('it fails mentioning "{text}"'))
def fails_with(repo, text):
    assert any(text in p for p in repo["problems"]), repo["problems"]


@then(parsers.parse('the audit fails mentioning "{text}"'))
def audit_fails(repo, text):
    fails_with(repo, text)


@then("it passes")
def passes(repo):
    assert repo["problems"] == [], repo["problems"]
