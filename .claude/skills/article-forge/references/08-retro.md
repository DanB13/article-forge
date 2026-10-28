# Phase 8 — Retro & style learning (the flywheel)

Trigger: the user pastes back the article **as actually published** (or a URL to it). This phase is what makes the system improve per article. Never skip it; prompt for it proactively a day or two after packaging if the user hasn't offered.

## Step 1 — Diff published vs final draft

Compare the published text against the last draft in `articles/<slug>/draft.md`. Categorise every difference:

- **Voice edits** — word swaps, punctuation, rhythm changes, added asides/jokes/personal details
- **Structural edits** — reordered sections, cut paragraphs, changed headers
- **Content edits** — facts, attributions, stats changed or removed
- **Additions** — lines the user wrote that never appeared in any draft (these are gold: they're pure voice)

## Step 1b — Measure the edit distance

Save the published text, article only, as `articles/<slug>/published.md`. If `articles/<slug>/draft-v1.md` exists, run `python <skill-dir>/scripts/edit_distance.py articles/<slug>` from the repo root. Report the edit distance (the share of words the writer changed from the first draft) next to the baseline it prints, and record both in `retro.md`. A falling edit distance means the engine is getting closer to the writer.

## Step 2 — Extract patterns, propose profile updates

Learning is **per register**: tag the article with its register (from the brief), and file each proposed rule either under Mechanics (if it should apply everywhere) or under that specific register (if it's audience-flavoured). A joke pattern learned from a jovial network piece must not leak into the authority register. From the diff, propose specific, rule-shaped additions to `profile/voice-profile.md`, e.g.:
- "Consistently replaces [construction] with [construction]"
- "Cut every instance of [word] — add to banned list?"
- "Opens sections with direct address more than drafts do"

Present as a numbered proposal table. The user approves/rejects each. Apply approved items to the profile as a single batch. **Never update the profile without approval.**

## Step 2b — Tune the meters (every third article)

Once three published articles have scorecards, read the Flags tables in them. If the writer ignored most of one meter's flags, propose loosening it, for example adding a word to `allowed_words` in `profile/settings.yaml`. If the diff shows the writer cutting a word no meter flagged, propose adding it to `banned_words`. These are profile changes: propose them in the same numbered table and apply only what the writer approves.

## Step 3 — Archive to corpus

Ask once: "May I save the published version to `profile/corpus/<slug>.md`?" Save it only after a yes, because `profile/` belongs to the user. The corpus is the ground truth for future drafting; drafts are not corpus.

## Step 4 — Process retro

Two quick questions:
1. What in this cycle felt slow or repetitive? (Candidate for a process/template fix — if the user maintains the shared skill, note it for upstream.)
2. What's the follow-up article this piece surfaced? Each piece seeds the next; capture the half-formed brief in `articles/_ideas.md` while it's fresh.

## Output

Write `articles/<slug>/retro.md` in the same turn as the proposal table, before you wait for answers. It holds the diff summary, every proposal with its status (`pending`, `approved` or `rejected`), the corpus status and the seeded next idea. Update the statuses when the user answers. The record then survives if the session ends before the user replies.
