# status: in-progress
# approved: Dan 2026-10-23
Feature: Graders are grounded in the spec
  As the maintainer,
  I want every grader tied to an approved scenario, exact checks by default, and no way to pass by doing nothing,
  so that the tests check the spec and not the model's own view of it.

  Each eval case has a grading.yaml naming, for every grader, the scenario it checks (checks:),
  its tier, a reason for any AI judge, and a did-the-work partner for any "must not" check.

  @code @id:021-01
  Scenario: Every grader names its scenario
    Given a throwaway engine with eval case "case-a" and its grader "check"
    And the grader "check" names no scenario
    When I run the spec check
    Then it fails mentioning "case-a/check names no scenario"

  @code @id:021-02
  Scenario: An AI judge must say why no exact check works
    Given a throwaway engine with eval case "case-a" and its grader "check"
    And an AI-judged grader "judge" with no reason
    When I run the spec check
    Then it fails mentioning "case-a/judge is an AI judge and needs a reason"

  @code @id:021-03
  Scenario: A "must not" check needs a did-the-work partner
    Given a throwaway engine with eval case "case-a" and its grader "check"
    And a "must not" grader "no-dash" with no partner
    When I run the spec check
    Then it fails mentioning "case-a/no-dash is a 'must not' check with no did-the-work partner"
