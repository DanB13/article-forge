# status: shipped (v1.3.0)
# approved: Dan 2026-10-23 (backfilled in v1.3.2: merging that release's PR confirms it)
Feature: The writer owns the profile; the retro only proposes
  As a writer whose voice profile is my property,
  I want the retro to propose changes for my approval and never apply them itself,
  so that the engine learns from me without rewriting me.

  Phase 8.

  # last-verified: 2026-10-23
  @eval:retro-proposes-not-applies @id:008-01
  Scenario: The retro proposes profile changes and does not apply them
    Given a final draft and the published version
    When the retro runs
    Then proposed profile changes are listed for approval
    And the voice profile file is not edited

  # last-verified: 2026-10-23
  @eval:retro-proposes-not-applies @id:008-02
  Scenario: The retro writes its record now and asks before archiving
    Given a final draft and the published version
    When the retro runs
    Then a retro file is written for the article with each proposal marked pending
    And the published piece is not saved to the corpus until the writer says yes
