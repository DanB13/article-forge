# Specs: the canonical record of what the engine does

One `.feature` file per capability. Each file holds the user story, its status
and its scenarios (Given / When / Then). A scenario is not done until a test
proves it.

```
user story ─► scenario ─┬─ @code        ─► pytest-bdd  (tests/)         every commit, free
                        └─ @eval:<case> ─► claude plugin eval            before release, uses model calls
                                            (.claude/skills/article-forge/evals/<case>/)
```

## Rules

1. Every feature file records its approval (`# approved: <name> YYYY-MM-DD`), starts with `Feature:`, an `As a / I want / so that` story,
   and a `# status:` line: `proposed`, `in-progress` or `shipped`. A feature
   that replaces another adds `# supersedes: NNN`.
2. Every scenario has a permanent ID tag, `@id:NNN-NN` (private: `@id:L001-01`),
   and exactly one test tag:
   - `@code` for deterministic behaviour (scripts). A pytest-bdd test must load
     the feature file with `scenarios("...")`.
   - `@eval:<case>` for Claude's behaviour. The eval case directory must exist.
3. `tools/check_specs.py` enforces 1 and 2 in CI, fails on orphan eval cases,
   and warns about retire candidates and `@eval` scenarios not verified in 90
   days (`# last-verified: YYYY-MM-DD` above the tag). `--strict` turns
   warnings into failures before a release.
4. `specs/ledger.json` records every scenario ID in the last release. A
   released scenario cannot vanish: restore it, or add a retire record to
   `specs/retired.yaml` with a reason and an approver. `pytest` fails if a
   `@code` scenario is skipped or never runs (`@upstream` ones may skip in a
   writer's copy, because they check the public engine repo itself).
5. Changing a test the last release recorded (scenario wording, grader, eval
   case, fixture, pytest step file, pass rules) needs an entry in
   `specs/test-changes.yaml` with the reason and who approved it. Each eval
   case's `grading.yaml` links every grader to a scenario and a tier, and names
   the case's mutant (see `MAINTAINING.md`).
6. Documentation-only changes need no spec.
7. Specs describe the engine for everyone. Personal rules belong in the user's
   `profile/`, never here. Private specs live under `local/` in the user's repo.

The full workflow (tiers, retiring, releasing) is in `MAINTAINING.md`.

## Index

| # | Feature | Status |
|---|---|---|
| 001 | [Profile scaffold that never overwrites](001-profile-scaffold.feature) | shipped (v1.2.0; v1.3.0) |
| 002 | [Subcut statistics get their own provenance record](002-provenance-subcuts.feature) | shipped (v1.2.0) |
| 003 | [Imagery keeps sources and warns on unsupported CSS](003-imagery-sources.feature) | shipped (v1.2.0) |
| 004 | [The brief comes first; then a full first draft without stopping](004-brief-before-draft.feature) | shipped (v1.3.0) |
| 005 | [Never edit silently; the writer's own lines win](005-never-edit-silently.feature) | shipped (v1.3.0) |
| 006 | [No statistic is trusted until it is traced](006-statistics-stay-flagged.feature) | shipped (v1.3.0) |
| 007 | [The voice edit enforces mechanics and never invents the writer](007-voice-edit-mechanics.feature) | shipped (v1.3.0) |
| 008 | [The writer owns the profile; the retro only proposes](008-profile-ownership.feature) | shipped (v1.3.0) |
| 009 | [Real imagery comes first](009-imagery-real-first.feature) | shipped (v1.3.0) |
| 010 | [Spec hygiene: every scenario tested, stale ones flagged](010-spec-hygiene.feature) | shipped (v1.3.0) |
| 011 | [Facts about the writer stay true; fact and style edits stay apart](011-accuracy-and-rounds.feature) | shipped (v1.3.0) |
| 012 | [A release is consistent and ships only what users need](012-release.feature) | shipped (v1.3.0) |
| 013 | [Nothing ships without a passing eval run](013-release-gate.feature) | shipped (v1.3.1) |
| 014 | [Engine updates cannot touch the writer's own folders](014-upgrade-safety.feature) | shipped (v1.3.1) |
| 015 | [Profile format changes arrive as approved migrations](015-migrations.feature) | shipped (v1.3.1) |
| 016 | [Updates bring in final releases; candidates by choice](016-release-channels.feature) | shipped (v1.3.1) |
| 017 | [A set-up check finds missing GitHub settings](017-setup-check.feature) | shipped (v1.3.1) |
| 018 | [Nothing disappears silently](018-nothing-disappears.feature) | shipped (v1.3.1) |
| 019 | [The release package is complete and nothing private leaks](019-package-and-secrets.feature) | shipped (v1.3.1) |
| 020 | [Test changes are visible and approved](020-test-changes.feature) | in progress (v1.3.2) |
| 021 | [Graders are grounded in the spec](021-grounded-graders.feature) | in progress (v1.3.2) |
| 022 | [Every eval case can fail](022-mutant-checks.feature) | in progress (v1.3.2) |
| 023 | [The maintainer's labels calibrate the AI judges](023-calibration.feature) | in progress (v1.3.2) |
| 024 | [Pass rules follow risk](024-pass-rules.feature) | in progress (v1.3.2) |
| 025 | [Rules and approvals are traced](025-rules-traced.feature) | in progress (v1.3.2) |
| 026 | [The guards themselves are tested](026-guards-tested.feature) | in progress (v1.3.2) |

`CAPABILITIES.md` at the repo root summarises shipped features by phase.
