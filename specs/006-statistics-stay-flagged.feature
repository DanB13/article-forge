# status: shipped (v1.3.0)
Feature: No statistic is trusted until it is traced
  As a writer whose credibility rests on data,
  I want every statistic flagged until its origin is proven,
  so that laundered, derived or secondary-only numbers never reach readers as fact.

  Non-negotiable rule 3 and Phase 4. See also 002 (subcut statistics).

  # last-verified: 2026-10-22
  @eval:draft-from-locked-brief @id:006-01
  Scenario: Draft statistics carry the unverified marker
    Given research whose statistics are all unverified
    When the first draft is written
    Then every statistic in the draft is marked [UNVERIFIED]

  # last-verified: 2026-10-22
  @eval:provenance-secondary-only @id:006-02
  Scenario: A statistic seen only in secondary coverage is not verified
    Given a statistic whose only source is a blog that names no survey
    When Phase 4 runs
    Then its evidence record leaves it unverified, escalates it, or recommends cutting it

  # last-verified: 2026-10-22
  @eval:provenance-secondary-only @id:006-03
  Scenario: A derived number is labelled as derived
    Given a figure that a blogger calculated by multiplying two other numbers
    When Phase 4 runs
    Then its evidence record calls it derived and recommends dropping or labelling it
