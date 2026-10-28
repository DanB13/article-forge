"""Steps for specs/028-optional-modules.feature: scripts/settings.py and the AI detector in scripts/meters.py."""

import shutil
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import check_profile
import meters
import migrate
import scaffold_profile
import settings

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures"
scenarios("../specs/028-optional-modules.feature")


@pytest.fixture
def ctx(tmp_path):
    return {"root": tmp_path, "env": {}, "calls": []}


def set_settings(root: Path, pangram: str) -> None:
    p = root / settings.SETTINGS
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"informality: light\nmodules:\n  meters: on\n  pangram: {pangram}\n", encoding="utf-8")


@given("a new profile")
def new_profile(ctx):
    scaffold_profile.scaffold(ctx["root"])


@when("I read its settings")
def read_settings(ctx):
    assert (ctx["root"] / settings.SETTINGS).exists()
    ctx["s"] = settings.load(ctx["root"])


@then("the meters are on")
def meters_on(ctx):
    assert ctx["s"]["modules"]["meters"] is True


@then("the Pangram module is off")
def pangram_off(ctx):
    assert ctx["s"]["modules"]["pangram"] is False


@then(parsers.parse('the informality dial is "{dial}"'))
def dial_is(ctx, dial):
    assert ctx["s"]["informality"] == dial


@given("the engine's modules")
def engine_modules(ctx):
    ctx["modules"] = settings.MODULES


@when("I list them with their status")
def list_status(ctx):
    ctx["rows"] = settings.module_status(ctx["root"], env={})


@then("each module states whether the writer's text leaves the machine")
def states_leaves(ctx):
    assert ctx["rows"] and all(isinstance(r["leaves_machine"], bool) for r in ctx["rows"])


@then("Pangram states that it does")
def pangram_leaves(ctx):
    assert next(r for r in ctx["rows"] if r["module"] == "pangram")["leaves_machine"] is True


def fake_pangram(ctx, fail=False):
    def transport(method, url, body, headers):
        ctx["calls"].append((method, url))
        if fail:
            raise OSError("network down")
        if method == "POST":
            return {"task_id": "t1"}
        return {"stage": "STAGE_SUCCESS", "fraction_ai": 0.1, "fraction_ai_assisted": 0.2}
    return transport


@given(parsers.re(r"the Pangram module is (?P<setting>on|off) and the key is (?P<key>set|not set)$"))
def pangram_setting(ctx, setting, key):
    set_settings(ctx["root"], setting)
    ctx["env"] = {"PANGRAM_API_KEY": "test-key-not-real"} if key == "set" else {}
    ctx["transport"] = fake_pangram(ctx)


@given("Pangram returns an error")
def pangram_errors(ctx):
    ctx["transport"] = fake_pangram(ctx, fail=True)


def _run(ctx, rel):
    p = ctx["root"] / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIX / "meters" / "sample-written-1.md", p)
    ctx["results"] = {r["meter"]: r for r in meters.score(ctx["root"], p, env=ctx["env"],
                                                          transport=ctx["transport"], poll_seconds=0)}
    ctx["det"] = ctx["results"]["AI detector"]


@when("the scorecard runs on a published article")
def run_published(ctx):
    _run(ctx, "articles/piece/published.md")


@when("the scorecard runs on an unpublished draft")
def run_unpublished(ctx):
    _run(ctx, "articles/piece/draft.md")


@then(parsers.re(r"Pangram is (?P<outcome>.+)$"))
def pangram_outcome(ctx, outcome):
    outcome = outcome.strip()
    if outcome == "called once":
        assert [m for m, _ in ctx["calls"]].count("POST") == 1
        assert ctx["det"]["reason"].startswith("Pangram AI share")
        return
    assert ctx["calls"] == []
    if outcome != "not called":
        expected = outcome.split('"')[1]
        assert expected in ctx["det"]["reason"], ctx["det"]["reason"]


@then("the scorecard warns that Pangram could not be reached")
def warns_unreachable(ctx):
    assert "could not be reached" in ctx["det"]["reason"]


@then("the scorecard finishes without an error")
def finishes(ctx):
    assert len(ctx["results"]) == 6


@then(parsers.parse('the scorecard says "{text}"'))
def scorecard_says(ctx, text):
    assert ctx["det"]["reason"] == text


@given("a settings file that holds a Pangram key")
def settings_with_key(ctx):
    shutil.copytree(FIX / "profiles" / "v1.3.0" / "profile", ctx["root"] / "profile")
    (ctx["root"] / settings.SETTINGS).write_text(
        "modules:\n  pangram: on\npangram_api_key: pg_" + "a1B2c3D4" * 4 + "\n", encoding="utf-8")


@when("I check the profile")
def check(ctx):
    ctx["problems"] = check_profile.problems(ctx["root"])


@then(parsers.parse('the check fails with "{text}"'))
def check_fails(ctx, text):
    assert any(text in p for p in ctx["problems"]), ctx["problems"]


@given(parsers.parse('a profile from engine version "{version}"'))
def profile_from(ctx, version):
    shutil.copytree(FIX / "profiles" / f"v{version}" / "profile", ctx["root"] / "profile")
    ctx["before"] = {p.relative_to(ctx["root"]).as_posix(): p.read_bytes()
                     for p in (ctx["root"] / "profile").rglob("*") if p.is_file()}


@when("the writer approves and the migrations run")
def migrations_run(ctx):
    migrate.apply(ctx["root"], migrate.discover(ctx["root"]), yes=True)


@then("profile/settings.yaml exists with the defaults")
def settings_defaults(ctx):
    s = settings.load(ctx["root"])
    assert (ctx["root"] / settings.SETTINGS).exists()
    assert s["modules"] == {"meters": True, "pangram": False} and s["informality"] == "light"


@then("profile/samples/ exists")
def samples_exists(ctx):
    assert (ctx["root"] / "profile" / "samples" / "README.md").exists()


@then("no existing profile file has changed")
def unchanged(ctx):
    for rel, data in ctx["before"].items():
        assert (ctx["root"] / rel).read_bytes() == data, rel
