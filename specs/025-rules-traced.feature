# status: shipped (v1.3.2)
# approved: Dan 2026-10-23
Feature: Rules and approvals are traced
  As the maintainer,
  I want every engine rule linked to the scenarios that test it, and every spec to record who approved it,
  so that no rule goes untested and approval lives in the repo, not only in a chat.

  @code @id:025-01
  Scenario Outline: Every rule in SKILL.md names the scenarios that test it
    Given a throwaway engine whose SKILL.md rule 1 names <named>
    When I run the spec check
    Then it fails mentioning "<message>"

    Examples:
      | named               | message                             |
      | no scenario         | rule 1 in SKILL.md names no scenario |
      | the scenario 999-01 | names unknown scenario 999-01       |

  @code @id:025-02
  Scenario: Every spec records its approval
    Given a spec "004-demo.feature" with no approval record
    When I run the spec check
    Then it fails mentioning "no approval record"

  @code @id:025-03
  Scenario: An issue template turns an idea into a story with scenarios
    Given the engine-idea issue template
    Then it asks for a story and for scenarios, and both are required
