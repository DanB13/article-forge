# Phase 6 — Imagery (its own workstream)

Treat imagery as a separate workstream with its own iteration budget (expect 3–5 rounds on the cover alone). Start only when the text and title are near-final; a cover built before an audience pivot is a cover built twice.

## Rules that consistently produce good visual sets

1. **Real beats conceptual.** Real photographs, real screenshots, real charts, real frameworks. Reject stock-concept imagery repeatedly until something authentic appears; "no rubbish" said five times is what produces a distinctive set.
2. **The user's own finds are usually the best asset.** Ask them to hunt (Unsplash search by the user directly outperforms automated image search for editorial photos). Their own screenshots and photos beat everything.
3. **Borrow authority.** An established vendor's framework diagram or a research lab's own graphic carries credibility no stock photo can. Editorial use with credit; check licensing (Wikimedia/CC/own photography for free use).
4. **One custom chart is worth building.** A hand-built data chart anchoring the conclusion consistently earns its place. Build as HTML/SVG, iterate live (bars, labels, arrows), render to PNG.
5. **Captions do work.** A caption can flip an image's meaning from problem to solution. Draft captions with the user; verify any tool/person attribution with them.
6. **Correct any text inside generated images before export.**

## Cover image formula

Strongest known composition: **one real artefact + one designed panel expressing the thesis**, hard-cut side by side. Export at platform-exact dimensions (LinkedIn: 1200×627 px).

## The rendering pipeline (shipped in `scripts/`)

Established, reproducible pipeline for custom covers and charts:
1. Build a self-contained HTML template; embed all images as base64 data URIs (no external fetches).
2. Render: `wkhtmltoimage --load-error-handling ignore` (ignores blocked font CDNs).
3. Crop/resize to exact dimensions with Pillow.
4. Output PNG to the article's `assets/` folder.

Use `scripts/render_cover.py`. Iterate on contrast and text alignment with the user; expect 3–5 rounds.

Two rules learned the hard way:

- **Keep the HTML sources.** `render_cover.py` copies each input HTML into `assets/html/` next to the PNG (skip with `--no-keep-source`). Without the source, a late title change means rebuilding a slide from scratch.
- **No flexbox or grid.** wkhtmltoimage uses an old WebKit engine that ignores `display: flex` and `display: grid`, and the layout silently collapses. Use `table` / `table-cell` layouts. `render_cover.py` warns when it finds either.

For a multi-article series, lock an image style guide once (palette with hex values, type sizes at the render canvas, layout tokens) in the first article's `assets/image-style-guide.md`, and reuse it for every later piece. Start from `assets/image-style-guide-template.md`.

## Third-party options (document for users, don't assume)

- **Sourced photography**: Unsplash, Pexels (user searches directly; automated editorial image search is unreliable).
- **Generated imagery with text**: Ideogram or Canva handle text-on-image better than most generators, if the user wants a generated cover. Generated imagery is the fallback, not the default; it must still pass rule 1.
- If a design tool is connected (e.g. a design MCP), it can be used for layout mock-ups, but export dimensions and the "real beats conceptual" rule still apply.

## Pre-publish image checks

- Cover matches the CURRENT title, subtitle, and stats (titles change late; covers silently go stale).
- Every image has a caption and, where needed, a credit.
- Licensing checked per image.
