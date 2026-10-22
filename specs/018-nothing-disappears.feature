# status: in-progress
Feature: Nothing disappears silently
  As the maintainer,
  I want every scenario, test and eval case tracked by identity against the last release,
  so that losing one fails loudly, even when the total number of tests goes up.

  @code @id:018-01
  Scenario: Every scenario needs an ID
    Given a spec "004-demo.feature" with a scenario that has no ID
    When I run the spec check
    Then it fails mentioning "has no @id"

  @code @id:018-02
  Scenario: Two scenarios cannot share an ID
    Given a spec "004-demo.feature" with two scenarios that both have "@id:004-01"
    When I run the spec check
    Then it fails mentioning "duplicate @id:004-01"

  @code @id:018-03
  Scenario: A released scenario cannot disappear without a retire record
    Given a ledger from release "1.3.0" that lists scenario "004-01"
    And no spec contains scenario "004-01"
    When I run the spec check
    Then it fails mentioning "004-01 disappeared"

  @code @id:018-04
  Scenario: A retire record with a reason and an approver allows a removal
    Given a ledger from release "1.3.0" that lists scenario "004-01"
    And no spec contains scenario "004-01"
    And a retire record for "004-01" approved by "Dan"
    When I run the spec check
    Then it passes

  @code @id:018-05
  Scenario: A release's eval run covers every case from the last release
    Given the last release's eval summary covers "case-a, case-b"
    And this release's eval summary covers only "case-a"
    When I run the release gate
    Then it fails mentioning "case-b was not run"

  @code @id:018-06
  Scenario: Only eval scenarios may be skipped
    Given a code scenario "Version numbers agree" that was skipped
    When I audit the test run
    Then the audit fails mentioning "Version numbers agree"

  @code @id:018-07
  Scenario: Every code scenario must be collected
    Given a code scenario "Version numbers agree" that no test collected
    When I audit the test run
    Then the audit fails mentioning "never ran"

  @code @id:018-08
  Scenario: A release needs the ledger updated to its version
    Given a ledger from release "1.3.0" that lists scenario "004-01"
    And a spec contains scenario "004-01"
    When I run the release check for "1.3.1"
    Then it fails mentioning "ledger.json is at 1.3.0"
