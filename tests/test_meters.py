"""Steps for specs/029-meters-and-scorecard.feature and 030-informality-dial.feature: scripts/meters.py."""

import shutil
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import meters

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "meters"
scenarios("../specs/029-meters-and-scorecard.feature")
scenarios("../specs/030-informality-dial.feature")

FILLER = ["We met on Tuesday.", "The plan changed twice before lunch, which surprised nobody in the room.",
          "Fine.", "I wrote the first version on a train with a cold coffee and a phone at four percent.",
          "Then we shipped it.", "Nobody read the release notes, of course, but the support queue went quiet."]


@pytest.fixture
def ctx(tmp_path):
    (tmp_path / "articles" / "piece").mkdir(parents=True)
    return {"root": tmp_path, "settings": {}}


def write_settings(ctx, **kw):
    lines = [f"informality: {kw.get('informality', 'light')}"]
    if "allowed" in kw:
        lines.append("allowed_words: [" + ", ".join(kw["allowed"]) + "]")
    p = ctx["root"] / "profile" / "settings.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_draft(ctx, text, name="draft.md"):
    p = ctx["root"] / "articles" / "piece" / name
    p.write_text(text, encoding="utf-8")
    ctx["draft"] = p
    return p


def run(ctx):
    ctx["results"] = {r["meter"]: r for r in meters.score(ctx["root"], ctx["draft"], env={})}


@given(parsers.parse('a draft that uses "{word}" twice'))
def draft_with_word(ctx, word):
    write_draft(ctx, " ".join(FILLER) + f" We {word} the details. Then we {word} them again.")


@given(parsers.parse('the writer allows "{words}"'))
def writer_allows(ctx, words):
    write_settings(ctx, allowed=[w.strip() for w in words.split(",")])


@when("the meters run")
def meters_run(ctx):
    run(ctx)


@then(parsers.re(r"the overused-words meter (?P<result>.+)$"))
def overused_result(ctx, result):
    r = ctx["results"]["overused words"]
    if result.startswith("does not flag"):
        word = result.split('"')[1]
        assert not any(word in f for f in r["flags"]), r
    else:
        assert result.removeprefix("flags ") in r["reason"], r


@given(parsers.parse('a draft with {n:d} "X, not Y" constructions'))
def draft_antithesis(ctx, n):
    lines = [f"We chose the {w} plan, not the expensive one." for w in ("first", "quiet", "slow", "small", "odd", "late")][:n]
    write_draft(ctx, " ".join(FILLER) + " " + " ".join(lines))


@then(parsers.parse('the antithesis meter is amber with the reason "{reason}"'))
def antithesis_amber(ctx, reason):
    r = ctx["results"]["antithesis"]
    assert (r["light"], r["reason"]) == ("amber", reason), r


@given("a draft where every sentence is 14 to 16 words long")
def uniform_draft(ctx):
    s = ["The team reviewed the policy and agreed that the new controls were clearly needed now.",
         "Every department will receive training on the approved tools before the end of March.",
         "The security group will monitor usage and report any unusual activity to the board quarterly.",
         "Managers should remind their staff that personal accounts must never hold company data at all."]
    write_draft(ctx, " ".join(s * 2))


@then("the rhythm meter is amber or red with a reason that names the spread of sentence lengths")
def rhythm_flagged(ctx):
    r = ctx["results"]["rhythm"]
    assert r["light"] in ("amber", "red") and "spread" in r["reason"] and "words" in r["reason"], r


@given("two written samples")
def two_samples(ctx):
    d = ctx["root"] / "profile" / "samples"
    d.mkdir(parents=True, exist_ok=True)
    for name in ("sample-written-1.md", "sample-written-2.md"):
        shutil.copy(FIX / name, d / name)


@when("the meters run on a draft copied from one of the samples, and on a fictional AI draft")
def run_two_drafts(ctx):
    copied = (FIX / "sample-written-2.md").read_text(encoding="utf-8").split("---\n", 2)[2]
    write_draft(ctx, copied, "copied.md")
    run(ctx)
    ctx["copied"] = ctx["results"]["is it me?"]
    shutil.copy(FIX / "ai-draft.md", ctx["root"] / "articles" / "piece" / "ai.md")
    ctx["draft"] = ctx["root"] / "articles" / "piece" / "ai.md"
    run(ctx)
    ctx["ai"] = ctx["results"]["is it me?"]


@then("the copied draft scores closer to the writer than the AI draft")
def copied_closer(ctx):
    assert ctx["copied"]["value"] < ctx["ai"]["value"], (ctx["copied"], ctx["ai"])
    assert ctx["ai"]["light"] in ("amber", "red")


@given("a draft")
def a_draft(ctx):
    shutil.copy(FIX / "ai-draft.md", ctx["root"] / "articles" / "piece" / "draft.md")
    ctx["draft"] = ctx["root"] / "articles" / "piece" / "draft.md"


@then("articles/<slug>/scorecard.md lists every meter with a traffic light and a reason")
def scorecard_file(ctx):
    meters.main([str(ctx["draft"]), "--root", str(ctx["root"])])
    text = (ctx["root"] / "articles" / "piece" / "scorecard.md").read_text(encoding="utf-8")
    ctx["scorecard"] = text
    for name, r in ctx["results"].items():
        assert f"| {name} | {r['light']} | {r['reason']} |" in text


@then("it records the date and the draft it scored")
def records_date(ctx):
    import datetime as dt
    assert dt.date.today().isoformat() in ctx["scorecard"] and "articles/piece/draft.md" in ctx["scorecard"]


@given("a draft that every meter rates red")
def all_red(ctx):
    shutil.copy(FIX / "ai-draft.md", ctx["root"] / "articles" / "piece" / "draft.md")
    ctx["draft"] = ctx["root"] / "articles" / "piece" / "draft.md"


@then("they exit without an error")
def exit_zero(ctx):
    assert meters.main([str(ctx["draft"]), "--root", str(ctx["root"])]) == 0
    assert ctx["results"]["overused words"]["light"] == "red"


@given(parsers.parse('the informality dial is "{dial}"'))
def dial(ctx, dial):
    write_settings(ctx, informality=dial)
    fp = ctx["root"] / "profile" / "samples" / "fingerprint.md"
    fp.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(FIX / "fingerprint.md", fp)


@given(parsers.parse("a draft that uses {n:d} of the writer's signature phrases"))
def signature_draft(ctx, n):
    phrases = ["We would have a crack at it.", "Fair play to the team.", "I rock up early.", "They got stuck in."][:n]
    write_draft(ctx, " ".join(FILLER) + " " + " ".join(phrases))


@then(parsers.re(r"the informality meter is (?P<light>.+)$"))
def informality_light(ctx, light):
    r = ctx["results"]["informality"]
    if light == "green":
        assert r["light"] == "green", r
    else:
        reason = light.split('"')[1]
        assert r["light"] == "amber" and reason in r["reason"], r
