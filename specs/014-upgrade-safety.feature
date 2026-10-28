# status: shipped (v1.3.1; 014-06 and 014-07 in v1.3.2; 014-08 and 014-09 in progress for v1.4.0-rc1)
# approved: Dan 2026-10-22; 014-06 and 014-07 approved by Dan 2026-10-23; 014-08 and 014-09 approved by Dan 2026-10-28
Feature: Engine updates cannot touch the writer's own folders
  As a writer whose profile and articles live in my own repo,
  I want every engine update to leave profile/ and articles/ exactly as they were,
  so that taking an update is never a risk to my work.

  The update logic lives in tools/engine_update.py; the engine-update workflow calls it.

  @code @upstream @id:014-01
  Scenario: The engine repo never contains a writer's folders
    Given the engine repo
    When I list the files the engine repo tracks
    Then none is under profile/ or articles/

  @code @id:014-02
  Scenario: An upgrade leaves the writer's folders byte for byte
    Given a writer's repo made from engine release "v1.0.0", with a filled-in profile and an article
    And newer engine releases "v1.1.0" and "v1.2.0"
    When the engine update runs after each release, and the writer merges each update
    Then the writer's profile/ and articles/ are byte-identical to before
    And the engine files match release "v1.2.0"

  @code @id:014-03
  Scenario: An update that would change the writer's folders is refused
    Given a writer's repo made from engine release "v1.0.0", with a filled-in profile and an article
    And a newer engine release "v1.1.0" that adds "profile/voice-profile.md"
    When the engine update runs
    Then no update branch is pushed
    And it reports "profile/voice-profile.md" as a refused file

  @code @id:014-04
  Scenario: The token only pushes; the workflow's own access opens the pull request
    Given the engine-update workflow
    Then the step that opens the pull request uses the workflow's own token
    And only the checkout uses the ENGINE_UPDATE_TOKEN secret

  @code @id:014-05
  Scenario: A half-finished update gets its pull request
    Given a writer's repo made from engine release "v1.0.0", with a filled-in profile and an article
    And a newer engine release "v1.1.0"
    And the update branch for "v1.1.0" was pushed but no pull request is open
    When the engine update runs
    Then it asks for a pull request for that branch
    And it pushes nothing new

  @code @id:014-06
  Scenario: The update opens its pull request through GitHub's REST API
    Given the engine-update workflow
    Then the step that opens the pull request calls the REST pulls endpoint, not gh pr create
    And it uses the workflow's own token

  @code @id:014-07
  Scenario: If the pull request cannot be opened, an issue gives a one-click link and the run fails
    Given the engine-update workflow
    Then a step runs only when opening the pull request failed
    And that step opens an issue whose body links to the compare page for the update branch
    And that step makes the run fail

  @code @id:014-08
  Scenario: Without the token, an update that changes workflow files pushes nothing and says so
    Given a writer's repo made from engine release "v1.0.0", with a filled-in profile and an article
    And a newer engine release "v1.1.0" that changes a workflow file
    When the engine update runs without the ENGINE_UPDATE_TOKEN secret
    Then no branch is pushed, because the token is missing
    And it asks for the manual-merge issue for "v1.1.0"

  @code @id:014-09
  Scenario: The manual-merge issue gives the commands to run
    Given the engine-update workflow
    Then a step runs only when the update needs the token
    And that step opens an issue whose body gives the git commands to merge the release by hand
    And that step marks the run with a warning, not a failure
