# status: in-progress (v1.4.0-rc1)
# approved: Dan 2026-10-28
Feature: The publish pack holds everything needed to publish, in one file
  As a writer on publish day,
  I want one file per platform with the change log, formatting guide, clean article, link map and checklist,
  so that publishing is a copy-and-check job, not a hunt.

  Describes references/07-packaging.md.

  @eval:publish-pack-sections @id:037-01
  Scenario: The pack has the five sections in order
    Given an article that has passed provenance and voice edit
    When the writer asks for the LinkedIn publish pack
    Then publish-pack.md holds the change log, formatting guide, clean article, link map and pre-publish checklist, in that order

  @eval:publish-pack-sections @id:037-02
  Scenario: The LinkedIn article is plain text, not markdown
    Given an article that has passed provenance and voice edit
    When the writer asks for the LinkedIn publish pack
    Then the clean article contains no markdown syntax
