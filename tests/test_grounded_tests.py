"""Steps for specs 020 to 026: test-change control, grounded graders, mutants, calibration,
pass rules, rule tracing and the guard registry, on throwaway engines."""

import json
from pathlib import Path

import pytest
import yaml
from pytest_bdd import given, parsers, scenarios, then, when

import calibrate
import check_specs
import eval_summary
import integrity
import mutant_check

ROOT = Path(__file__).resolve().parents[1]
scenarios("../specs/020-test-changes.feature")
scenarios("../specs/021-grounded-graders.feature")
scenarios("../specs/022-mutant-checks.feature")
scenarios("../specs/023-calibration.feature")
scenarios("../specs/024-pass-rules.feature")
scenarios("../specs/025-rules-traced.feature")
scenarios("../specs/026-guards-tested.feature")

RULE = "1. **Do it.** Always do the thing."
POLICY = "runs_per_case: 3\ntiers:\n  safety: 3\n  style: 2\n"


@pytest.fixture
def ctx(tmp_path):
    return {"root": tmp_path / "repo", "tmp": tmp_path}


def skill(ctx) -> Path:
    return ctx["root"] / integrity.SKILL


def grading(ctx, case="case-a") -> Path:
    return skill(ctx) / "evals" / case / "grading.yaml"


def edit_grading(ctx, fn, case="case-a"):
    meta = yaml.safe_load(grading(ctx, case).read_text(encoding="utf-8"))
    fn(meta)
    grading(ctx, case).write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")


def build_engine(ctx):
    root = ctx["root"]
    (root / "specs").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "specs" / "004-demo.feature").write_text(
        "# status: shipped\n# approved: Test 2026-10-23\nFeature: Demo\n\n"
        "  @eval:case-a @id:004-01\n  Scenario: Claude does it\n    Given z\n", encoding="utf-8")
    sk = skill(ctx)
    (sk / "evals" / "case-a" / "graders").mkdir(parents=True)
    (sk / "VERSION").write_text("1.4.0\n", encoding="utf-8")
    (sk / "SKILL.md").write_text(f"# Engine\n\n## Non-negotiable rules\n\n{RULE} <!-- specs: 004-01 -->\n\n## More\n",
                                 encoding="utf-8")
    (sk / "evals" / "grading-policy.yaml").write_text(POLICY, encoding="utf-8")
    (sk / "evals" / "case-a" / "prompt.md").write_text("Do the thing.", encoding="utf-8")
    (sk / "evals" / "case-a" / "graders" / "check.md").write_text("---\ntype: regex\npattern: \"done\"\n---\n",
                                                                  encoding="utf-8")
    grading(ctx).write_text(yaml.safe_dump({"tier": "style", "mutant": [{"file": "SKILL.md", "text": RULE}],
                                            "graders": {"check": {"checks": "004-01"}}}, sort_keys=False),
                            encoding="utf-8")


def add_grader(ctx, name, frontmatter: str, entry: dict):
    (skill(ctx) / "evals" / "case-a" / "graders" / f"{name}.md").write_text(f"---\n{frontmatter}---\nRubric.\n",
                                                                           encoding="utf-8")
    edit_grading(ctx, lambda m: m["graders"].__setitem__(name, entry))


# ---- building blocks -------------------------------------------------------

@given(parsers.parse('a throwaway engine with eval case "{case}" and its grader "{grader}"'))
def engine(ctx, case, grader):
    build_engine(ctx)


@given(parsers.parse('the ledger was updated for release "{version}"'))
def ledger_updated(ctx, version):
    assert check_specs.update_ledger(ctx["root"], version) == []


@when(parsers.parse('I update the ledger for release "{version}"'))
def update_ledger(ctx, version):
    assert check_specs.update_ledger(ctx["root"], version) == []
    ctx["ledger"] = json.loads((ctx["root"] / "specs" / "ledger.json").read_text(encoding="utf-8"))


@when("I run the spec check")
def spec_check(ctx):
    ctx["problems"] = check_specs.check(ctx["root"]).fails


@then(parsers.re(r'it fails mentioning "(?P<text>.+)"'))
def fails_with(ctx, text):
    assert any(text in p for p in ctx["problems"]), ctx["problems"]


@then("it passes")
def passes(ctx):
    assert ctx["problems"] == [], ctx["problems"]


# ---- 020 test-change control ------------------------------------------------

@then("the ledger holds a fingerprint for the scenario, the grader, the eval case and the pass rules")
def has_fingerprints(ctx):
    keys = set(ctx["ledger"]["fingerprints"])
    assert {"scenario:004-01", "grader:case-a/check", "case:case-a", "policy"} <= keys, keys


@given(parsers.parse('the grader "{grader}" of "{case}" is changed'))
def change_grader(ctx, grader, case):
    (skill(ctx) / "evals" / case / "graders" / f"{grader}.md").write_text(
        "---\ntype: regex\npattern: \"done|almost\"\n---\n", encoding="utf-8")


@given(parsers.parse('a test-change record for "{item}" approved by "{who}"'))
def change_record(ctx, item, who):
    (ctx["root"] / "specs" / "test-changes.yaml").write_text(
        f'- item: "{item}"\n  reason: "Accept the second spelling"\n  approved_by: "{who}"\n  date: "2026-10-23"\n',
        encoding="utf-8")


@given("the style tier is lowered to 1 passing run")
def lower_policy(ctx):
    (skill(ctx) / "evals" / "grading-policy.yaml").write_text(POLICY.replace("style: 2", "style: 1"), encoding="utf-8")


# ---- 021 grounded graders --------------------------------------------------

@given(parsers.parse('the grader "{grader}" names no scenario'))
def no_scenario(ctx, grader):
    edit_grading(ctx, lambda m: m["graders"].__setitem__(grader, {}))


@given(parsers.parse('an AI-judged grader "{name}" with no reason'))
def judge_without_reason(ctx, name):
    add_grader(ctx, name, "type: llm\nfocus: last_message\n", {"checks": "004-01"})


@given(parsers.parse('a "must not" grader "{name}" with no partner'))
def must_not_without_partner(ctx, name):
    add_grader(ctx, name, "type: regex\npattern: \"x\"\nmatch: not_contains\n", {"checks": "004-01"})


# ---- 022 mutants -----------------------------------------------------------

@given(parsers.parse('the mutant of "{case}" is {mutant}'))
def set_mutant(ctx, case, mutant):
    value = [] if mutant == "missing" else [{"file": "SKILL.md", "text": "Text that is nowhere in the engine."}]
    edit_grading(ctx, lambda m: m.__setitem__("mutant", value), case)


def eval_run(ctx, graders_passed: dict[str, list[bool]], name="run.json") -> Path:
    n = len(next(iter(graders_passed.values())))
    runs = [{"passed": all(v[i] for v in graders_passed.values()),
             "graders": [{"name": g, "passed": v[i]} for g, v in graders_passed.items()]} for i in range(n)]
    p = ctx["tmp"] / name
    p.write_text(json.dumps({"claudeVersion": "test", "cases": [{"name": "case-a", "arms": {"with": runs}}]}),
                 encoding="utf-8")
    return p


def write_labels(ctx, items, labelled_by="Dan"):
    d = skill(ctx) / "evals" / "calibration"
    d.mkdir(parents=True, exist_ok=True)
    (d / "v1.4.0.yaml").write_text(yaml.safe_dump({"version": "1.4.0", "labelled_by": labelled_by, "items": items}),
                                   encoding="utf-8")


def agreeing_items():
    return [{"id": 1, "case": "case-a", "grader": "judge", "judge": "pass", "label": "pass"}]


@given(parsers.re(r'a passing eval summary for an engine with grading, where the mutant of "case-a" (?P<outcome>survived|was killed)'))
def summary_with_mutant(ctx, outcome):
    build_engine(ctx)
    mutants = ctx["tmp"] / "mutants.json"
    mutants.write_text(json.dumps({"engine_fingerprint": eval_summary.fingerprint(skill(ctx)),
                                   "cases": {"case-a": {"killed": outcome == "was killed", "runs": 1}}}),
                       encoding="utf-8")
    write_labels(ctx, agreeing_items())
    eval_summary.make(ctx["root"], "1.4.0", [eval_run(ctx, {"check": [True, True, True]})], mutants)


@given(parsers.re(r'"case-a" (?P<guard>is|is not) recorded as an approved guard'))
def guard_record(ctx, guard):
    if guard == "is":
        (ctx["root"] / "specs" / "guard-cases.yaml").write_text(
            '- case: "case-a"\n  reason: "Tests the model\'s baseline"\n  approved_by: "Dan"\n  date: "2026-10-23"\n',
            encoding="utf-8")


@when("I run the release gate")
def release_gate(ctx):
    ctx["problems"], _ = eval_summary.check(ctx["root"], "1.4.0")


@then(parsers.re(r'the gate (?P<result>.+)'))
def gate_result(ctx, result):
    if result == "passes":
        assert ctx["problems"] == [], ctx["problems"]
    else:
        text = result.removeprefix("fails mentioning ").strip('"')
        assert any(text in p for p in ctx["problems"]), ctx["problems"]


@when(parsers.parse('the mutant check runs "{case}" with a runner that fails whenever the mutant text is gone'))
def run_mutant(ctx, case):
    seen = {}

    def runner(mutant_skill: Path, name: str, work: Path) -> Path:
        text = (mutant_skill / "SKILL.md").read_text(encoding="utf-8")
        seen["had_rule"] = RULE in text
        out = work / "out.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({"costUsd": 0.1, "cases": [{"name": name, "arms": {"with": [
            {"passed": RULE in text}]}}]}), encoding="utf-8")
        return out

    ctx["seen"] = seen
    ctx["mutants"] = mutant_check.run(ctx["root"], [case], runner=runner, jobs=1)


@then("the runner saw the engine without the mutant text")
def saw_mutant(ctx):
    assert ctx["seen"]["had_rule"] is False
    assert RULE in (skill(ctx) / "SKILL.md").read_text(encoding="utf-8")  # the real engine is untouched


@then(parsers.parse('the result records the mutant of "{case}" as killed'))
def killed(ctx, case):
    assert ctx["mutants"]["cases"][case]["killed"] is True
    assert ctx["mutants"]["engine_fingerprint"] == eval_summary.fingerprint(skill(ctx))


# ---- 023 calibration -------------------------------------------------------

@given("an eval run with 3 AI-judged verdicts from 2 judges")
def judged_run(ctx):
    def g(name, passed):
        return {"name": name, "passed": passed, "judgeVotes": [passed] * 3, "evidence": f"Reply judged by {name}."}
    run = {"cases": [{"name": "case-a",
                      "graders": [{"name": "j1", "graderMarkdown": "PASS if it asks."},
                                  {"name": "j2", "graderMarkdown": "PASS if it waits."}],
                      "arms": {"with": [{"graders": [g("j1", True), g("j2", False)]},
                                        {"graders": [g("j1", True)]}]}}]}
    ctx["run"] = ctx["tmp"] / "judged.json"
    ctx["run"].write_text(json.dumps(run), encoding="utf-8")


@when(parsers.parse("I export a calibration sample of {n:d}"))
def export_sample(ctx, n):
    ctx["doc"] = calibrate.export(ctx["run"], "1.4.0", ctx["tmp"] / "labels.yaml", n)


@then(parsers.parse("the file holds {n:d} items, each with the rubric, the judged text, the judge's verdict and an empty label"))
def sample_shape(ctx, n):
    items = yaml.safe_load((ctx["tmp"] / "labels.yaml").read_text(encoding="utf-8"))["items"]
    assert len(items) == n
    for it in items:
        assert it["rubric"].startswith("PASS if") and it["judged_text"] and it["judge"] in ("pass", "fail")
        assert it["label"] == ""
    assert {it["grader"] for it in items} == {"j1", "j2"}  # every judge is covered


@given(parsers.parse('calibration labels where I disagree with judge "{judge}" twice'))
def disagreeing_labels(ctx, judge):
    case, grader = judge.split("/")
    ctx["labels"] = ctx["tmp"] / "labels.yaml"
    ctx["labels"].write_text(yaml.safe_dump({"labelled_by": "Dan", "items": [
        {"id": i, "case": case, "grader": grader, "judge": "pass", "label": "fail"} for i in (1, 2)]}),
        encoding="utf-8")


@when("I score the labels")
def score_labels(ctx):
    ctx["score"] = calibrate.score(ctx["labels"])


@then(parsers.parse('"{judge}" is flagged'))
def flagged(ctx, judge):
    assert judge in ctx["score"]["flagged"]


@given(parsers.parse("calibration labels that are {state}"))
def labels_state(ctx, state):
    path = skill(ctx) / "evals" / "calibration" / "v1.4.0.yaml"
    if state == "missing":
        path.unlink()
    elif state == "not all labelled":
        write_labels(ctx, agreeing_items() + [{"id": 2, "case": "case-a", "grader": "judge", "judge": "fail", "label": ""}])
    elif state == "flagging a judge":
        write_labels(ctx, [{"id": i, "case": "case-a", "grader": "judge", "judge": "pass", "label": "fail"} for i in (1, 2)])
    else:
        write_labels(ctx, agreeing_items())


# ---- 024 pass rules --------------------------------------------------------

@given(parsers.parse('"{case}" and its grader have no tier'))
def no_tier(ctx, case):
    edit_grading(ctx, lambda m: m.pop("tier", None), case)


@given(parsers.parse("a {tier} grader that passed {passes:d} of 3 runs"))
def tiered_grader(ctx, tier, passes):
    ctx["judge_args"] = ([{"graders": [{"name": "g", "passed": i < passes}]} for i in range(3)],
                         yaml.safe_load(POLICY), {"tier": tier, "graders": {"g": {}}})


@when("the case is judged")
def judge(ctx):
    ctx["judged"] = eval_summary.judge_case(*ctx["judge_args"])


@then(parsers.re(r"the case (?P<result>passes|fails)"))
def case_result(ctx, result):
    assert ctx["judged"]["passed"] is (result == "passes"), ctx["judged"]


# ---- 025 rules and approvals -----------------------------------------------

@given(parsers.parse("a throwaway engine whose SKILL.md rule 1 names {named}"))
def rule_names(ctx, named):
    build_engine(ctx)
    p = skill(ctx) / "SKILL.md"
    comment = "" if named == "no scenario" else f" <!-- specs: {named.removeprefix('the scenario ')} -->"
    p.write_text(p.read_text(encoding="utf-8").replace(" <!-- specs: 004-01 -->", comment), encoding="utf-8")


@given(parsers.parse('a spec "{name}" with no approval record'))
def no_approval(ctx, name):
    build_engine(ctx)
    p = ctx["root"] / "specs" / name
    p.write_text(p.read_text(encoding="utf-8").replace("# approved: Test 2026-10-23\n", ""), encoding="utf-8")


@given("the engine-idea issue template")
def issue_template(ctx):
    ctx["template"] = yaml.safe_load((ROOT / ".github/ISSUE_TEMPLATE/engine-idea.yml").read_text(encoding="utf-8"))


@then("it asks for a story and for scenarios, and both are required")
def template_fields(ctx):
    fields = {b.get("id"): b for b in ctx["template"]["body"]}
    for f in ("story", "scenarios"):
        assert fields[f]["validations"]["required"] is True


# ---- 026 guards ------------------------------------------------------------

@given("the engine repo")
def engine_repo(ctx):
    ctx["root"] = ROOT


@when("I read the guard registry")
def read_registry(ctx):
    ctx["registry"] = yaml.safe_load((ROOT / "tools" / "guards.yaml").read_text(encoding="utf-8"))
    report = check_specs.check(ROOT)
    ctx["code_ids"] = {s for s, v in report.ids.items() if v.get("kind") == "code"}


@then("every guard names at least one code scenario, and each exists")
def registry_ok(ctx):
    assert len(ctx["registry"]) >= 10
    assert integrity.check_guards(ROOT, ctx["code_ids"]) == []


@given("a throwaway engine with a guard registry entry that names no failure scenario")
def bad_registry(ctx):
    build_engine(ctx)
    (ctx["root"] / "tools").mkdir()
    (ctx["root"] / "tools" / "guards.yaml").write_text("- name: demo guard\n  failure_scenarios: []\n", encoding="utf-8")
