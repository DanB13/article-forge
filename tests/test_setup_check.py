"""Steps for specs/017-setup-check.feature: check_setup.py with a stand-in GitHub CLI."""

import json

import pytest
from pytest_bdd import given, scenarios, then, when

import check_setup

scenarios("../specs/017-setup-check.feature")


def fake_gh(signed_in=True, prs_on=True, token=True):
    def run(cmd):
        joined = " ".join(cmd)
        if joined.startswith("gh auth status"):
            return (0 if signed_in else 1), ""
        if joined.startswith("gh repo view"):
            return 0, "DanB13/article-forge-private\n"
        if "actions/permissions/workflow" in joined:
            return 0, json.dumps({"default_workflow_permissions": "read", "can_approve_pull_request_reviews": prs_on})
        if "actions/secrets" in joined:
            return 0, "ENGINE_UPDATE_TOKEN\n" if token else "OTHER_SECRET\n"
        if "actions/variables/ENGINE_CHANNEL" in joined:
            return 1, ""
        raise AssertionError(f"unexpected command: {joined}")
    return run


@pytest.fixture
def setup():
    return {}


@given("GitHub reports update PRs switched on and the ENGINE_UPDATE_TOKEN secret present")
def all_on(setup):
    setup["run"] = fake_gh()


@given("GitHub reports update PRs switched off and no ENGINE_UPDATE_TOKEN secret")
def all_off(setup):
    setup["run"] = fake_gh(prs_on=False, token=False)


@given("the GitHub CLI is not signed in")
def signed_out(setup):
    setup["run"] = fake_gh(signed_in=False)


@when("I run the set-up check")
def run_check(setup):
    lines, setup["ok"] = check_setup.check(setup["run"])
    setup["text"] = "\n".join(lines)


@then("it reports update PRs as on")
def prs_on(setup):
    assert "OK Update PRs: on" in setup["text"]


@then("it reports the token as present")
def token_present(setup):
    assert "OK Token: ENGINE_UPDATE_TOKEN present" in setup["text"]


@then("it reports update PRs as off, with the steps to fix it")
def prs_off(setup):
    assert "MISSING Update PRs: off" in setup["text"]
    assert "Allow GitHub Actions to create and approve pull requests" in setup["text"]
    assert setup["ok"] is False


@then("it reports the token as optional, with the steps to add it")
def token_optional(setup):
    assert "OPTIONAL Token" in setup["text"] and "Fine-grained tokens" in setup["text"]
    assert "issue with the commands" in setup["text"]


@then("it explains how to check both settings by hand")
def by_hand(setup):
    assert "by hand" in setup["text"] and "ENGINE_UPDATE_TOKEN" in setup["text"]
    assert "Allow GitHub Actions to create and approve pull requests" in setup["text"]


@then("it exits without an error")
def no_error(setup):
    assert setup["ok"] is True
