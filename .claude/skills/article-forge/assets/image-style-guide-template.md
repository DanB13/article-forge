# Image style guide: <series name>

Locked <date> with <author>. Applies to every cover and in-article image in the
series. HTML sources live in each article's `assets/html/`; re-render with
`scripts/render_cover.py`.

## Palette

| Role | Hex |
|---|---|
| Background | |
| Ink (titles, body, borders) | |
| Accent (subtitles, markers, callouts) | |
| Tint (light fills, separators) | |
| Muted (axis, notes) | |
| Text on dark | |

## Typography

Font stack: <stack> (note what it falls back to on the render machine)

Sizes at the render canvas (<width>x<height>):

- Title:
- Subtitle:
- Body:
- Captions:
- Small labels:

## Layout tokens

- Canvas and padding:
- Corner radii and border widths:
- Visual grammar (e.g. dashed border = optional, solid = fixed):
- wkhtmltoimage: no flexbox or grid; table / table-cell layouts only
