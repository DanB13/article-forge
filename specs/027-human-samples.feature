# status: in-progress (v1.4.0-rc1)
# approved: Dan 2026-10-28
Feature: The writer's human samples are the reference for "is it me?"
  As a writer,
  I want a small set of my own unaided writing, each piece tagged written or spoken,
  so that the engine measures its drafts against me and not against AI-assisted text.

  Samples live in profile/samples/. Each sample has a header: kind (written, spoken, or
  description for a summary of the writer's style), source, date, register, published and
  human_only. A file may hold several samples, each with its own header. scripts/samples.py
  reads them. The phrase fingerprint (profile/samples/fingerprint.md) lists signature
  phrases and phrases to leave out.

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
      | kind description, source, date, human_only true | kept for reference, not used to measure |

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
  Scenario: Onboarding keeps AI-assisted writing out of the samples
    Given a new writer who has pasted two pieces and said the second was written with AI help
    When onboarding builds the profile
    Then it proposes only the first piece as a sample, tagged written and human-only
    And it writes nothing to profile/samples/ before the writer approves

  @code @id:027-06
  Scenario: Placeholders and emoji codes are not measured
    Given a written sample that holds "[PERSON]", "[LINK]" and ":grin:"
    When the meters read the sample
    Then the measured text contains none of them
