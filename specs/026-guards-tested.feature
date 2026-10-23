# status: shipped (v1.3.2)
# approved: Dan 2026-10-23
Feature: The guards themselves are tested
  As the maintainer,
  I want every guard to have a scenario that proves it fails on bad input, and a review that looks for contradictions,
  so that no guard can stop working unnoticed and conflicts between instructions are caught before release.

  @code @id:026-01
  Scenario: Every guard in the registry has a failure scenario
    Given the engine repo
    When I read the guard registry
    Then every guard names at least one code scenario, and each exists

  @code @id:026-02
  Scenario: A guard without a failure scenario fails the check
    Given a throwaway engine with a guard registry entry that names no failure scenario
    When I run the spec check
    Then it fails mentioning "has no failure scenario"

  # last-verified: 2026-10-23
  @eval:consistency-review-finds-contradiction @id:026-03
  Scenario: The pre-release review finds a planted contradiction
    Given a copy of the skill where a reference file contradicts a rule in SKILL.md
    When the maintainer asks for a review before release
    Then the review names the contradiction and both files
