# Changelog

All notable changes to the article-forge engine. Versions follow semver; the
current version is in `.claude/skills/article-forge/VERSION`.

## v1.4.0 (unreleased): Measure

Measures how close the engine's drafts are to the writer, so later releases can
prove they help. rc1 ships the tools; rc2 adds the baseline.

**For writers**
- A scorecard at the voice edit (`scripts/meters.py`): overused AI words,
  stacked "X, not Y" contrasts, sentence rhythm, an "is it me?" distance from
  your own writing, and your signature phrases against the informality dial.
  Each meter shows a traffic light and a reason. Lights are warnings, never
  stops. You mark each flag accepted or ignored; every third article, the retro
  proposes tuning from those calls.
- Your writing samples (`profile/samples/`): your own unaided writing, tagged
  written or spoken, published or not. Only written samples judge rhythm.
  Redaction placeholders and emoji codes are not measured.
- Settings (`profile/settings.yaml`): the informality dial (off, light, warm),
  allowed and banned words, and optional modules. Every module states whether
  your text leaves your machine. Keys live only in environment variables; a key
  written into the file fails the profile check.
- Pangram AI detector, off by default: published text only, and a failure is a
  warning, never a stop.
- Edit distance at the retro (`scripts/edit_distance.py`): the share of words you
  changed from the first draft, recorded per article, with your baseline.
  `draft-v1.md` keeps the first complete draft.
- `scripts/check_links.py` compares the links as published with the link map.
- Covers now fit any target size (scale to cover, then centre-crop).
- Engine updates no longer need the token: an update that changes workflow
  files without it opens an issue with the commands to merge it by hand. The
  set-up check reports the token as optional.
- Migration 0101 adds `profile/settings.yaml` and `profile/samples/` (with your
  approval; nothing existing changes).

**For the maintainer**
- Specs 027 to 038, plus 014-08 and 014-09: 45 scenarios, 11 new eval cases.
  Specs 033 to 038 describe capabilities that had none (voice profile build,
  research, edition anchors, cover render, publish pack, link list).
- Fixture provenance (`tools/fixture_provenance.py`, spec 032): every test-text
  folder is marked fictional, or public with its source and licence, in
  `specs/fixture-provenance.yaml`.
- Pillow is pinned in `requirements-dev.txt` for the cover tests.

## v1.3.2 (2026-10-23): Grounded tests

Tests that cannot lie, weaken quietly, or share the engine's blind spots.

**For the maintainer**
- Test-change control: the ledger fingerprints every scenario's wording, grader,
  eval case, fixture, pytest step file and the pass rules. Changing one that a
  release recorded needs an entry in `specs/test-changes.yaml` (reason, approver).
- Grounded graders: each eval case has a `grading.yaml` naming, per grader, the
  scenario it checks and its tier. AI judges must state why no exact check works;
  every "must not" check has a did-the-work partner.
- Mutant checks (`tools/mutant_check.py`): each case runs once with the engine
  text it depends on removed and must fail. A case that still passes needs an
  approved record in `specs/guard-cases.yaml`.
- Calibration (`tools/calibrate.py`): the maintainer labels about 20 AI-judged
  verdicts per final release; a judge disagreed with twice is flagged and blocks
  the release.
- Pass rules by risk (`evals/grading-policy.yaml`): safety graders must pass
  every run; style graders 2 of 3.
- Every SKILL.md rule names the scenarios that test it; every spec records who
  approved it; an issue template turns an idea into a story with scenarios.
- A guard registry (`tools/guards.yaml`): every guard names a scenario proving
  it fails on bad input.
- A pre-release consistency review (`references/maintainer-review.md`),
  advisory, proven by an eval case with a planted contradiction.

**Engine**
- The skill can review itself for contradictions when asked.

**For writers**
- The update workflow opens its pull request through GitHub's REST API. If
  GitHub still refuses, it opens an issue with a one-click link to create the
  pull request, and the run fails visibly (specs 014-06 and 014-07).

**Release gate results:** 14 of 14 eval cases, 42 of 42 runs with the skill.
Mutants: 4 cases proven able to fail (facts about the writer, migrations,
fact-and-style rounds, retro). 10 recorded as guards with the maintainer's
approval (`specs/guard-cases.yaml`): 7 pass even without the skill, and 3
need the skill but no single instruction (hardening planned for v1.4). The
maintainer's calibration labels agreed with all 20 sampled AI verdicts.
- The engine fingerprint now excludes grading metadata, which the model never
  reads; changes to it are guarded by test-change control.

**Specs:** 020 to 026, 20 approved scenarios as 23 scenarios. Specs 001 to 012
record their approval as backfilled; merging this release confirms them.

## v1.3.1 (2026-10-22): Safe upgrades

Upgrades, releases and tests that cannot fail silently.

**For writers**
- Updates bring in final releases only. Set the repository variable
  `ENGINE_CHANNEL=rc` to receive release candidates first.
- An update that would change `profile/` or `articles/` is refused, and an
  issue explains why.
- The update token now only pushes the update branch; the workflow's own
  token opens the pull request. A token needs only Contents and Workflows.
- A half-finished update (branch pushed, no pull request) is finished by the
  next run.
- The first update of a template copy now also removes engine files that
  upstream deleted. (Found by the new upgrade rehearsal test.)
- Profile migrations: `scripts/migrate.py` runs waiting format changes in
  order, only after your yes, with a backup of every file. Claude checks for
  waiting migrations at the start of each session. No migrations exist yet.
- `scripts/check_setup.py` checks the two GitHub settings updates need.
- `scripts/check_profile.py` checks the profile has what the engine reads.
- UPDATING.md explains how to undo an update.

**Engine behaviour (found by the release eval passes)**
- Rule 7: a message asking for a fact fix and a style change gets only the
  fact fix in that turn, then options for the style change.
- `draft.md` holds the article only; drafting notes go in the reply or in
  `articles/<slug>/notes.md`. The closing question is the last line.
- Every appearance of a statistic carries `[UNVERIFIED]`, including
  back-references, so a later correction finds every mention.

**For the maintainer**
- Final releases need an eval summary made for exactly the released engine
  (`tools/eval_summary.py`), with every case passing and every case from the
  last release run. Release candidates need only the free tests.
- Every scenario has a permanent ID; `specs/ledger.json` records each release's
  scenarios, and removing one needs a retire record in `specs/retired.yaml`.
- `pytest` fails if a code scenario is skipped or never runs.
- Tests check the skill ZIP holds every file the skill mentions, the public
  repo holds no private material, and no tracked file holds a key or token
  (`tools/secret_scan.py`, also in CI).
- Test tools are pinned in `requirements-dev.txt`.
- A pull request template with a definition of done.
- Public repo: push protection, secret scanning and a protected main branch
  (CI must pass) are switched on.

**Specs:** 013 to 019, 29 approved scenarios plus 3 added during the build
(013-05, 015-07, 018-08); see the v1.3.1 pull request.

## v1.3.0 (2026-10-22): Prove

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
- Rule 5: every claim about the writer's past, including roles ("signed off")
  and past thoughts ("I thought we were done"), comes from the brief's anchors
  or is marked `[CONFIRM: ...]`. When a confession needs a detail the anchors
  lack, the engine asks for it before offering openings.
- Imagery starts by asking what real material exists, before anything is built.
- The retro writes `retro.md` at once, with each proposal marked pending, and
  asks before saving the published piece to `profile/corpus/` (spec 008).

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
