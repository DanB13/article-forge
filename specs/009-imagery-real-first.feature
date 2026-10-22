# status: shipped (v1.3.0)
Feature: Real imagery comes first
  As a writer who wants authentic visuals,
  I want the engine to start from my own screenshots, photos and charts,
  so that generated imagery is a fallback, not the default.

  Non-negotiable rule 6 and Phase 6. See also 003 (imagery sources and CSS).

  # last-verified: 2026-10-22
  @eval:imagery-real-first
  Scenario: A cover request starts from real material
    Given a near-final draft
    When the user asks for a cover image
    Then the engine asks for or proposes real material first
    And generated imagery is offered only as a fallback
