"""Steps for specs/036-cover-render.feature: scripts/render_cover.py (no browser needed)."""

import base64

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import render_cover

scenarios("../specs/036-cover-render.feature")


@pytest.fixture
def ctx(tmp_path):
    return {"root": tmp_path}


@given(parsers.parse('a cover template with the placeholder "{token}" and a small photo'))
def template_and_photo(ctx, token):
    from PIL import Image
    photo = ctx["root"] / "photo.png"
    Image.new("RGB", (4, 4), (200, 30, 30)).save(photo)
    ctx["photo"], ctx["token"] = photo, token
    ctx["html"] = f'<html><body><img src="{token}"></body></html>'


@when(parsers.parse('I embed the photo for "{token}"'))
def embed(ctx, token):
    ctx["out"] = render_cover.embed_images(ctx["html"], [f"{ctx['photo']}={token}"])


@then("the template holds the photo as a data URI")
def data_uri(ctx):
    expected = base64.b64encode(ctx["photo"].read_bytes()).decode()
    assert f"data:image/png;base64,{expected}" in ctx["out"]


@then("the placeholder is gone")
def placeholder_gone(ctx):
    assert ctx["token"] not in ctx["out"]


@given(parsers.parse("a rendered image of {w:d} by {h:d} pixels"))
def rendered(ctx, w, h):
    from PIL import Image
    ctx["img"] = Image.new("RGB", (w, h), (10, 120, 60))


@when(parsers.parse("I fit it to {width:d} by {height:d}"))
def fit(ctx, width, height):
    ctx["fitted"] = render_cover.fit(ctx["img"], width, height)


@then(parsers.parse("the image is exactly {width:d} by {height:d} pixels"))
def exact(ctx, width, height):
    assert ctx["fitted"].size == (width, height)
