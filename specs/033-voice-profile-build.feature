# status: in-progress (v1.4.0-rc1)
# approved: Dan 2026-10-28
Feature: Onboarding builds the voice profile from the writer's own work
  As a new writer,
  I want my profile drawn from what I have written and shown to me before it is saved,
  so that the engine starts from my voice, not a generic one.

  Describes references/00-onboarding.md as it works today.

  @eval:onboarding-proposes-first @id:033-01
  Scenario: The extracted profile is a proposal until the writer approves it
    Given a new writer who has pasted two published pieces
    When onboarding analyses them
    Then Claude shows the extracted voice profile as a proposal
    And it writes nothing to profile/voice-profile.md before the writer approves

  @eval:onboarding-proposes-first @id:033-02
  Scenario: Every voice rule cites the writing it came from
    Given a new writer who has pasted two published pieces
    When onboarding analyses them
    Then each proposed voice rule quotes or points to the line it came from
