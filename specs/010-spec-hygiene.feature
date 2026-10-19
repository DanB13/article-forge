# status: shipped (v1.3.0)
Feature: Spec hygiene: every scenario is tested, stale ones are flagged for retirement
  As the maintainer of the engine,
  I want the spec checker to fail on untested or orphaned work and to list specs to retire,
  so that the requirements stay a true and current description of the engine.

  @code
  Scenario: A scenario with no test tag fails the check
    Given a spec "004-demo.feature" with a scenario tagged ""
    When I run the spec check
    Then it fails mentioning "needs exactly one of @code or @eval"

  @code
  Scenario: An eval case that no scenario uses fails as an orphan
    Given an eval case "old-case" that no scenario uses
    When I run the spec check
    Then it fails mentioning "'old-case' is not used by any scenario"

  @code
  Scenario: A superseded spec is listed as a retire candidate
    Given a spec "004-demo.feature" with a scenario tagged "@code"
    And a spec "005-newer.feature" that supersedes "004"
    When I run the spec check
    Then it warns "retire candidate: 004-demo.feature"
    And the strict check fails

  @code
  Scenario: A shipped eval scenario that was never verified is flagged
    Given a shipped spec "004-demo.feature" with an eval scenario verified on ""
    When I run the spec check on "2026-10-19"
    Then it warns "has never been verified"

  @code
  Scenario Outline: Eval verification goes stale after 90 days
    Given a shipped spec "004-demo.feature" with an eval scenario verified on "<verified>"
    When I run the spec check on "2026-10-19"
    Then the stale warning count is <warnings>

    Examples:
      | verified   | warnings |
      | 2026-10-01 | 0        |
      | 2026-07-01 | 1        |

  @code
  Scenario: Private specs and evals under local/ are checked too
    Given a private spec "L001-rory.feature" whose scenario uses the private eval case "rory-moves"
    When I run the spec check
    Then it passes
