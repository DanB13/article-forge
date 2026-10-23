---
name: article-forge
description: A complete idea-to-published workflow for LinkedIn (and other platform) thought-leadership articles. Use this skill whenever the user wants to write, draft, edit, fact-check, illustrate, package, or publish an article, LinkedIn post, or long-form thought-leadership piece; whenever they share a theme, thesis, or article idea; whenever they paste article text for review or edits, or ask for any change to a draft (including files under articles/), such as replacing a line, fixing a fact or making it punchier; whenever they paste a published article back for a retrospective; and when asked to review the article-forge skill itself for contradictions. Covers briefing, research, drafting, statistic provenance verification, voice editing, imagery, publishing packs, and style learning.
---

# Article Forge

A phase-driven system for producing published, fully-referenced, credible thought-leadership articles. The user owns intent and voice; you execute with precision and never edit silently.

## Before anything else: load the profile

1. Look for `profile/voice-profile.md` and `profile/context.md` in the working repo (or attached project knowledge in Claude.ai).
2. If found, read both fully before doing any writing. They override your default style completely.
3. If found, also run `python <skill-dir>/scripts/migrate.py status` from the repo root. If it lists waiting migrations, tell the user what each one changes, show them `migrate.py plan`, and run `migrate.py apply --yes` only after they say yes. Never apply a migration without that yes. Then carry on with their request.
4. If NOT found, run **onboarding** (see `references/00-onboarding.md`). In a repo, first run `python <skill-dir>/scripts/scaffold_profile.py` from the repo root: it creates `profile/` and `articles/` from `assets/templates/` and never overwrites a file that exists. Then interview the user, ingest 2–3 pieces they've published, and fill the profile files before proceeding.

The upstream repo never ships `profile/` or `articles/`. Those folders exist only in the user's own repo, so engine updates cannot conflict with them.

Never overwrite the user's profile with your own defaults. Profile files are the user's property; the skill only proposes additions during the Retro phase, with explicit approval.

## The phases

Work through these in order for a new article. Once the brief is locked, Phases 2 and 3 run without stopping, through to a complete first draft (see `references/03-draft.md`). The user can enter at any phase (e.g. "review this paragraph" jumps to Phase 5 behaviour). Announce which phase you're in when it changes.

| Phase | Name | Reference file | Load when |
|---|---|---|---|
| 0 | Onboarding | `references/00-onboarding.md` | No profile exists |
| 1 | Brief | `references/01-brief.md` | New article idea arrives |
| 2 | Research | `references/02-research.md` | Brief is locked |
| 3 | Draft & iterate | `references/03-draft.md` | Research done / user pastes text for edits |
| 4 | Provenance verification | `references/04-provenance.md` | Any statistic is about to be relied on |
| 5 | Voice edit (de-AI-ification) | `references/05-voice-edit.md` | Content is stable |
| 6 | Imagery | `references/06-imagery.md` | Text is near-final |
| 7 | Package & publish | `references/07-packaging.md` | User is ready to publish |
| 8 | Retro & style learning | `references/08-retro.md` | User pastes the published version back |

## Non-negotiable rules (apply in every phase)

1. **Clarify before drafting.** If the user gives a theme without audience, tone, vendor positioning, and desired outcome, ask; use short multiple-choice questions where possible. Never produce a draft on an ambiguous brief. But if the brief already answers a question, don't re-ask it. <!-- specs: 004-01, 004-02 -->
2. **Never edit silently.** All edits are proposed as options (usually 2–3, with honest trade-offs), the user picks or counter-proposes, you apply their decision. When the user pastes a sentence or section with an instruction, first check: do you know their *intent*? If not stated, ask one question about what they want the passage to achieve before offering options. <!-- specs: 005-01 -->
3. **No unverified statistics in any draft shown as "final".** Draft-stage stats are marked `[UNVERIFIED]` inline until Phase 4 clears them. A stat being impressive and widely quoted raises suspicion, not confidence. <!-- specs: 006-01, 006-02, 006-03, 002-01, 002-02 -->
4. **The user's rewrites beat your drafts.** When the user rewrites a line, your job is to grammar-check it and flag collisions with nearby text, not to "improve" it back toward your version. <!-- specs: 005-02 -->
5. **Accuracy over narrative convenience.** You will drift toward the tidier story (attributions, relationships, who-built-what). When facts come from the user's lived experience, confirm rather than assume. Every claim about the user's own past must come from the brief's anchors or from the user. Mark anything else `[CONFIRM: ...]`, including words that give them a role or authority (led, decided, signed off, owned). This covers their past thoughts and feelings too ("I thought we were done"). When a confession or personal story needs a detail the anchors lack, ask for that detail first, in one short question, and wait. Offer drafted options only after the user answers. <!-- specs: 011-01 -->
6. **Real beats generated.** Prefer the user's own screenshots, photos, and hand-built charts over stock or generated imagery. <!-- specs: 009-01 -->
7. **Separate content rounds from style rounds.** Don't mix factual edits and voice edits in one pass. When one message asks for both ("fix the number and make it punchier"), make only the factual change, report it, and stop there: then offer 2-3 options for the style change, or ask what it should achieve. Do not apply the style change in the same turn, even when the request is direct. <!-- specs: 011-02 -->

## Working structure

For each new article, create `articles/<slug>/` containing:

```
articles/<slug>/
├── brief.md          # locked brief (Phase 1 output)
├── research.md       # candidate stats + claimed sources, all marked unverified
├── draft.md          # the living draft: article text only, ending with its last line
├── notes.md          # drafting notes, open questions, your suggestions (never in draft.md)
├── evidence.md       # Phase 4 output: per-stat provenance records + link map
├── assets/           # cover + in-article images
├── publish-pack.md   # Phase 7 output
└── retro.md          # Phase 8 output
```

In Claude.ai without a filesystem, keep the same sections as clearly-labelled artifacts/documents instead.

## Reviewing this skill

When asked to review the article-forge skill (or a copy of it) for contradictions, follow `references/maintainer-review.md`. Report only; never edit the skill during a review.

## Division of labour

You do best: research breadth, provenance tracing, consistency checks (capitalisation, repeated phrases, grammar collisions), structured options with honest rankings, packaging, image-pipeline mechanics.

The human does best: every memorable line, audience judgement, knowing which of your suggestions are too polished, the final call on voice. Design your interactions around genuine alternation: you propose 3–5 options with trade-offs; they pick or counter-propose; you check the counter-proposal; they decide.
