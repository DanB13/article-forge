# status: proposed (v1.4.0-rc1)
Feature: Rule-based meters give every draft a scorecard
  As a writer,
  I want a scorecard at the voice edit that shows, with a reason, where a draft reads as AI or not as me,
  so that I fix the right lines and can see the trend across articles.

  scripts/meters.py runs the meters and writes articles/<slug>/scorecard.md. Each meter
  shows a traffic light (green, amber, red, or grey when it cannot run) and a reason.
  The writer's allowed words (profile/settings.yaml) are never flagged.

  @code @id:029-01
  Scenario Outline: Overused AI words are flagged unless the writer allows them
    Given a draft that uses "<word>" twice
    And the writer allows "navigate, seamless, robust"
    When the meters run
    Then the overused-words meter <result>

    Examples:
      | word   | result                     |
      | delve  | flags "delve" (2)          |
      | robust | does not flag "robust"     |

  @code @id:029-02
  Scenario: Repeated "not X but Y" and "X, not Y" constructions are counted
    Given a draft with 5 "X, not Y" constructions
    When the meters run
    Then the antithesis meter is amber with the reason "5 found; 2 to 3 reads as rhetoric, more as a rhythm"

  @code @id:029-03
  Scenario: Sentences of near-identical length are flagged
    Given a draft where every sentence is 14 to 16 words long
    When the meters run
    Then the rhythm meter is amber or red with a reason that names the spread of sentence lengths

  @code @id:029-04
  Scenario: The "is it me?" meter compares the draft with the written samples
    Given two written samples
    When the meters run on a draft copied from one of the samples, and on a fictional AI draft
    Then the copied draft scores closer to the writer than the AI draft

  @code @id:029-05
  Scenario: The scorecard records every meter with a light and a reason
    Given a draft
    When the meters run
    Then articles/<slug>/scorecard.md lists every meter with a traffic light and a reason
    And it records the date and the draft it scored

  @code @id:029-06
  Scenario: A poor score never stops the work
    Given a draft that every meter rates red
    When the meters run
    Then they exit without an error

  @eval:voice-edit-shows-scorecard @id:029-07
  Scenario: The voice edit shows the scorecard and proposes fixes
    Given a draft with three overused AI words and five "X, not Y" constructions
    When the writer asks for the voice edit
    Then Claude shows the scorecard with its lights and reasons
    And it proposes a fix for each flagged line without applying any

  @eval:voice-edit-shows-scorecard @id:029-08
  Scenario: The voice edit checks the reader clues
    Given a draft with three overused AI words and five "X, not Y" constructions
    When the writer asks for the voice edit
    Then Claude reports the reader-clue checklist (vocabulary, sentence shape, generic examples)
