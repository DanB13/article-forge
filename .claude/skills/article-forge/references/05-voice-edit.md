# Phase 5 — Voice edit (de-AI-ification)

A dedicated pass, separate from copy editing, hunting for machine fingerprints and adding human ones. Run it against `profile/voice-profile.md` — the user's rules override everything below where they conflict.

## Start with the scorecard

1. From the repo root, run `python <skill-dir>/scripts/meters.py articles/<slug>/draft.md`. It writes `articles/<slug>/scorecard.md`.
2. Show the user every meter's traffic light and reason (overused words, antithesis, rhythm, "is it me?", informality, AI detector). Lights are warnings, never stops.
3. For each flag, propose a fix as options (rule 2). Apply none until the user chooses.
4. Report the **reader-clue checklist**: what an expert reader would notice. **Vocabulary**: AI-tell words and corporate filler. **Sentence shape**: uniform sentence length, stacked "X, not Y". **Generic examples**: any example that could sit in anyone's article; ask the user for their own.
5. When the user decides on a flag, record their call in the Flags table of `scorecard.md`: `accepted` if they changed the line, `ignored` if they kept it. The retro uses these calls to tune the meters. Running the meters again starts a fresh scorecard, so record calls before re-running.

Words listed under `allowed_words` in `profile/settings.yaml` are the writer's own: never flag them, even if they appear below.

## Kill on sight (unless the profile says otherwise)

- Transitional throat-clearing: "worth sitting with", "here's the striking bit", "sit that with a second", "worth noting", "let's be clear".
- Corporate-smooth constructions: "the demand signal could not be clearer".
- Consultant vocabulary LLMs overuse: "inflection point", "leverage" (as a verb), "landscape", "delve", "robust", "seamless".
- Any word on the user's banned list.

## Patterns to COUNT, not just spot

- **"X, not Y" antithesis.** One or two is rhetoric; six is a detectable rhythm. Count them; reduce to 2–3, keeping the ones doing structural work (a header, the close).
- **Fragment triads** ("Unmanaged, unmonitored, and much harder to deal with."). Fine once; a tell when repeated.
- **Repeated phrases within three paragraphs of each other.**

## Add the human fingerprints

Propose (never insert silently) places for:
- **Period detail** — era references, model numbers, "remember those?"
- **First-person confession** — the user's real relationship to the topic.
- **Small risks** — a joke, a wry aside, a "Spoiler:", direct address to the reader.

At least two genuinely personal details per article. These must come FROM the user's life; ask, don't invent.

## Mechanical hygiene checklist

- Punctuation per profile (common ruleset: no em dashes — use semicolons, commas, or sentence breaks; no ampersands in prose).
- Compound modifiers hyphenated (high-agency, multi-billion-dollar).
- Terminology capitalisation consistent throughout.
- Headers are claims; reading only the headers tells the story.

## The relationship in this phase

The user's own rewrites are consistently better hooks than drafted ones. Your job here is to grammar-check the human's instincts — catch a phrase used backwards, a duplicated word, a redundancy — not to replace them. When you flag an issue in the user's own line, offer the minimal fix, not a rewrite.
