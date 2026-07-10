# Getting process updates

Upstream (the maintainer's repo) only ever changes:
- `.claude/skills/article-forge/` (the process)
- `CLAUDE.md`, `README.md`, `UPDATING.md`, `tools/`

Your `profile/` and `articles/` are never modified upstream, so updates
never conflict with your personal files.

## Claude Code / git users

One-time setup (after creating your repo from the template):

    git remote add upstream https://github.com/DanB13/article-forge.git

To update:

    git fetch upstream
    git merge upstream/main

If you've customised skill files locally, git will flag the conflict; prefer
proposing customisations upstream as PRs instead, and keep personal rules in
`profile/` (the skill always defers to your profile).

## Claude.ai users

1. Download the new release ZIP from the upstream repo's Releases page.
2. Settings → Capabilities → Skills → remove the old article-forge skill,
   upload the new ZIP.
3. Your Project knowledge (voice profile, corpus) is untouched.

## Version check

The skill ships a VERSION file. Ask Claude "what version of article-forge am I
running?" and compare against the latest release.
