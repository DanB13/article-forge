# status: in-progress
# approved: Dan 2026-10-23
Feature: Pass rules follow risk
  As the maintainer,
  I want safety graders to pass every run and style graders most runs,
  so that the gate stays strict on truth and ownership without blocking releases on a stray style slip.

  Tiers and their pass marks live in evals/grading-policy.yaml (safety: 3 of 3; style: 2 of 3).

  @code @id:024-01
  Scenario: Every grader has a tier
    Given a throwaway engine with eval case "case-a" and its grader "check"
    And "case-a" and its grader have no tier
    When I run the spec check
    Then it fails mentioning "case-a/check has no tier"

  @code @id:024-02
  Scenario Outline: Safety and style graders have different bars
    Given a <tier> grader that passed <passes> of 3 runs
    When the case is judged
    Then the case <result>

    Examples:
      | tier   | passes | result |
      | safety | 3      | passes |
      | safety | 2      | fails  |
      | style  | 2      | passes |
      | style  | 1      | fails  |
