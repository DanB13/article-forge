# status: in-progress
# approved: Dan 2026-10-23
Feature: Test changes are visible and approved
  As the maintainer,
  I want every change to a released test to need a written reason and my approval,
  so that a test cannot be weakened quietly, even when its ID and the test count stay the same.

  The ledger (specs/ledger.json) records a fingerprint of every scenario's wording, every grader,
  every eval case and fixture, every pytest step file and the pass rules. A change to a recorded
  item needs an entry in specs/test-changes.yaml: item, reason, approved_by, date.

  @code @id:020-01
  Scenario: Every test is fingerprinted at release
    Given a throwaway engine with eval case "case-a" and its grader "check"
    When I update the ledger for release "1.4.0"
    Then the ledger holds a fingerprint for the scenario, the grader, the eval case and the pass rules

  @code @id:020-02
  Scenario: A changed test needs a record
    Given a throwaway engine with eval case "case-a" and its grader "check"
    And the ledger was updated for release "1.4.0"
    And the grader "check" of "case-a" is changed
    When I run the spec check
    Then it fails mentioning "grader:case-a/check changed"

  @code @id:020-03
  Scenario: An approved change goes through
    Given a throwaway engine with eval case "case-a" and its grader "check"
    And the ledger was updated for release "1.4.0"
    And the grader "check" of "case-a" is changed
    And a test-change record for "grader:case-a/check" approved by "Dan"
    When I run the spec check
    Then it passes

  @code @id:020-04
  Scenario: Pass marks cannot drop quietly
    Given a throwaway engine with eval case "case-a" and its grader "check"
    And the ledger was updated for release "1.4.0"
    And the style tier is lowered to 1 passing run
    When I run the spec check
    Then it fails mentioning "policy changed"
