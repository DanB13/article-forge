# status: shipped (v1.3.0)
Feature: The voice edit enforces the profile's mechanics and never invents the writer
  As a writer with a defined voice,
  I want the voice edit to apply my mechanical rules and leave personal detail to me,
  so that the article sounds like me and nothing in it is made up about me.

  Phase 5.

  # last-verified: 2026-10-22
  @eval:voice-edit-mechanics
  Scenario: Approved mechanical fixes remove em dashes and banned words
    Given a draft with em dashes and banned words, and the user's advance approval of mechanical fixes
    When the voice edit runs
    Then the draft contains no em dash and no banned word

  # last-verified: 2026-10-22
  @eval:voice-edit-mechanics
  Scenario: "X, not Y" contrasts are cut to the profile limit
    Given a draft with six "X, not Y" contrasts and a profile limit of three
    When the voice edit runs
    Then at most three remain

  # last-verified: 2026-10-22
  @eval:voice-edit-mechanics
  Scenario: Personal details are asked for, never invented
    Given a draft with no personal anecdotes
    When the voice edit runs
    Then no invented first-person story appears in the draft
