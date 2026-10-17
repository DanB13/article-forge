# Article Forge: working instructions

This repo is an article-writing system. The process lives in the
`article-forge` skill (`.claude/skills/article-forge/`); the user's voice and
context live in `profile/`; work-in-progress lives in `articles/`.

On any article-related request (new idea, draft, edit, fact-check, imagery,
publish, retro), use the **article-forge** skill. Read `profile/voice-profile.md`
and `profile/context.md` before writing anything. If `profile/` does not exist
or still holds unfilled templates, run the skill's onboarding first (it starts
with `scripts/scaffold_profile.py`).

Ownership boundary (important for updates):
- Upstream owns `.claude/skills/`, `specs/`, `tests/`, `tools/`, `.github/`,
  `CLAUDE.md` and the docs. Do not make user-specific edits there; propose
  upstream changes instead (see UPDATING.md).
- `profile/` and `articles/` belong to the user and are never shipped upstream.
  Never modify `profile/` without the user's explicit approval of each change.

Statistics rule: no stat appears unflagged in any near-final draft until it has
a full provenance record in the article's `evidence.md` (see the skill's
Phase 4). This is the system's core credibility guarantee.

Changing the engine: every behaviour change starts as a scenario in `specs/`
tagged `@code` (pytest-bdd test in `tests/`) or `@eval:<case>` (eval case in
`.claude/skills/article-forge/evals/`). Run `python tools/check_specs.py` and
`pytest` before committing. See `specs/README.md`.
