# status: in-progress
Feature: A set-up check finds missing GitHub settings
  As a writer setting up my repo,
  I want one command that tells me whether engine updates can reach me,
  so that a missing setting is found in seconds, not after weeks without updates.

  The check is scripts/check_setup.py in the skill. It uses the GitHub CLI (gh).

  @code @id:017-01
  Scenario: The check reports both settings when they are on
    Given GitHub reports update PRs switched on and the ENGINE_UPDATE_TOKEN secret present
    When I run the set-up check
    Then it reports update PRs as on
    And it reports the token as present

  @code @id:017-02
  Scenario: The check finds missing settings and says how to fix them
    Given GitHub reports update PRs switched off and no ENGINE_UPDATE_TOKEN secret
    When I run the set-up check
    Then it reports update PRs as off, with the steps to fix it
    And it reports the token as missing, with the steps to fix it

  @code @id:017-03
  Scenario: Without a signed-in GitHub CLI the check explains how to look by hand
    Given the GitHub CLI is not signed in
    When I run the set-up check
    Then it explains how to check both settings by hand
    And it exits without an error
