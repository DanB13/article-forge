# Maintaining the engine

This repo holds two systems. **A, the maintainer system** (this guide): specs,
tests, evals, CI and releases. **B, the engine**: the `article-forge` skill
that every user runs on their own profile.

## Change the engine: spec first

1. **Write.** Add or edit `specs/NNN-name.feature`: the story (As a / I want /
   so that), `# status: proposed`, and each scenario tagged `@code` or
   `@eval:<case>`.
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
| T2 | Before a release | `claude plugin eval .claude/skills/article-forge --scaffold --allow-tools Bash Write Edit --threshold 0.8 --max-cost-usd 10`, then `python tools/check_specs.py --strict` | Model calls |
| T3 | Monthly | The T2 suite, to catch model drift (a scheduled cloud task, or the `evals` workflow with an API key) | Model calls |

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
under "Retired" in the CHANGELOG. Git history keeps the old files.

## Private specs (your repo only)

Specs, tests and evals that must stay private (for example a style pack built
from someone else's material) live under `local/` in your private repo:
`local/specs/L001-name.feature`, `local/tests/`, `local/evals/<case>/`.
`check_specs.py` scans them too. Upstream never ships `local/`.

A private eval case needs `plugins: ["../../../.claude/skills/article-forge"]`
in its `prompt.md` frontmatter, and runs with
`claude plugin eval local/evals/<case>/prompt.md`.

## Release

1. Bump `.claude/skills/article-forge/VERSION` and the `version` in
   `.claude/skills/article-forge/.claude-plugin/plugin.json`; add the
   CHANGELOG entry. A test fails if the three disagree.
2. Run T2. The maintainer merges the PR on GitHub with **Squash and merge**,
   so `main` gets one commit authored by the maintainer. An AI assistant
   working on the engine stops once the PR is open and its checks are green;
   it does not merge or tag.
3. The maintainer tags and pushes from their own machine:
   `git tag -a v1.3.0 -m "v1.3.0" && git push origin v1.3.0`. Do not create the
   tag from the GitHub Releases page: that makes the release first, and the
   workflow then fails when it tries to make it again. The `release`
   workflow checks the tag, runs the tests, builds the skill ZIP (without
   evals) and publishes a GitHub Release.
4. Users get the engine in Monday's update PR; Claude.ai users download the ZIP.

## Users and this tooling

Every user's repo gets `specs/`, `tests/`, the evals and the CI workflow, so
they can check their own copy. Their CI is optional: they can turn Actions off
for the `ci` workflow without affecting anything else.
