# status: in-progress (v1.4.0-rc1)
# approved: Dan 2026-10-28
Feature: The published links are checked against the link map
  As a writer,
  I want the links as they went live compared with the link map,
  so that a link swapped or dropped at the last minute is caught.

  scripts/check_links.py compares articles/<slug>/links-published.md with the link map in evidence.md.

  @code @id:038-01
  Scenario: A link in the link map but not published is reported
    Given a link map with three links and a published list with two of them
    When I compare the published links with the link map
    Then the missing link is reported with its anchor phrase

  @code @id:038-02
  Scenario: A link published with a different URL is reported
    Given a link map and a published list where one anchor phrase points to a different URL
    When I compare the published links with the link map
    Then that anchor phrase is reported with both URLs
