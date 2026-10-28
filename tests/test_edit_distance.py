"""Steps for specs/031-edit-distance.feature: scripts/edit_distance.py."""

import pytest
import yaml
from pytest_bdd import given, parsers, scenarios, then, when

import edit_distance

scenarios("../specs/031-edit-distance.feature")

BASE = [f"word{i}" for i in range(100)]


@pytest.fixture
def ctx(tmp_path):
    art = tmp_path / "articles" / "piece"
    art.mkdir(parents=True)
    return {"root": tmp_path, "art": art}


@given(parsers.re(r"a first draft and a published text that (?P<change>.+)$"))
def draft_and_published(ctx, change):
    first = list(BASE)
    if change == "are identical":
        pub = list(first)
    elif change == "differ in 10 of 100 words":
        pub = [w if i % 10 else f"changed{i}" for i, w in enumerate(first)]
    else:
        pub = [f"other{i}" for i in range(100)]
    (ctx["art"] / "draft-v1.md").write_text(" ".join(first), encoding="utf-8")
    (ctx["art"] / "published.md").write_text(" ".join(pub), encoding="utf-8")


@when("I measure the edit distance")
def measure(ctx):
    ctx["result"] = edit_distance.record(ctx["art"])


@then(parsers.re(r"it is (?P<distance>\d+%)$"))
def it_is(ctx, distance):
    assert ctx["result"]["percent"] == distance, ctx["result"]


@given("an article with a first draft and a published text")
def article(ctx):
    (ctx["art"] / "draft-v1.md").write_text("A short first draft about a quiet policy.", encoding="utf-8")
    (ctx["art"] / "published.md").write_text("A short published piece about a loud policy.", encoding="utf-8")


@then("articles/<slug>/metrics.yaml records the distance, the date and the engine version")
def metrics_recorded(ctx):
    import datetime as dt
    data = yaml.safe_load((ctx["art"] / "metrics.yaml").read_text(encoding="utf-8"))["edit_distance"]
    assert data["value"] > 0 and data["date"] == dt.date.today().isoformat()
    assert data["engine_version"] == (edit_distance.SKILL_DIR / "VERSION").read_text(encoding="utf-8").strip()


@given(parsers.parse("three articles with edit distances of {a:d}%, {b:d}% and {c:d}%"))
def three_articles(ctx, a, b, c):
    for i, v in enumerate((a, b, c)):
        d = ctx["root"] / "articles" / f"a{i}"
        d.mkdir(parents=True, exist_ok=True)
        (d / "metrics.yaml").write_text(yaml.safe_dump({"edit_distance": {"value": v / 100}}), encoding="utf-8")


@when("I compute the baseline")
def compute_baseline(ctx):
    ctx["baseline"] = edit_distance.baseline(ctx["root"])


@then(parsers.parse("the baseline is {pct:d}%"))
def baseline_is(ctx, pct):
    assert round(ctx["baseline"] * 100) == pct
