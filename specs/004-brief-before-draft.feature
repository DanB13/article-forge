# status: shipped (v1.3.0)
Feature: The brief comes first; then a full first draft without stopping
  As a writer handing the engine an idea,
  I want it to pin down the brief before it writes, and then write the whole first draft in one go,
  so that I edit a complete article aimed at the right reader, not a guess.

  Non-negotiable rule 1, plus decision 1 (19 Oct 2026): once the brief is locked,
  research and the complete first draft run without stopping. The one exception:
  research that contradicts the thesis is raised before drafting.

  # last-verified: 2026-10-22
  @eval:brief-ambiguous-asks
  Scenario: An ambiguous theme gets questions, not a draft
    Given a theme with no audience, outcome or argument
    When the user asks for an article
    Then the engine asks about at least two of audience, outcome, argument and positioning
    And no draft file is written

  # last-verified: 2026-10-22
  @eval:draft-from-locked-brief
  Scenario: A locked brief gets a complete first draft in one pass
    Given a locked brief and finished research
    When the user asks for the first draft
    Then a complete article is written: opening, at least three sections, closing question
    And the engine does not stop to re-ask what the brief already answers

  # last-verified: 2026-10-22
  @eval:draft-from-locked-brief
  Scenario: The first draft follows the profile's mechanics
    Given a voice profile that bans em dashes and listed words
    When the first draft is written
    Then it contains no em dash and no banned word
