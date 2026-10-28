# status: in-progress (v1.4.0-rc1)
# approved: Dan 2026-10-28
Feature: Edit distance shows how much the writer had to change
  As a writer,
  I want each article to record how much I changed between the first draft and what I published,
  so that I can see whether the engine needs less of my time with each release.

  scripts/edit_distance.py compares articles/<slug>/draft-v1.md with the published text and
  writes articles/<slug>/metrics.yaml. The baseline is the median across recorded articles.

  @code @id:031-01
  Scenario Outline: Edit distance is the share of words changed
    Given a first draft and a published text that <change>
    When I measure the edit distance
    Then it is <distance>

    Examples:
      | change                      | distance        |
      | are identical               | 0%              |
      | differ in 10 of 100 words   | 10%             |
      | share no words              | 100%            |

  @code @id:031-02
  Scenario: The measure is recorded in the article's metrics file
    Given an article with a first draft and a published text
    When I measure the edit distance
    Then articles/<slug>/metrics.yaml records the distance, the date and the engine version

  @code @id:031-03
  Scenario: The baseline is the median of the recorded articles
    Given three articles with edit distances of 20%, 35% and 50%
    When I compute the baseline
    Then the baseline is 35%

  @eval:draft-keeps-v1 @id:031-04
  Scenario: The first complete draft is kept as draft-v1.md
    Given an article with a locked brief and research
    When Claude writes the first draft and the writer asks for a change
    Then the first draft is saved as draft-v1.md
    And the change goes into a later version, never into draft-v1.md

  @eval:retro-records-edit-distance @id:031-05
  Scenario: The retro records the edit distance
    Given an article with draft-v1.md and the published text pasted back
    When the retro runs
    Then Claude measures the edit distance and reports it next to the baseline
