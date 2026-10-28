# status: in-progress (v1.4.0-rc1)
# approved: Dan 2026-10-28
Feature: Optional modules are off until the writer switches them on
  As a writer,
  I want every optional module off by default, and to know whether each one sends my text anywhere,
  so that nothing leaves my machine without my choice.

  Settings live in profile/settings.yaml. Keys live only in environment variables.
  The first module is the Pangram AI detector; style packs and image sources follow later.
  Detector scores are warnings, never gates.

  @code @id:028-01
  Scenario: A new profile has every optional module off and the meters on
    Given a new profile
    When I read its settings
    Then the meters are on
    And the Pangram module is off
    And the informality dial is "light"

  @code @id:028-02
  Scenario: The module list says which modules send text away
    Given the engine's modules
    When I list them with their status
    Then each module states whether the writer's text leaves the machine
    And Pangram states that it does

  @code @id:028-03
  Scenario Outline: Pangram runs only when it is on and its key is set
    Given the Pangram module is <setting> and the key is <key>
    When the scorecard runs on a published article
    Then Pangram is <outcome>

    Examples:
      | setting | key     | outcome                                                    |
      | off     | not set | not called, and the scorecard says "AI detector: off"        |
      | on      | not set | not called, and the scorecard warns "Pangram key not set"   |
      | on      | set     | called once                                                 |

  @code @id:028-04
  Scenario: If Pangram fails, the scorecard warns and carries on
    Given the Pangram module is on and the key is set
    And Pangram returns an error
    When the scorecard runs on a published article
    Then the scorecard warns that Pangram could not be reached
    And the scorecard finishes without an error

  @code @id:028-05
  Scenario: Unpublished text is never sent to Pangram
    Given the Pangram module is on and the key is set
    When the scorecard runs on an unpublished draft
    Then Pangram is not called
    And the scorecard says "AI detector: published text only"

  @code @id:028-06
  Scenario: A key written into the settings file is refused
    Given a settings file that holds a Pangram key
    When I check the profile
    Then the check fails with "keys belong in environment variables, not profile/settings.yaml"

  @code @id:028-07
  Scenario: The migration adds the settings and samples folder, and keeps what exists
    Given a profile from engine version "1.3.2"
    When the writer approves and the migrations run
    Then profile/settings.yaml exists with the defaults
    And profile/samples/ exists
    And no existing profile file has changed
