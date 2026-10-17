"""Steps for specs/003-imagery-sources.feature."""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import render_cover

scenarios("../specs/003-imagery-sources.feature")


@pytest.fixture
def ctx(tmp_path):
    return {"root": tmp_path}


@given(parsers.parse('a cover template "{rel}"'))
def cover_template(ctx, rel):
    p = ctx["root"] / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("<html><body><table><tr><td>Title</td></tr></table></body></html>", encoding="utf-8")
    ctx["html"] = p


@when(parsers.parse('I keep the source for output "{rel}"'))
def keep(ctx, rel):
    out = ctx["root"] / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    ctx["kept"] = render_cover.keep_source(ctx["html"], out)


@then(parsers.parse('"{rel}" exists'))
def exists(ctx, rel):
    assert (ctx["root"] / rel).is_file()
    assert ctx["kept"] == ctx["root"] / rel


@then("no copy is made")
def no_copy(ctx):
    assert ctx["kept"] is None


@given(parsers.parse('HTML containing "{css}"'))
def html_with(ctx, css):
    ctx["html_text"] = f"<style>.box {{ {css}; }}</style><div class='box'></div>"


@when("I lint the HTML")
def lint(ctx):
    ctx["warnings"] = render_cover.lint_html(ctx["html_text"])


@then(parsers.parse("there are {count:d} warnings"))
def warning_count(ctx, count):
    assert len(ctx["warnings"]) == count
