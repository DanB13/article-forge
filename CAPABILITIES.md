# Capabilities (v1.2.0)

What the engine does today, by phase. Each line links to the spec that proves
it, where one exists. Specs live in `specs/`; history is in `CHANGELOG.md`.

| Phase | Capability | Spec |
|---|---|---|
| 0 Onboarding | Build a voice profile and author context from published writing | |
| 0 Onboarding | Scaffold `profile/` and `articles/` without overwriting existing files | [001](specs/001-profile-scaffold.feature) |
| 1 Brief | Lock argument, audience, outcome, positioning, register | |
| 2 Research | Test the thesis; collect candidate stats marked `[UNVERIFIED]` | |
| 3 Draft | Complete draft fast; batched, never-silent edit rounds | |
| 4 Provenance | Seven-part record per stat; tiered agentic trace; link map | |
| 4 Provenance | Subcut claims traced as separate records | [002](specs/002-provenance-subcuts.feature) |
| 4 Provenance | Edition-specific anchors for dated reports | |
| 5 Voice edit | De-AI-ification against the profile; density counts | |
| 6 Imagery | HTML to PNG cover pipeline at platform-exact sizes | |
| 6 Imagery | HTML sources kept; unsupported CSS warned | [003](specs/003-imagery-sources.feature) |
| 7 Package | Platform publish pack, companion post, publish sequence | |
| 7 Package | Publish-day link list saved for regression diffs | |
| 8 Retro | Published-vs-draft diff proposes profile updates per register | |
| All | Engine updates arrive as pull requests in your own repo | [UPDATING.md](UPDATING.md) |

Rows without a spec predate v1.2.0. They gain specs as they are next changed.
