# status: in-progress (v1.4.0-rc1)
# approved: Dan 2026-10-28
Feature: Test text says where it came from
  As the maintainer,
  I want every piece of text the tests use to be marked fictional, or public with its licence,
  so that no real writer's private text reaches the public repo by accident.

  @code @upstream @id:032-01
  Scenario: Every fixture in the engine repo is marked
    Given the engine repo
    When I check the eval fixtures and test texts
    Then each one is marked "fictional" or "public" with a source and a licence

  @code @id:032-02
  Scenario: An unmarked fixture is reported
    Given an eval fixture with no provenance mark
    When I check the eval fixtures and test texts
    Then the check fails and names the fixture
