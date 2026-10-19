# status: shipped (v1.3.0)
Feature: The writer owns the profile; the retro only proposes
  As a writer whose voice profile is my property,
  I want the retro to propose changes for my approval and never apply them itself,
  so that the engine learns from me without rewriting me.

  Phase 8.

  @eval:retro-proposes-not-applies
  Scenario: The retro proposes profile changes and does not apply them
    Given a final draft and the published version
    When the retro runs
    Then proposed profile changes are listed for approval
    And the voice profile file is not edited

  @eval:retro-proposes-not-applies
  Scenario: The retro writes its record and archives the published piece
    Given a final draft and the published version
    When the retro runs
    Then a retro file is written for the article
    And the published piece is saved to the corpus
