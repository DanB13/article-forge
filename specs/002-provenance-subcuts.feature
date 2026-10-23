# status: shipped (v1.2.0)
# approved: Dan 2026-10-23 (backfilled in v1.3.2: merging that release's PR confirms it)
Feature: Subcut statistics get their own provenance record
  As a writer whose credibility rests on data,
  I want every breakdown of a headline statistic traced on its own,
  so that a real number cannot smuggle in an unsupported one.

  Why: a real production cycle published "66% of office professionals use AI
  tools; at large companies it rises to 72%". The 66% was real. The source's
  only 72% measured a different question. Phase 4 must catch this pattern.
  The eval uses a synthetic survey so the fixture is stable and copyright-free.

  # last-verified: 2026-10-23
  @eval:provenance-subcut @id:002-01
  Scenario: A subcut that measures a different question is flagged
    Given a draft that says a survey found 61% overall, rising to 74% at large firms
    And the source survey reports 61% overall and 74% for a different question
    When Phase 4 runs on the draft
    Then evidence.md has a separate record for the 74% claim
    And that record says the source does not support it

  # last-verified: 2026-10-23
  @eval:provenance-subcut @id:002-02
  Scenario: The supported headline figure is not flagged
    Given the same draft and source
    When Phase 4 runs on the draft
    Then evidence.md marks the 61% figure as supported
