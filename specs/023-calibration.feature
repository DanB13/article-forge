# status: shipped (v1.3.2)
# approved: Dan 2026-10-23
Feature: The maintainer's labels calibrate the AI judges
  As the maintainer,
  I want a short file of AI-judged verdicts to label myself, with agreement measured per judge,
  so that my judgement, not another model's, is the ground truth for the judges.

  @code @id:023-01
  Scenario: A labelling file is exported from an eval run
    Given an eval run with 3 AI-judged verdicts from 2 judges
    When I export a calibration sample of 2
    Then the file holds 2 items, each with the rubric, the judged text, the judge's verdict and an empty label

  @code @id:023-02
  Scenario: A judge I disagree with twice is flagged
    Given calibration labels where I disagree with judge "case-a/judge" twice
    When I score the labels
    Then "case-a/judge" is flagged

  @code @id:023-03
  Scenario Outline: The release needs complete labels and no flagged judge
    Given a passing eval summary for an engine with grading, where the mutant of "case-a" was killed
    And calibration labels that are <state>
    When I run the release gate
    Then the gate <result>

    Examples:
      | state             | result                                  |
      | missing           | fails mentioning "no calibration labels" |
      | not all labelled  | fails mentioning "is not labelled"      |
      | flagging a judge  | fails mentioning "is flagged"           |
      | complete and agreeing | passes                              |
