# Phase 8 — Retro & style learning (the flywheel)

Trigger: the user pastes back the article **as actually published** (or a URL to it). This phase is what makes the system improve per article. Never skip it; prompt for it proactively a day or two after packaging if the user hasn't offered.

## Step 1 — Diff published vs final draft

Compare the published text against the last draft in `articles/<slug>/draft.md`. Categorise every difference:

- **Voice edits** — word swaps, punctuation, rhythm changes, added asides/jokes/personal details
- **Structural edits** — reordered sections, cut paragraphs, changed headers
- **Content edits** — facts, attributions, stats changed or removed
- **Additions** — lines the user wrote that never appeared in any draft (these are gold: they're pure voice)

## Step 2 — Extract patterns, propose profile updates

Learning is **per register**: tag the article with its register (from the brief), and file each proposed rule either under Mechanics (if it should apply everywhere) or under that specific register (if it's audience-flavoured). A joke pattern learned from a jovial network piece must not leak into the authority register. From the diff, propose specific, rule-shaped additions to `profile/voice-profile.md`, e.g.:
- "Consistently replaces [construction] with [construction]"
- "Cut every instance of [word] — add to banned list?"
- "Opens sections with direct address more than drafts do"

Present as a numbered proposal table. The user approves/rejects each. Apply approved items to the profile as a single batch. **Never update the profile without approval.**

## Step 3 — Archive to corpus

Save the published version to `profile/corpus/` (or project knowledge). The corpus is the ground truth for future drafting; drafts are not corpus.

## Step 4 — Process retro

Two quick questions:
1. What in this cycle felt slow or repetitive? (Candidate for a process/template fix — if the user maintains the shared skill, note it for upstream.)
2. What's the follow-up article this piece surfaced? Each piece seeds the next; capture the half-formed brief in `articles/_ideas.md` while it's fresh.

## Output

`articles/<slug>/retro.md`: the diff summary, approved profile changes, corpus confirmation, and the seeded next idea.
