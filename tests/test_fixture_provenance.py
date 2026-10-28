"""Steps for specs/032-fixture-provenance.feature: tools/fixture_provenance.py."""

from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

import fixture_provenance

ROOT = Path(__file__).resolve().parents[1]
scenarios("../specs/032-fixture-provenance.feature")


@pytest.fixture
def ctx():
    return {}


@given("the engine repo")
def engine_repo(ctx):
    ctx["root"] = ROOT


@given("an eval fixture with no provenance mark")
def unmarked(ctx, tmp_path):
    case = tmp_path / fixture_provenance.EVALS / "some-case" / "resources"
    case.mkdir(parents=True)
    (case / "notes.md").write_text("Some text of unknown origin.\n", encoding="utf-8")
    (tmp_path / "specs").mkdir()
    (tmp_path / fixture_provenance.REGISTRY).write_text("[]\n", encoding="utf-8")
    ctx["root"] = tmp_path


@when("I check the eval fixtures and test texts")
def check(ctx):
    ctx["problems"] = fixture_provenance.check(ctx["root"])
    ctx["dirs"] = fixture_provenance.fixture_dirs(ctx["root"])


@then('each one is marked "fictional" or "public" with a source and a licence')
def all_marked(ctx):
    assert ctx["dirs"] and ctx["problems"] == []


@then("the check fails and names the fixture")
def fails(ctx):
    assert len(ctx["problems"]) == 1 and "some-case/resources" in ctx["problems"][0]
