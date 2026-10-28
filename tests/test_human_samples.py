"""Steps for specs/027-human-samples.feature: scripts/samples.py and the meters' use of samples."""

import shutil
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import meters
import samples

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "meters"
scenarios("../specs/027-human-samples.feature")

HEADERS = {
    "kind written, source, date, human_only true": {"kind": "written", "source": "s", "date": "2020-01", "human_only": True},
    "kind written, source, date, human_only false": {"kind": "written", "source": "s", "date": "2020-01", "human_only": False},
    "kind written, date, human_only true, no source": {"kind": "written", "date": "2020-01", "human_only": True},
    "kind poem, source, date, human_only true": {"kind": "poem", "source": "s", "date": "2020-01", "human_only": True},
    "kind description, source, date, human_only true": {"kind": "description", "source": "s", "date": "2020-01",
                                                        "human_only": True},
}


@pytest.fixture
def ctx(tmp_path):
    (tmp_path / "profile" / "samples").mkdir(parents=True)
    return {"root": tmp_path}


def write_sample(root: Path, name: str, header: dict, body: str) -> None:
    import yaml
    text = "---\n" + yaml.safe_dump(header, sort_keys=False) + "---\n" + body + "\n"
    (root / "profile" / "samples" / name).write_text(text, encoding="utf-8")


@given(parsers.re(r"a sample whose header has (?P<header>.+)$"))
def sample_with_header(ctx, header):
    write_sample(ctx["root"], "s.md", HEADERS[header.strip()], "Some words I wrote myself.")


@when("I list the reference samples")
def list_samples(ctx):
    ctx["all"] = samples.load(ctx["root"])
    ctx["refs"] = samples.references(ctx["root"])


@then(parsers.re(r"the sample is (?P<result>.+)$"))
def sample_result(ctx, result):
    (s,) = ctx["all"]
    assert s.status() == result.strip(), s.status()
    assert (s in ctx["refs"]) == (result.strip() == "used")


@given("one written sample and one spoken sample")
def written_and_spoken(ctx):
    for name in ("sample-written-1.md", "sample-spoken.md"):
        shutil.copy(FIX / name, ctx["root"] / "profile" / "samples" / name)


@when("the meters measure sentence rhythm")
def measure_rhythm(ctx):
    ctx["rhythm"] = meters.rhythm_reference(ctx["root"])
    ctx["phrasing"] = meters.phrasing_reference(ctx["root"])


@then("only the written sample is used")
def only_written(ctx):
    assert len(ctx["rhythm"]) == 1 and "burnt coffee" in ctx["rhythm"][0]


@then("the spoken sample is used for phrasing only")
def spoken_for_phrasing(ctx):
    assert any("rock up on day one" in t for t in ctx["phrasing"])
    assert not any("rock up on day one" in t for t in ctx["rhythm"])


@given(parsers.parse('a fingerprint that lists "{sig}" as a signature phrase and "{out}" to leave out'))
def a_fingerprint(ctx, sig, out):
    (ctx["root"] / "profile/samples/fingerprint.md").write_text(
        f"---\nsignature_phrases: [{sig}]\nleave_out: [{out}]\n---\n# Fingerprint\n", encoding="utf-8")


@when("I read the fingerprint")
def read_fingerprint(ctx):
    ctx["fp"] = samples.fingerprint(ctx["root"])


@then(parsers.parse('"{phrase}" is a signature phrase'))
def is_signature(ctx, phrase):
    assert phrase in ctx["fp"]["signature"]


@then(parsers.parse('"{phrase}" is a phrase to leave out'))
def is_leave_out(ctx, phrase):
    assert phrase in ctx["fp"]["leave_out"]


@given("a profile with no samples")
def no_samples(ctx):
    ctx["draft"] = ctx["root"] / "articles" / "x" / "draft.md"
    ctx["draft"].parent.mkdir(parents=True)
    shutil.copy(FIX / "ai-draft.md", ctx["draft"])


@when("the meters run on a draft")
def meters_on_draft(ctx):
    ctx["results"] = {r["meter"]: r for r in meters.score(ctx["root"], ctx["draft"], env={})}


@then(parsers.parse('the "is it me?" meter is grey with the reason "{reason}"'))
def itm_grey(ctx, reason):
    r = ctx["results"]["is it me?"]
    assert (r["light"], r["reason"]) == ("grey", reason)


@then("every other meter still reports")
def others_report(ctx):
    assert {"overused words", "antithesis", "rhythm", "informality", "AI detector"} <= set(ctx["results"])
    assert ctx["results"]["overused words"]["light"] in ("amber", "red")


@given(parsers.parse('a written sample that holds "{a}", "{b}" and "{c}"'))
def sample_with_placeholders(ctx, a, b, c):
    ctx["marks"] = (a, b, c)
    write_sample(ctx["root"], "work.md", HEADERS["kind written, source, date, human_only true"],
                 f"Thanks {a} for the call, the deck is here {b} and I loved it {c}")


@when("the meters read the sample")
def meters_read_sample(ctx):
    (s,) = samples.references(ctx["root"])
    ctx["measured"] = samples.clean(s.text)


@then("the measured text contains none of them")
def none_of_them(ctx):
    assert not any(m in ctx["measured"] for m in ctx["marks"]), ctx["measured"]
    assert "Thanks" in ctx["measured"] and "loved it" in ctx["measured"]
