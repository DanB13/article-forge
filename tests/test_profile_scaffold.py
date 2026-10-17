"""Steps for specs/001-profile-scaffold.feature."""

from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import scaffold_profile

scenarios("../specs/001-profile-scaffold.feature")


@pytest.fixture
def ctx(tmp_path):
    return {"root": tmp_path}


@given("an empty repo")
def empty_repo(ctx):
    assert not any(ctx["root"].iterdir())


@given(parsers.parse('a repo where {rel} says "{text}"'))
def repo_with_file(ctx, rel, text):
    p = ctx["root"] / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


@when("I run the profile scaffold")
def run_scaffold(ctx):
    ctx["out"] = scaffold_profile.scaffold(ctx["root"])


@when("I run the profile scaffold as a dry run")
def run_dry(ctx):
    ctx["out"] = scaffold_profile.scaffold(ctx["root"], dry_run=True)


@then(parsers.parse("{rel} is created"))
def is_created(ctx, rel):
    assert (ctx["root"] / rel).is_file()
    assert rel in ctx["out"]["created"]


@then(parsers.parse('{rel} still says "{text}"'))
def still_says(ctx, rel, text):
    assert (ctx["root"] / rel).read_text(encoding="utf-8") == text


@then(parsers.parse("{rel} is reported as kept"))
def reported_kept(ctx, rel):
    assert rel in ctx["out"]["kept"]
    assert rel not in ctx["out"]["created"]


@then("no files are written")
def nothing_written(ctx):
    assert not any(Path(ctx["root"]).rglob("*"))
    assert ctx["out"]["created"]  # the dry run still reports what it would create
