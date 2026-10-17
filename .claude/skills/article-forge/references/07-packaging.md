# Phase 7 — Package & publish

Ask which platform(s) first; the pack is platform-specific. Output everything as a single `publish-pack.md` per platform.

## The publish pack format (single file)

1. **Change log** — what moved since the last version and why.
2. **Formatting guide** for the platform's editor.
3. **The article, clean**, ready to copy.
4. **Link map** — each URL paired with the exact phrase it anchors to (from `evidence.md`).
5. **Pre-publish checklist** (below).

## LinkedIn article specifics

- LinkedIn's article editor doesn't render markdown: convert to plain text with the formatting guide alongside.
- Headers as H2; subtitle as first italic line.
- Hyperlink the statistic text itself, not bare URLs.
- Pull quotes marked for blockquote formatting.
- Image slots marked inline with captions.
- References section at the article's end AND prepared separately for the first comment.
- Check rendering on mobile before publishing.

## Companion post (LinkedIn)

Written separately from the article, for the actual ICP (which may differ from the article's general audience):
- Conversational register; lead with provocation or the human anecdote.
- The stat-free "here's why I wrote this" style has outperformed stat-led drafts.
- Draft long, then cut ~30%.
- End with a genuine question that invites answers from the reader's own experience.
- Seed the follow-up article in a teaser line if one exists.
- Article link below the fold or in first comment.
- Hashtags: ~7, mixing high-volume, ICP-specific, and one emerging tag.
- **The user rewrites the final version in their own voice — always.** Your drafts are raw material.

## Twitter/X specifics

- Thread structure: hook tweet standing alone → one idea per tweet → article link in the final tweet or reply.
- Hook = the article's repeat-line or strongest verified stat pairing.
- No hashter stuffing; 0–2 max.

## Other platforms (Medium, Substack, company blog)

Markdown usually renders: deliver a markdown pack instead of plain text; keep the link map and checklist identical.

## Publish sequence (LinkedIn)

1. Publish the article.
2. References into the first comment immediately.
3. Companion post linking to the article.
4. Supporting links (forum threads etc.) into the post's comments.
5. Timing: Tue–Thu, 7–9am in the audience's primary timezone.
6. **Capture the published link list.** On publish day, save every URL as it actually went live, with its anchor phrase, to `articles/<slug>/links-published.md`. Links often change at the last minute (a dead slug fixed, a source swapped). The Retro phase and future regression tests diff this file against `evidence.md`.

## Pre-publish checklist

- [ ] Every link clicked and resolving TODAY
- [ ] Report calendar checked for imminent supersession of any stat
- [ ] Cover image matches current title, subtitle, and stats
- [ ] Companion post drafted; link placement decided
- [ ] Closing question answerable from the reader's own experience
- [ ] Mobile rendering checked
- [ ] References prepared for first comment
- [ ] `links-published.md` saved after publishing
