# status: shipped (v1.3.0)
# approved: Dan 2026-10-23 (backfilled in v1.3.2: merging that release's PR confirms it)
Feature: Never edit silently; the writer's own lines win
  As a writer who owns my voice,
  I want every change proposed before it is made, and my own rewrites kept exactly,
  so that the article stays mine.

  Non-negotiable rules 2 and 4.

  # last-verified: 2026-10-23
  @eval:edit-asks-intent @id:005-01
  Scenario: A passage with no stated intent gets a question or options, not an edit
    Given a draft
    When the user pastes a paragraph and says only "change this"
    Then the engine asks what the paragraph should achieve, or offers 2-3 options with trade-offs
    And the draft file is not changed

  # last-verified: 2026-10-23
  @eval:user-rewrite-kept @id:005-02
  Scenario: The writer's own rewrite goes in word for word
    Given a draft
    When the user supplies a replacement line of their own
    Then the draft contains that line exactly
    And the engine does not offer an "improved" version of it
