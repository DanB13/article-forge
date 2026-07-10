# Phase 0 — Onboarding: building the voice profile

Run this once per user (or when they ask to rebuild their profile). Output: `profile/voice-profile.md` and `profile/context.md`, written from the templates in `profile/` at the repo root.

## Step 1 — Gather published writing

Ask the user for 2–3 pieces they've already published, in order of preference:
1. Public URLs (LinkedIn articles, blog posts) — fetch them with web fetch
2. Pasted full text
3. Uploaded files

If they have published nothing yet, ask for anything they've written that sounds like them (emails they're proud of, internal docs) and note the profile is provisional.

## Step 2 — Extract the voice, don't invent it

Analyse the corpus for, at minimum:
- Sentence length distribution and rhythm (short and punchy vs long and flowing)
- Punctuation habits (em dashes? semicolons? parentheticals? ampersands?)
- Formality register and use of first person
- Humour: present? What kind (dry asides, self-deprecation, jokes)?
- Signature moves (rhetorical questions, direct address, callbacks, confession openings)
- Vocabulary to preserve and vocabulary they never use
- How they open and how they close pieces

Present the extracted profile to the user as a proposal. They correct it; only then write the file.

## Step 3 — Interview for context

Ask (multiple-choice where possible, a few at a time, not a wall):
- Role, employer, and credibility base ("why should a reader believe you on this topic?")
- Default vendor/employer positioning: neutral / subtle nod / explicit
- Primary publishing platform(s) and typical audience(s)
- Standing style rules they already know they have (banned words, punctuation rules)
- Goals: engagement, authority, hiring pipeline, lead generation? (Shapes CTAs and closing style.)

Write the answers into `profile/context.md`.

## Step 4 — Confirm and store

Show both files. Get explicit approval. Remind the user these files are theirs: the skill reads them but only proposes changes during Retro (Phase 8), never applies them unilaterally.
