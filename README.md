# Article Forge

An idea-to-published article system with Claude at its heart. It takes you from
a rough theme to a published, fully-referenced, credible thought-leadership
piece: guided brief, research, drafting in *your* voice, statistic provenance
verification, imagery, platform publishing packs, and a retro loop that learns
your style from what you actually published.

Built from the real production of multiple published LinkedIn articles,
including the statistic-laundering failures caught along the way (misattributed
headline stats, derived numbers sold as primary research, zombie stats,
publish-day link rot). The process exists so you don't repeat them.

## What's in the box

```
article-forge/
├── .claude/skills/article-forge/   # THE ENGINE (maintained upstream)
│   ├── SKILL.md                    #   orchestrator: phases & rules
│   ├── references/                 #   one playbook per phase (0–8)
│   ├── scripts/                    #   render_cover.py, scaffold_profile.py
│   ├── assets/templates/           #   profile/ and articles/ starter files
│   ├── evals/                      #   behaviour evals (claude plugin eval)
│   └── .claude-plugin/plugin.json  #   manifest, so Claude Code can evaluate it
├── specs/                          # one Gherkin feature file per capability
├── tests/                          # pytest-bdd tests for @code scenarios
├── tools/                          # check_specs.py, package_skill.sh
├── .github/workflows/              # ci, evals, engine-update
├── CAPABILITIES.md  CHANGELOG.md   # what the engine does; what changed
├── CLAUDE.md                       # Claude Code entry point
└── UPDATING.md                     # how updates reach your repo
```

Your own repo also gets `profile/` (voice profile, context, corpus, report
calendar) and `articles/` (one folder per article). Onboarding creates them;
upstream never ships them.

The design principle: **process and profile are separate.** The process is
shared and versioned (this repo, upstream). Your voice profile, context, and
article corpus are yours, live only in your own repo, and are never touched by
updates.

## Install

### Path A — Claude Code (recommended)

1. Click **Use this template** on GitHub → your own **private** repo. Don't fork:
   a fork of a public repo is always public.
   Private matters: your `profile/` and drafts will live in it.
2. Clone it and open Claude Code in the repo root.
3. Say: *"Set up my voice profile"*. Claude creates `profile/` and `articles/`
   from the templates, then runs onboarding, ingesting 2–3 things you've
   published.
4. Do the one-time upstream merge in [UPDATING.md](UPDATING.md) and enable the
   `engine-update` workflow, so future engine versions arrive as pull requests.
5. Then: *"New article: [your theme/thesis/audience]"* and follow the phases.

Optional for the image pipeline: `sudo apt install wkhtmltopdf` and
`pip install pillow`.

### Path B — Claude.ai (no terminal)

1. Download the latest skill ZIP from this repo's **Releases** (or run
   `tools/package_skill.sh` if you have the repo).
2. In Claude.ai: **Settings → Capabilities → Skills → Upload skill** and upload
   the ZIP. (The ZIP must contain the `article-forge` folder at its root;
   the release ZIP already does.)
3. Create a **Project** for your writing. In the first conversation, say
   *"Set up my voice profile"*; save the generated `voice-profile.md` and
   `context.md` files it produces into the Project's knowledge.
4. Work on articles inside that Project so memory and knowledge compound.
5. **Recommended:** connect the GitHub connector and create a private repo from
   this template anyway. Point the skill at it and Claude reads your profile
   from, and writes drafts/evidence/retros back to, the same repo structure a
   Claude Code user has; your work persists across conversations in git.


### Path C — Claude Project only (no skill upload)

If you can't upload skills: copy the contents of
`.claude/skills/article-forge/SKILL.md` and the `references/` files (plus `assets/templates/` for the profile structure) into a
Project's knowledge, and paste the SKILL.md "Before anything else" and
"Non-negotiable rules" sections into the Project instructions. Everything works;
you just update files manually.

## Updating

See [UPDATING.md](UPDATING.md). Short version: upstream never ships
`profile/` or `articles/`, so updates cannot conflict with your work. After one
first merge, new versions arrive in your repo as pull requests. Claude.ai users
re-upload the new release ZIP.

## Testing

Every capability is a scenario in `specs/`. Deterministic scenarios (`@code`)
run with pytest-bdd on every push; Claude's behaviour (`@eval:<case>`) runs with
`claude plugin eval`, on demand, because it uses model calls.

```bash
pip install pytest pytest-bdd
python tools/check_specs.py     # every scenario has a test
pytest                          # @code scenarios
claude plugin eval .claude/skills/article-forge --scaffold --allow-tools Bash Write Edit
```

See [specs/README.md](specs/README.md) and the evals
[README](.claude/skills/article-forge/evals/README.md).

## The phases at a glance

0. **Onboarding** — build your voice profile from what you've published
1. **Brief** — lock argument, audience (asked twice!), outcome, positioning
2. **Research** — test the thesis; collect stats, all marked unverified
3. **Draft** — complete draft fast, then batched, never-silent edit rounds
4. **Provenance** — every stat traced to its originating report; link map built
5. **Voice edit** — de-AI-ification against your profile; human fingerprints in
6. **Imagery** — real beats conceptual; cover pipeline; 3–5 iteration rounds
7. **Package** — platform publish pack, companion post, publish sequence
8. **Retro** — paste back the published piece; the diff updates your profile

## Contributing

Process improvements welcome via PR. Start with a scenario in `specs/` and a
test that proves it; CI checks both. Please never include anything from your
own `profile/` or `articles/`.

## License

MIT — see [LICENSE](LICENSE).
