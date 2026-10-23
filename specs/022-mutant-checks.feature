# status: in-progress
# approved: Dan 2026-10-23
Feature: Every eval case can fail
  As the maintainer,
  I want each eval case run once with the engine text it depends on removed, and to fail,
  so that a test that passes whatever the engine says cannot count as proof.

  tools/mutant_check.py runs the mutants; tools/eval_summary.py records and gates them.
  A case whose mutant survives needs an approved record in specs/guard-cases.yaml.

  @code @id:022-01
  Scenario Outline: Each case names its mutant
    Given a throwaway engine with eval case "case-a" and its grader "check"
    And the mutant of "case-a" is <mutant>
    When I run the spec check
    Then it fails mentioning "<message>"

    Examples:
      | mutant                         | message                                  |
      | missing                        | case-a names no mutant                   |
      | text that is not in the engine | case-a mutant text not found exactly once |

  @code @id:022-02
  Scenario Outline: A mutant that survives blocks the release unless it is an approved guard
    Given a passing eval summary for an engine with grading, where the mutant of "case-a" <outcome>
    And "case-a" <guard> recorded as an approved guard
    When I run the release gate
    Then the gate <result>

    Examples:
      | outcome  | guard  | result                                |
      | survived | is not | fails mentioning "case-a's mutant survived" |
      | survived | is     | passes                                |
      | was killed | is not | passes                              |

  @code @id:022-03
  Scenario: The mutant run removes the engine text and records the result
    Given a throwaway engine with eval case "case-a" and its grader "check"
    When the mutant check runs "case-a" with a runner that fails whenever the mutant text is gone
    Then the runner saw the engine without the mutant text
    And the result records the mutant of "case-a" as killed
