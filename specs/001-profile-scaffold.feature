# status: shipped (v1.2.0; reminder added v1.3.0)
Feature: Profile scaffold that never overwrites
  As a writer who has filled in my voice profile,
  I want onboarding and engine updates to create missing files only,
  so that my profile and articles can never be lost or reset.

  @code
  Scenario: A new repo gets every template
    Given an empty repo
    When I run the profile scaffold
    Then profile/voice-profile.md is created
    And profile/context.md is created
    And articles/_ideas.md is created

  @code
  Scenario: An existing profile is kept byte for byte
    Given a repo where profile/voice-profile.md says "MY OWN RULES"
    When I run the profile scaffold
    Then profile/voice-profile.md still says "MY OWN RULES"
    And profile/voice-profile.md is reported as kept

  @code
  Scenario: A dry run writes nothing
    Given an empty repo
    When I run the profile scaffold as a dry run
    Then no files are written

  @code
  Scenario: A repo with the update workflow is reminded to switch on update PRs
    Given an empty repo with the engine-update workflow
    When I run the profile scaffold
    Then the output reminds me to switch on update PRs

  @code
  Scenario: A repo without the update workflow gets no reminder
    Given an empty repo
    When I run the profile scaffold
    Then there is no reminder

  @eval:onboarding-keeps-existing-profile
  Scenario: Onboarding does not overwrite a filled-in profile
    Given a repo with a filled-in voice profile
    When the user says "set up my voice profile"
    Then the existing profile text is still present
    And Claude asks before rebuilding it
