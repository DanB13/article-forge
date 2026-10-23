# status: shipped (v1.3.1)
# approved: Dan 2026-10-22
Feature: Profile format changes arrive as approved migrations
  As a writer who may skip engine updates for months,
  I want changes to the profile format applied in order, only with my approval, and reversibly,
  so that any jump between versions is safe.

  Migrations live in .claude/skills/article-forge/migrations/ (engine) and local/migrations/
  (private). scripts/migrate.py runs them and records each one in profile/.engine-migrations.json.

  @code @id:015-01
  Scenario: A jump runs every migration in between, in order
    Given a writer's profile with no migration record
    And sample migrations "0001, 0002, 0003", where each builds on the one before
    When the writer approves and the migrations run
    Then "0001, 0002, 0003" are recorded as applied, in that order
    And the profile shows the change from each migration

  @code @id:015-02
  Scenario: Nothing changes without the writer's yes
    Given a writer's profile with no migration record
    And sample migrations "0001, 0002, 0003", where each builds on the one before
    When the migrations run without approval
    Then the proposed changes are shown
    And no file is changed

  @code @id:015-03
  Scenario: Running the migrations twice changes nothing the second time
    Given a writer's profile with no migration record
    And sample migrations "0001, 0002, 0003", where each builds on the one before
    When the writer approves and the migrations run twice
    Then the second run changes no file

  @code @id:015-04
  Scenario: A profile with no record counts as before the first migration
    Given a writer's profile with no migration record
    And sample migrations "0001, 0002, 0003", where each builds on the one before
    When I ask which migrations are waiting
    Then "0001, 0002, 0003" are waiting

  @code @id:015-05
  Scenario Outline: Profiles from older versions reach the latest version
    Given a profile from engine version "<version>"
    And sample migrations "0001, 0002, 0003", where each builds on the one before
    When the writer approves and the engine's and the sample migrations run
    Then the profile passes the profile check
    And no migration is waiting

    Examples:
      | version |
      | 1.1.0   |
      | 1.2.0   |
      | 1.3.0   |

  @code @id:015-06
  Scenario: A migration backs up each file before changing it
    Given a writer's profile with no migration record
    And sample migrations "0001, 0002, 0003", where each builds on the one before
    When the writer approves and the migrations run
    Then a backup holds the voice profile as it was before

  @code @id:015-07
  Scenario: A new profile starts with every migration marked as applied
    Given an empty repo
    When I run the profile scaffold
    Then no engine migration is waiting

  # last-verified: 2026-10-23
  @eval:migration-asks-first @id:015-08
  Scenario: The engine asks before running waiting migrations
    Given a writer's repo with a waiting migration
    When the writer starts an article task
    Then Claude says a migration is waiting and what it changes
    And the profile is unchanged
