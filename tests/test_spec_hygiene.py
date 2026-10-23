"""Steps for specs/010-spec-hygiene.feature: check_specs.py on throwaway repos."""

import datetime as dt
import sys
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import check_specs  # noqa: E402

scenarios("../specs/010-spec-hygiene.feature")

EVALS = Path(".claude/skills/article-forge/evals")


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "specs").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / EVALS).mkdir(parents=True)
    return {"root": tmp_path, "today": None}


def _case(root: Path, base: Path, name: str) -> None:
    d = root / base / name
    d.mkdir(parents=True)
    (d / "prompt.md").write_text("Do the thing.", encoding="utf-8")


def _feature(root: Path, folder: str, name: str, body: str, status: str = "shipped") -> None:
    p = root / folder / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"# status: {status}\n# approved: Test 2026-10-23\nFeature: Demo\n\n{body}\n", encoding="utf-8")


def _id(name: str) -> str:
    return f"@id:{name.split('-', 1)[0]}-01"


def _code_test(root: Path, rel: str) -> None:
    (root / "tests" / f"test_{Path(rel).stem}.py").write_text(f'scenarios("../{rel}")\n', encoding="utf-8")


@given(parsers.re(r'a spec "(?P<name>[^"]+)" with a scenario tagged "(?P<tag>[^"]*)"'))
def spec_with_tag(repo, name, tag):
    _feature(repo["root"], "specs", name, f"  {tag} {_id(name)}\n  Scenario: Something happens\n    Given x")
    if tag == "@code":
        _code_test(repo["root"], f"specs/{name}")


@given(parsers.parse('an eval case "{case}" that no scenario uses'))
def orphan_case(repo, case):
    _case(repo["root"], EVALS, case)


@given(parsers.parse('a spec "{name}" that supersedes "{old}"'))
def superseding_spec(repo, name, old):
    _feature(repo["root"], "specs", name,
             f"# supersedes: {old}\n  @code {_id(name)}\n  Scenario: Newer behaviour\n    Given y")
    _code_test(repo["root"], f"specs/{name}")


@given(parsers.re(r'a shipped spec "(?P<name>[^"]+)" with an eval scenario verified on "(?P<date>[^"]*)"'))
def shipped_eval(repo, name, date):
    verified = f"  # last-verified: {date}\n" if date else ""
    _feature(repo["root"], "specs", name, f"{verified}  @eval:demo-case {_id(name)}\n  Scenario: Claude does it\n    Given z")
    _case(repo["root"], EVALS, "demo-case")


@given(parsers.parse('a private spec "{name}" whose scenario uses the private eval case "{case}"'))
def private_spec(repo, name, case):
    _feature(repo["root"], "local/specs", name, f"  @eval:{case} {_id(name)}\n  Scenario: Pack moves applied\n    Given w",
             status="in-progress")
    _case(repo["root"], Path("local/evals"), case)


@when("I run the spec check")
def run_check(repo):
    repo["report"] = check_specs.check(repo["root"], repo["today"])


@when(parsers.parse('I run the spec check on "{day}"'))
def run_check_on(repo, day):
    repo["today"] = dt.date.fromisoformat(day)
    repo["report"] = check_specs.check(repo["root"], repo["today"])


@then(parsers.parse('it fails mentioning "{text}"'))
def fails_with(repo, text):
    assert any(text in f for f in repo["report"].fails), repo["report"].fails


@then(parsers.parse('it warns "{text}"'))
def warns_with(repo, text):
    assert any(text in w for w in repo["report"].warns), repo["report"].warns


@then("the strict check fails")
def strict_fails(repo):
    assert check_specs.main(["--root", str(repo["root"]), "--strict"]) == 1


@then(parsers.parse("the stale warning count is {count:d}"))
def stale_count(repo, count):
    assert sum("days ago" in w for w in repo["report"].warns) == count


@then("it passes")
def passes(repo):
    assert repo["report"].fails == []


ENGINE_EVALS = Path(__file__).resolve().parents[1] / EVALS


@given("the engine's eval cases")
def engine_cases(repo):
    repo["files"] = [f for f in ENGINE_EVALS.rglob("*")
                     if f.name == "case.yaml" or (f.suffix == ".md" and (f.parent.name == "graders" or f.name == "prompt.md"))]
    assert repo["files"]


@when("I parse each case.yaml and the frontmatter of each prompt and grader")
def parse_all(repo):
    import yaml
    repo["errors"] = []
    for f in repo["files"]:
        text = f.read_text(encoding="utf-8")
        doc = text if f.name == "case.yaml" else (text.split("---", 2)[1] if text.startswith("---") else "")
        try:
            yaml.safe_load(doc)
        except yaml.YAMLError as e:
            repo["errors"].append(f"{f.relative_to(ENGINE_EVALS)}: {e}")


@then("every file parses as YAML")
def all_parse(repo):
    assert repo["errors"] == []
