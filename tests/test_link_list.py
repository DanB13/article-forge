"""Steps for specs/038-link-list.feature: scripts/check_links.py."""

import pytest
from pytest_bdd import given, scenarios, then, when

import check_links

scenarios("../specs/038-link-list.feature")

MAP = """## Link map
| Anchor phrase | URL |
|---|---|
| 46% of workers | https://example.org/survey-2025 |
| Gartner expects | https://example.org/gartner-forecast |
| real network telemetry | https://example.org/telemetry |
"""


@pytest.fixture
def ctx():
    return {}


@given("a link map with three links and a published list with two of them")
def two_of_three(ctx):
    ctx["map"] = MAP
    ctx["pub"] = "- [46% of workers](https://example.org/survey-2025)\n- [Gartner expects](https://example.org/gartner-forecast)\n"


@given("a link map and a published list where one anchor phrase points to a different URL")
def changed_url(ctx):
    ctx["map"] = MAP
    ctx["pub"] = ("- [46% of workers](https://example.org/survey-2025)\n"
                  "- [Gartner expects](https://example.org/gartner-newsroom)\n"
                  "- [real network telemetry](https://example.org/telemetry)\n")


@when("I compare the published links with the link map")
def compare(ctx):
    ctx["problems"] = check_links.compare(ctx["map"], ctx["pub"])


@then("the missing link is reported with its anchor phrase")
def missing_reported(ctx):
    assert ctx["problems"] == ['not published: "real network telemetry" (https://example.org/telemetry)']


@then("that anchor phrase is reported with both URLs")
def both_urls(ctx):
    (p,) = ctx["problems"]
    assert "gartner expects" in p and "gartner-forecast" in p and "gartner-newsroom" in p
