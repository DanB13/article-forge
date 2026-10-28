"""Bind every behaviour-only spec so a Gherkin syntax error fails CI.

Their scenarios are all @eval: conftest.py reports them as skipped here, and
`claude plugin eval` runs them. A new eval-only feature file goes in this list.
"""

from pytest_bdd import scenarios

for _feature in (
    "002-provenance-subcuts.feature",
    "004-brief-before-draft.feature",
    "005-never-edit-silently.feature",
    "006-statistics-stay-flagged.feature",
    "007-voice-edit-mechanics.feature",
    "008-profile-ownership.feature",
    "009-imagery-real-first.feature",
    "011-accuracy-and-rounds.feature",
    "033-voice-profile-build.feature",
    "034-research.feature",
    "035-edition-anchors.feature",
    "037-publish-pack.feature",
):
    scenarios(f"../specs/{_feature}")
