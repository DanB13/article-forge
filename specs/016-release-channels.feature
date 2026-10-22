# status: in-progress
Feature: Updates bring in final releases; the writer can opt in to candidates
  As the maintainer of a few dozen user repos,
  I want users to receive only eval-gated releases, while my own repo tries candidates first,
  so that my private repo is the staging step and nobody else gets untested changes.

  @code @id:016-01
  Scenario Outline: By default the update brings in the latest final release
    Given upstream release tags "<tags>"
    When the update picks its target on the "release" channel
    Then the target is "<target>"

    Examples:
      | tags                                    | target |
      | v1.3.0, v1.3.1-rc1, v1.3.1-rc2          | v1.3.0 |
      | v1.2.0, v1.3.0, v1.10.0                 | v1.10.0 |

  @code @id:016-02
  Scenario Outline: The candidate channel brings in the newest candidate or release
    Given upstream release tags "<tags>"
    When the update picks its target on the "rc" channel
    Then the target is "<target>"

    Examples:
      | tags                                    | target     |
      | v1.3.0, v1.3.1-rc1, v1.3.1-rc2          | v1.3.1-rc2 |
      | v1.3.1-rc2, v1.3.1, v1.3.0              | v1.3.1     |
