# status: in-progress (v1.4.0-rc1)
# approved: Dan 2026-10-28
Feature: An informality dial controls how much of the writer's spoken voice drafts carry
  As a writer whose spoken voice is warmer than my articles,
  I want drafts to use a few of my signature phrases, and never my spoken habits,
  so that articles feel friendlier without losing their professional register.

  The dial is in profile/settings.yaml: off, light (the default) or warm.
  Signature phrases per article: off 0, light at most 3, warm at most 6.

  @code @id:030-01
  Scenario Outline: The meter flags signature phrases above the dial's cap
    Given the informality dial is "<dial>"
    And a draft that uses 4 of the writer's signature phrases
    When the meters run
    Then the informality meter is <light>

    Examples:
      | dial  | light                                       |
      | off   | amber with the reason "4 used; the cap is 0" |
      | light | amber with the reason "4 used; the cap is 3" |
      | warm  | green                                       |

  @eval:informality-light @id:030-02
  Scenario: At "light", a draft uses at most 3 signature phrases
    Given a fictional writer's fingerprint and the informality dial at "light"
    When Claude writes the first draft from a locked brief
    Then the draft uses between 1 and 3 of the writer's signature phrases

  @eval:informality-light @id:030-03
  Scenario: A draft never uses the phrases to leave out
    Given a fictional writer's fingerprint and the informality dial at "light"
    When Claude writes the first draft from a locked brief
    Then the draft uses none of the phrases to leave out
