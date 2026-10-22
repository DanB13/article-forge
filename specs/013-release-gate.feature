# status: in-progress
Feature: Nothing ships without a passing eval run
  As the maintainer,
  I want a release to need an eval summary made for exactly the engine being released,
  so that every release was tested, and tested as shipped.

  The summary lives in .claude/skills/article-forge/evals/summaries/v<version>.json
  and records a fingerprint of the engine files. tools/eval_summary.py makes and checks it.

  @code @id:013-01
  Scenario: A release with no eval summary is refused
    Given an engine at version "1.4.0" with eval cases "case-a, case-b"
    When I run the release gate
    Then it fails mentioning "no eval summary for v1.4.0"

  @code @id:013-02
  Scenario: A summary made for different engine content is refused
    Given an engine at version "1.4.0" with eval cases "case-a, case-b"
    And a passing eval summary for that engine
    And the engine changes after the summary is made
    When I run the release gate
    Then it fails mentioning "engine changed since the eval run"

  @code @id:013-03
  Scenario: A failed eval case blocks the release
    Given an engine at version "1.4.0" with eval cases "case-a, case-b"
    And an eval summary for that engine where "case-b" failed
    When I run the release gate
    Then it fails mentioning "case-b failed"

  @code @id:013-04
  Scenario: A passing summary for the released engine lets the release go ahead
    Given an engine at version "1.4.0" with eval cases "case-a, case-b"
    And a passing eval summary for that engine
    When I run the release gate
    Then it passes

  @code @id:013-05
  Scenario: A release candidate needs only the free tests
    Given an engine at version "1.4.0" with eval cases "case-a, case-b"
    When I run the release gate for the tag "v1.4.0-rc1"
    Then it passes
    And it says the eval gate applies to the final release
