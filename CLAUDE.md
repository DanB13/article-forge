# Article Forge — working instructions

This repo is an article-writing system. The process lives in the
`article-forge` skill (`.claude/skills/article-forge/`); the user's voice and
context live in `profile/`; work-in-progress lives in `articles/`.

On any article-related request (new idea, draft, edit, fact-check, imagery,
publish, retro), use the **article-forge** skill. Read `profile/voice-profile.md`
and `profile/context.md` before writing anything. If they're still unfilled
templates, run the skill's onboarding first.

Ownership boundary (important for updates):
- `.claude/skills/` and `CLAUDE.md` are maintained upstream. Do not make
  user-specific edits here; propose upstream changes instead (see UPDATING.md).
- `profile/` and `articles/` belong to the user. Never modify `profile/`
  without the user's explicit approval of each change.

Statistics rule: no stat appears unflagged in any near-final draft until it has
a full provenance record in the article's `evidence.md` (see the skill's
Phase 4). This is the system's core credibility guarantee.
