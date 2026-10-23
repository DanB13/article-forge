# status: shipped (v1.2.0)
# approved: Dan 2026-10-23 (backfilled in v1.3.2: merging that release's PR confirms it)
Feature: Imagery keeps sources and warns on unsupported CSS
  As a writer who changes titles late,
  I want every rendered image to keep its HTML source and to warn me about
  layouts the renderer cannot draw,
  so that I can re-render in minutes instead of rebuilding from scratch.

  @code @id:003-01
  Scenario: Rendering keeps a copy of the HTML source
    Given a cover template "cover.html"
    When I keep the source for output "assets/cover.png"
    Then "assets/html/cover.html" exists

  @code @id:003-02
  Scenario: A source already in the html folder is not copied onto itself
    Given a cover template "assets/html/cover.html"
    When I keep the source for output "assets/cover.png"
    Then no copy is made

  @code @id:003-03
  Scenario Outline: Unsupported layout CSS is reported
    Given HTML containing "<css>"
    When I lint the HTML
    Then there are <count> warnings

    Examples:
      | css                    | count |
      | display: flex          | 1     |
      | display:grid           | 1     |
      | display: inline-flex   | 1     |
      | display: table-cell    | 0     |
