# Maintaining the engine

This repo holds two systems. **A, the maintainer system** (this guide): specs,
tests, evals, CI and releases. **B, the engine**: the `article-forge` skill
that every user runs on their own profile.

## Change the engine: spec first

1. **Write.** Add or edit `specs/NNN-name.feature`: the story (As a / I want /
   so that), `# status: proposed`, and each scenario tagged `@code` or
   `@eval:<case>`, plus a permanent ID: `@id:NNN-01`, `@id:NNN-02`... An ID
   never changes and is never reused. Scenarios that check the public engine
   repo itself also get `@upstream`, so writers' copies skip them.
   **The maintainer approves the scenarios before the build starts**, and the
   feature records it: `# approved: Dan YYYY-MM-DD`. A new eval case also needs
   a `grading.yaml` (scenario and tier per grader, a reason for each AI judge, a
   did-the-work partner for each "must not" check, and its mutant). A new rule
   in SKILL.md names its scenarios: `<!-- specs: NNN-NN -->`. A new guard goes in
   `tools/guards.yaml` with a scenario proving it fails.
2. **Red.** `python tools/check_specs.py` fails until a test exists. Write the
   pytest-bdd steps in `tests/`, or the eval case in
   `.claude/skills/article-forge/evals/<case>/`. It fails until the behaviour
   exists.
3. **Build.** Set `# status: in-progress`. Change the skill or a script until
   `pytest` passes. Run the eval case once:
   `claude plugin eval .claude/skills/article-forge --case <case> --runs 1 --ablation none --scaffold --allow-tools Bash Write Edit`.
4. **Ship.** Set `# status: shipped (vX.Y.Z)`, add a CHANGELOG entry and a
   CAPABILITIES row, then open a PR. Release when ready (below).

A new behaviour-only feature file also goes in the list in
`tests/test_eval_only_specs.py`, so CI catches Gherkin syntax errors.

## Test tiers

| Tier | When | Command | Cost |
|---|---|---|---|
| T1 | Every push and PR (CI) | `python tools/check_specs.py && pytest` + `claude plugin validate` | Free |
| T2 | Before a final release (enforced) | `claude plugin eval .claude/skills/article-forge --runs 3 --scaffold --allow-tools Bash Write Edit --json run.json --max-cost-usd 20`, then `python tools/eval_summary.py make --version X.Y.Z --from run.json` | Model calls |
| T3 | Monthly | The T2 suite, to catch model drift (a scheduled cloud task, or the `evals` workflow with an API key) | Model calls |

`pytest` also audits itself against the specs: a skipped `@code` scenario, or
one that no test ran, fails the run. Only `@eval` scenarios (and `@upstream`
ones in a writer's copy) may be skipped.

Evals run on whatever account runs them: your Claude plan in a Claude Code
session, or an Anthropic API key in GitHub Actions (`evals` workflow, run by
hand). After a passing run, set `# last-verified: YYYY-MM-DD` on the line above
each passing scenario's tag.

## Try an unreleased engine on real work

From your private repo, load your local clone of this repo for one session:

```bash
claude --plugin-dir ../article-forge/.claude/skills/article-forge
```

A `--plugin-dir` copy replaces the repo's own copy of the skill for that
session only, so you can test a change on your real profile and articles before
it ships. Nothing is installed or changed.

## Retire a spec

`python tools/check_specs.py` warns about retire candidates and stale evals:

- A newer feature declares `# supersedes: 004` while `004-*.feature` still exists.
- An `@eval` scenario in a shipped feature was never verified, or not in 90 days.

It fails on an **orphan**: an eval case that no scenario uses. To retire, delete
the feature (or scenario) and its test or eval case in the same PR, and list it
under "Retired" in the CHANGELOG. Released scenarios and eval cases also need a
retire record (below). Git history keeps the old files.

## Private specs (your repo only)

Specs, tests and evals that must stay private (for example a style pack built
from someone else's material) live under `local/` in your private repo:
`local/specs/L001-name.feature`, `local/tests/`, `local/evals/<case>/`.
`check_specs.py` scans them too. Upstream never ships `local/`.

A private eval case needs `plugins: ["../../../.claude/skills/article-forge"]`
in its `prompt.md` frontmatter, and runs with
`claude plugin eval local/evals/<case>/prompt.md`.

## Release

Every release goes out as a candidate first. Your private repo, set to the `rc`
channel, is the staging step.

1. **Prepare.** Bump `.claude/skills/article-forge/VERSION` and the `version`
   in `.claude/skills/article-forge/.claude-plugin/plugin.json`; add the
   CHANGELOG entry. A test fails if the three disagree. The PR goes green and
   the maintainer merges it with **Squash and merge**. An AI assistant stops
   once the PR is open and green; it does not merge or tag.
2. **Candidate.** The maintainer tags main from their own machine:
   `git tag -a v1.3.1-rc1 -m "v1.3.1-rc1" && git push origin v1.3.1-rc1`.
   The `release` workflow runs the free tests and publishes a pre-release.
   Repos with `ENGINE_CHANNEL=rc` receive it at their next update. Use it on
   real work.
3. **Eval gate.** Time it after the weekly usage reset; cap $15. On main:
   1. T2: `claude plugin eval .claude/skills/article-forge --runs 3 --judge-model sonnet --scaffold --allow-tools Bash Write Edit --json run.json --max-cost-usd 12`
   2. Mutants: `python tools/mutant_check.py --out mutants.json`. A survivor
      needs a stronger case, or an approved entry in `specs/guard-cases.yaml`.
   3. Summary: `python tools/eval_summary.py make --version X.Y.Z --from run.json --mutants mutants.json`
   4. Calibration: `python tools/calibrate.py export --from run.json --version X.Y.Z`;
      the maintainer labels the items (about 15 minutes), then
      `python tools/calibrate.py score --labels .claude/skills/article-forge/evals/calibration/vX.Y.Z.yaml`.
   5. Optional, advisory: ask Claude to review the skill for contradictions
      (`references/maintainer-review.md`).

   Then record the release's scenarios:
   `python tools/check_specs.py --update-ledger X.Y.Z`. It refuses if a
   scenario from the last release vanished without a retire record. Set the
   `# last-verified:` dates and each feature's `# status: shipped (vX.Y.Z)`.
   Commit the summary, the ledger and the dates in one PR; merge it.
   The summary records a fingerprint of the engine files, so any later change
   to the engine means a new eval run.
4. **Final.** Tag the same version without `-rc`:
   `git tag -a v1.3.1 -m "v1.3.1" && git push origin v1.3.1`. The workflow
   also runs `check_specs.py --strict --release X.Y.Z` and
   `eval_summary.py check`, and refuses the release if the ledger is behind,
   the summary is missing or stale, a case failed, or a case from the last
   release was not run. Do not create tags from the GitHub Releases page.
5. Tick the release in the README's Roadmap (in the release PR).
6. Users on the default channel get the final release in Monday's update PR;
   Claude.ai users download the ZIP.

## Retire records

To remove a released scenario or eval case on purpose, add an entry to
`specs/retired.yaml` in the same PR:

```yaml
- id: "004-02"            # a scenario ID, or eval:<case> for an eval case
  reason: "Replaced by 020-01, which checks the same rule more tightly"
  approved_by: "Dan"
  date: "2026-11-02"
```

Without one, `check_specs.py` and the release gate fail and name what vanished.

## Test-change records

A test the last release recorded can change only with an entry in
`specs/test-changes.yaml`. Items are named as `check_specs.py` reports them:
`scenario:004-02`, `grader:<case>/<grader>`, `case:<case>`, `fixture:<name>`,
`steps:<test file>`, or `policy`.

```yaml
- item: "grader:draft-from-locked-brief/stats-flagged"
  reason: "Also accept [UNVERIFIED: source] markers"
  approved_by: "Dan"
  date: "2026-11-02"
```

A case whose mutant survives goes in `specs/guard-cases.yaml` the same way
(`case`, `reason`, `approved_by`, `date`).

## Users and this tooling

Every user's repo gets `specs/`, `tests/`, the evals and the CI workflow, so
they can check their own copy. Their CI is optional: they can turn Actions off
for the `ci` workflow without affecting anything else.
