# status: proposed (v1.4.0-rc1)
Feature: The writer's human samples are the reference for "is it me?"
  As a writer,
  I want a small set of my own unaided writing, each piece tagged written or spoken,
  so that the engine measures its drafts against me and not against AI-assisted text.

  Samples live in profile/samples/, one file per sample, with a header: kind (written or
  spoken), source, date and human_only. scripts/samples.py reads them. The phrase
  fingerprint (profile/samples/fingerprint.md) lists signature phrases and phrases to leave out.

  @code @id:027-01
  Scenario Outline: Only a complete, human-only sample is used as a reference
    Given a sample whose header has <header>
    When I list the reference samples
    Then the sample is <result>

    Examples:
      | header                                         | result                                   |
      | kind written, source, date, human_only true    | used                                     |
      | kind written, source, date, human_only false   | not used, because it is not human-only   |
      | kind written, date, human_only true, no source | not used, because the source is missing  |
      | kind poem, source, date, human_only true       | not used, because the kind is unknown    |

  @code @id:027-02
  Scenario: A spoken sample is never used to judge sentence rhythm
    Given one written sample and one spoken sample
    When the meters measure sentence rhythm
    Then only the written sample is used
    And the spoken sample is used for phrasing only

  @code @id:027-03
  Scenario: The fingerprint gives signature phrases and phrases to leave out
    Given a fingerprint that lists "have a crack" as a signature phrase and "I mean" to leave out
    When I read the fingerprint
    Then "have a crack" is a signature phrase
    And "I mean" is a phrase to leave out

  @code @id:027-04
  Scenario: With no samples, the meters say so and carry on
    Given a profile with no samples
    When the meters run on a draft
    Then the "is it me?" meter is grey with the reason "no samples yet"
    And every other meter still reports

  @eval:onboarding-asks-for-samples @id:027-05
  Scenario: Onboarding asks for unaided writing and tags each piece
    Given a new writer who has pasted two pieces, one written with AI help
    When onboarding builds the profile
    Then it asks which pieces were written without AI help
    And it proposes only the unaided piece as a sample, tagged written
    And it writes nothing to profile/samples/ before the writer approves
