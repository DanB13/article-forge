# Capabilities (v1.3.0)

What the engine does today, by phase. Each line links to the spec that proves
it, where one exists. Specs live in `specs/`; history is in `CHANGELOG.md`.

| Phase | Capability | Spec |
|---|---|---|
| 0 Onboarding | Build a voice profile and author context from published writing | |
| 0 Onboarding | Scaffold `profile/` and `articles/` without overwriting existing files | [001](specs/001-profile-scaffold.feature) |
| 1 Brief | Lock argument, audience, outcome, positioning, register; ask before drafting on an ambiguous theme | [004](specs/004-brief-before-draft.feature) |
| 2 Research | Test the thesis; collect candidate stats marked `[UNVERIFIED]` | |
| 3 Draft | Complete first draft without stopping once the brief is locked | [004](specs/004-brief-before-draft.feature) |
| 3 Draft | Never-silent edits; the writer's own lines kept word for word | [005](specs/005-never-edit-silently.feature) |
| 3 Draft | Writer's facts kept true; fact and style rounds kept apart | [011](specs/011-accuracy-and-rounds.feature) |
| 4 Provenance | Seven-part record per stat; secondary-only and derived numbers caught | [006](specs/006-statistics-stay-flagged.feature) |
| 4 Provenance | Subcut claims traced as separate records | [002](specs/002-provenance-subcuts.feature) |
| 4 Provenance | Edition-specific anchors for dated reports | |
| 5 Voice edit | Mechanics enforced; contrasts capped; personal detail never invented | [007](specs/007-voice-edit-mechanics.feature) |
| 6 Imagery | Real material first; generated imagery only as a fallback | [009](specs/009-imagery-real-first.feature) |
| 6 Imagery | HTML to PNG cover pipeline at platform-exact sizes | |
| 6 Imagery | HTML sources kept; unsupported CSS warned | [003](specs/003-imagery-sources.feature) |
| 7 Package | Platform publish pack, companion post, publish sequence | |
| 7 Package | Publish-day link list saved for regression diffs | |
| 8 Retro | Proposes profile updates for approval; never applies them; archives the piece | [008](specs/008-profile-ownership.feature) |
| All | Engine updates arrive as pull requests in your own repo | [UPDATING.md](UPDATING.md) |
| Maintainer | Every scenario tested; stale specs flagged for retirement | [010](specs/010-spec-hygiene.feature) |
| Maintainer | Consistent versions; skill ZIP release without evals | [012](specs/012-release.feature) |

Rows without a spec gain one when they are next changed.
