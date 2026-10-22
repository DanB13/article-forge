# status: shipped (v1.3.0)
Feature: A release is consistent and ships only what users need
  As the maintainer,
  I want every release to carry one version number and a clean skill ZIP,
  so that Claude.ai users get a working skill and nobody gets my test fixtures.

  @code
  Scenario: Version numbers agree
    Given the engine repo
    When I read the skill VERSION, the plugin manifest and the CHANGELOG
    Then all three name the same version

  @code
  Scenario: The skill ZIP leaves out evals and fixtures
    Given the engine repo
    When I build the skill ZIP
    Then the ZIP holds SKILL.md under an article-forge folder
    And the ZIP holds no file from the evals folder
