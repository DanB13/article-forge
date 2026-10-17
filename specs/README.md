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

1. Every feature file starts with `Feature:`, an `As a / I want / so that` story,
   and a `# status:` line: `proposed`, `in-progress` or `shipped`.
2. Every scenario has exactly one test tag:
   - `@code` for deterministic behaviour (scripts). A pytest-bdd test must load
     the feature file with `scenarios("...")`.
   - `@eval:<case>` for Claude's behaviour. The eval case directory must exist.
3. `tools/check_specs.py` enforces 1 and 2 in CI.
4. Documentation-only changes need no spec.
5. Specs describe the engine for everyone. Personal rules belong in the user's
   `profile/`, never here.

## Index

| # | Feature | Status |
|---|---|---|
| 001 | [Profile scaffold that never overwrites](001-profile-scaffold.feature) | shipped (v1.2.0) |
| 002 | [Subcut statistics get their own provenance record](002-provenance-subcuts.feature) | shipped (v1.2.0) |
| 003 | [Imagery keeps sources and warns on unsupported CSS](003-imagery-sources.feature) | shipped (v1.2.0) |

`CAPABILITIES.md` at the repo root summarises shipped features by phase.
