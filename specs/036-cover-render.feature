# status: proposed (v1.4.0-rc1)
Feature: Covers render at the platform's exact size from self-contained HTML
  As a writer,
  I want a cover image at exactly the size the platform needs, with images embedded,
  so that it never crops badly or breaks because a link failed.

  Describes scripts/render_cover.py.

  @code @id:036-01
  Scenario: An embedded image replaces its placeholder
    Given a cover template with the placeholder "PHOTO_URI" and a small photo
    When I embed the photo for "PHOTO_URI"
    Then the template holds the photo as a data URI
    And the placeholder is gone

  @code @id:036-02
  Scenario Outline: The output is resized to the exact size asked for
    Given a rendered image of 1300 by 700 pixels
    When I fit it to <width> by <height>
    Then the image is exactly <width> by <height> pixels

    Examples:
      | width | height |
      | 1200  | 627    |
      | 1080  | 1080   |
