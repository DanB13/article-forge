"""Steps for specs/016-release-channels.feature."""

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import engine_update

scenarios("../specs/016-release-channels.feature")


@pytest.fixture
def ch():
    return {}


@given(parsers.parse('upstream release tags "{tags}"'))
def tags(ch, tags):
    ch["tags"] = [t.strip() for t in tags.split(",")]


@when(parsers.parse('the update picks its target on the "{channel}" channel'))
def pick(ch, channel):
    ch["target"] = engine_update.pick_target(ch["tags"], channel)


@then(parsers.parse('the target is "{target}"'))
def target_is(ch, target):
    assert ch["target"] == target
