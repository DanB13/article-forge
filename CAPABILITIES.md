# Capabilities (v1.3.2)

What the engine does today, by phase. Each line links to the spec that proves
it, where one exists. Specs live in `specs/`; history is in `CHANGELOG.md`.

| Phase | Capability | Spec |
|---|---|---|
| 0 Onboarding | Build a voice profile and author context from published writing; each rule cites its source line | [033](specs/033-voice-profile-build.feature) |
| 0 Onboarding | Unaided writing kept as samples (written or spoken); AI-assisted writing never a sample | [027](specs/027-human-samples.feature) |
| 0 Onboarding | Scaffold `profile/` and `articles/` without overwriting existing files | [001](specs/001-profile-scaffold.feature) |
| 1 Brief | Lock argument, audience, outcome, positioning, register; ask before drafting on an ambiguous theme | [004](specs/004-brief-before-draft.feature) |
| 2 Research | Test the thesis; collect candidate stats marked `[UNVERIFIED]`; thin evidence raised before any draft | [034](specs/034-research.feature) |
| 3 Draft | Complete first draft without stopping once the brief is locked | [004](specs/004-brief-before-draft.feature) |
| 3 Draft | Never-silent edits; the writer's own lines kept word for word | [005](specs/005-never-edit-silently.feature) |
| 3 Draft | Writer's facts kept true; fact and style rounds kept apart | [011](specs/011-accuracy-and-rounds.feature) |
| 3 Draft | Signature phrases by the informality dial; spoken habits left out | [030](specs/030-informality-dial.feature) |
| 3 Draft | First draft kept as `draft-v1.md`; edit distance measured at the retro | [031](specs/031-edit-distance.feature) |
| 4 Provenance | Seven-part record per stat; secondary-only and derived numbers caught | [006](specs/006-statistics-stay-flagged.feature) |
| 4 Provenance | Subcut claims traced as separate records | [002](specs/002-provenance-subcuts.feature) |
| 4 Provenance | Edition-specific anchors for dated reports | [035](specs/035-edition-anchors.feature) |
| 5 Voice edit | Mechanics enforced; contrasts capped; personal detail never invented | [007](specs/007-voice-edit-mechanics.feature) |
| 5 Voice edit | Scorecard: meters with lights and reasons; the writer's call on each flag recorded | [029](specs/029-meters-and-scorecard.feature) |
| 5 Voice edit | Optional modules off by default; Pangram on published text only; keys only in environment variables | [028](specs/028-optional-modules.feature) |
| 6 Imagery | Real material first; generated imagery only as a fallback | [009](specs/009-imagery-real-first.feature) |
| 6 Imagery | HTML to PNG cover pipeline at platform-exact sizes | [036](specs/036-cover-render.feature) |
| 6 Imagery | HTML sources kept; unsupported CSS warned | [003](specs/003-imagery-sources.feature) |
| 7 Package | Platform publish pack, companion post, publish sequence | [037](specs/037-publish-pack.feature) |
| 7 Package | Publish-day link list checked against the link map | [038](specs/038-link-list.feature) |
| 8 Retro | Proposes profile updates for approval; never applies them; archives the piece | [008](specs/008-profile-ownership.feature) |
| All | Engine updates arrive as pull requests in your own repo | [UPDATING.md](UPDATING.md) |
| All | Updates never change `profile/` or `articles/`; a half-finished update is finished | [014](specs/014-upgrade-safety.feature) |
| All | Profile format changes run as approved, ordered, backed-up migrations | [015](specs/015-migrations.feature) |
| All | Final releases by default; release candidates by choice | [016](specs/016-release-channels.feature) |
| All | A set-up check for the GitHub settings updates need | [017](specs/017-setup-check.feature) |
| Maintainer | Every scenario tested; stale specs flagged for retirement | [010](specs/010-spec-hygiene.feature) |
| Maintainer | Consistent versions; skill ZIP release without evals | [012](specs/012-release.feature) |
| Maintainer | A final release needs a passing eval run on exactly that engine | [013](specs/013-release-gate.feature) |
| Maintainer | Scenarios tracked by ID against the last release; skipped tests fail | [018](specs/018-nothing-disappears.feature) |
| Maintainer | Complete skill ZIP; no private material or keys in the repo | [019](specs/019-package-and-secrets.feature) |
| Maintainer | Changes to released tests need a recorded reason and approval | [020](specs/020-test-changes.feature) |
| Maintainer | Graders tied to scenarios; AI judges justified; no passing by doing nothing | [021](specs/021-grounded-graders.feature) |
| Maintainer | Every eval case proven able to fail (mutants) | [022](specs/022-mutant-checks.feature) |
| Maintainer | AI judges calibrated against the maintainer's labels | [023](specs/023-calibration.feature) |
| Maintainer | Safety graders pass every run; style graders 2 of 3 | [024](specs/024-pass-rules.feature) |
| Maintainer | Every rule traced to scenarios; approvals recorded | [025](specs/025-rules-traced.feature) |
| Maintainer | Every guard tested; pre-release contradiction review | [026](specs/026-guards-tested.feature) |
| Maintainer | Every fixture marked fictional, or public with its licence | [032](specs/032-fixture-provenance.feature) |

Rows without a spec gain one when they are next changed.
