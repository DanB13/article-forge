# status: in-progress (v1.4.0-rc1)
# approved: Dan 2026-10-28
Feature: A named edition keeps a link to that edition
  As a writer quoting "the 2025 report",
  I want the link map to keep the edition-specific source as well as the evergreen page,
  so that next year's edition cannot silently replace the numbers I quoted.

  Describes the edition-anchor rule in references/04-provenance.md.

  @eval:provenance-edition-anchor @id:035-01
  Scenario: The link map records both the evergreen link and the edition anchor
    Given an article that names "the 2025 edition" of a report whose evergreen page now shows 2026
    When Claude builds the link map
    Then the link map records the evergreen URL for readers
    And it records the 2025 edition's own release or PDF as the evidence of record
