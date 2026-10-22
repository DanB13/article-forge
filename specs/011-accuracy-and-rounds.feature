# status: shipped (v1.3.0)
Feature: Facts about the writer stay true; fact and style edits stay apart
  As a writer whose name is on the article,
  I want facts about my own past kept exactly as I gave them, and factual fixes kept apart from style changes,
  so that nothing about me is exaggerated and each kind of change can be checked on its own.

  Non-negotiable rules 5 and 7.

  # last-verified: 2026-10-22
  @eval:confirm-lived-facts
  Scenario: The writer's role is not made bigger than the anchor says
    Given a brief anchor saying the writer "helped" and was "one of three"
    When the user asks for a confession opening built from it
    Then the engine asks for the missing detail before offering openings
    And no opening it shows claims more than the anchor says

  # last-verified: 2026-10-22
  @eval:edit-rounds-separate
  Scenario: A fact fix and a style rewrite are handled as separate rounds
    Given a draft
    When the user asks in one message for a fact correction and a punchier style
    Then the fact is corrected
    And the style change is proposed or scheduled as its own round
