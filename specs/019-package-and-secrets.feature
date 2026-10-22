# status: in-progress
Feature: The release package is complete and nothing private leaks
  As the maintainer of a public engine,
  I want the skill ZIP checked for missing files and the repo checked for private material,
  so that Claude.ai users get a working skill and nothing of mine reaches the public.

  @code @id:019-01
  Scenario: The skill ZIP holds every file the skill refers to
    Given the engine repo
    When I build the skill ZIP
    Then every skill file that SKILL.md or a reference file mentions is in the ZIP

  @code @id:019-02
  Scenario: Every file the skill refers to exists
    Given the engine repo
    When I read SKILL.md and the reference files
    Then every skill file they mention exists

  @code @upstream @id:019-03
  Scenario: The engine repo holds no private-only material
    Given the engine repo
    When I list the files the engine repo tracks
    Then none is under local/ or names a private style pack

  @code @id:019-04
  Scenario: No tracked file holds a key or token
    Given the engine repo
    When I scan the tracked files for keys and tokens
    Then none is found

  @code @id:019-05
  Scenario: The key scan catches a planted token
    Given a file that holds a GitHub token
    When I scan it for keys and tokens
    Then the token is reported

  @code @id:019-06
  Scenario: CI installs pinned test dependencies
    Given the CI and release workflows
    Then each installs its test tools from requirements-dev.txt
    And every package in requirements-dev.txt is pinned to one version
