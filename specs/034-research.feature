# status: proposed (v1.4.0-rc1)
Feature: Research tests the thesis and trusts nothing yet
  As a writer,
  I want research to tell me early if the evidence is thin, and to mark every statistic unverified,
  so that a weak argument or a bad number never reaches a draft unnoticed.

  Describes references/02-research.md as it works today.

  @eval:research-flags-stats @id:034-01
  Scenario: Every statistic in the research notes is flagged and sourced
    Given a locked brief
    When Claude writes research.md from fixture sources
    Then every statistic carries "[UNVERIFIED]" and its claimed source

  @eval:research-thin-evidence @id:034-02
  Scenario: Thin evidence is raised before any draft exists
    Given a locked brief whose fixture sources contradict its thesis
    When Claude researches it
    Then Claude tells the writer the evidence is thin or contrary before drafting
    And no draft file is written
