# Changelog

All notable changes to the article-forge engine. Versions follow semver; the
current version is in `.claude/skills/article-forge/VERSION`.

## v1.3.0 (2026-10-19): Prove

Every non-negotiable rule now has a test.

**Engine behaviour**
- Once the brief is locked, research and the complete first draft run without
  stopping (decision of 19 Oct 2026). The one exception: research that
  contradicts the thesis is raised before drafting.
- Onboarding's scaffold reminds users to switch on engine update PRs.
- The skill now also starts on any change request to a draft, including files
  under `articles/` (it did not start for "replace this line" requests).
- A message that asks for a fact fix and a style change applies the fact fix
  first, then handles the style change as its own round.
- Eval graders for long drafts use exact checks (section count, closing
  question, every % figure flagged) instead of an LLM judge that saw only part
  of the file.

**Specs and evals**
- 8 new feature files (004 to 009, 011, 012) covering all 7 non-negotiable
  rules, the voice edit, the retro's profile ownership and releases.
- 10 new eval cases with a shared fictional fixture repo (`evals/_fixtures/`).
- 010: `check_specs.py` fails on orphan eval cases, warns about retire
  candidates (`# supersedes:`) and evals not verified in 90 days
  (`# last-verified:`), scans private specs under `local/`, and has `--strict`.

**Maintainer system**
- `MAINTAINING.md`: spec-first workflow, test tiers, trying an unreleased
  engine on real work (`--plugin-dir`), retiring specs, private specs, releases.
- `release` workflow: a version tag checks VERSION, runs the tests, builds the
  skill ZIP (without evals) and publishes a GitHub Release.
- A test fails if VERSION, the plugin manifest and the CHANGELOG disagree.

## v1.2.0 (2026-10-17): Foundations

**Updates that cannot touch your work**
- `profile/` and `articles/` are no longer shipped. Their templates now live in
  the skill (`assets/templates/`), and `scripts/scaffold_profile.py` creates any
  missing file without overwriting existing ones. Onboarding runs it first.
- New `engine-update` workflow: every Monday your copy checks upstream and opens
  a pull request with the new engine version. Conflicts open an issue instead.
- UPDATING.md now covers the one-time merge every template copy needs
  (`--allow-unrelated-histories -X theirs`); the workflow does it automatically.

**Provenance (Phase 4)**
- Subcut claims ("rises to X% at large firms") need their own provenance record.
- Edition-specific anchors: when an article names a report edition, record an
  edition-specific URL alongside any evergreen link.

**Imagery (Phase 6)**
- `render_cover.py` keeps a copy of each HTML source in `assets/html/` and warns
  on `display: flex` and `display: grid`, which wkhtmltoimage cannot render.
- New `assets/image-style-guide-template.md` for multi-article series.

**Packaging (Phase 7)**
- Publish sequence step 6: save the live link list to `links-published.md`.

**Testing**
- `specs/`: one Gherkin feature file per capability, each scenario tagged
  `@code` (pytest-bdd) or `@eval:<case>` (`claude plugin eval`).
- `tests/`: pytest-bdd step definitions for the `@code` scenarios.
- `.claude/skills/article-forge/evals/`: behaviour eval cases with synthetic
  fixtures, including a regression case for subcut stat laundering.
- `tools/check_specs.py` fails CI when a scenario has no test.
- CI runs the spec check, pytest and `claude plugin validate` on every push.
  The `evals` workflow runs behaviour evals on demand.
- The skill folder now has a `.claude-plugin/plugin.json` manifest, so Claude
  Code can evaluate it as a skills-directory plugin.

## v1.1.0 (2026-07-10)

- Initial public template: phases 0 to 8, cover rendering pipeline, Claude.ai
  skill ZIP packaging.
