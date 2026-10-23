# Getting engine updates

Upstream (this repo) ships only the engine: `.claude/skills/`, `specs/`,
`tests/`, `tools/`, `.github/` and the docs. It never ships `profile/` or
`articles/`. Those exist only in your repo, so an update cannot overwrite them.

```
upstream   a──b──────────c (v1.2)─────────d (v1.3)
               \          \                \
your repo  1…n─M1──n+1────M2───n+2─────────M3
               ▲
               one-time merge with --allow-unrelated-histories; M2, M3 are normal
```

## The first update

A repo created with **Use this template** starts with its own first commit, so
it shares no history with upstream. The update tool handles this for you: the
first update links the two histories (`--allow-unrelated-histories -X theirs`,
upstream wins on engine files), and every later update is an ordinary merge.
Your `profile/` and `articles/` are not affected, because upstream does not ship
them. If you had edited engine files yourself, the first update replaces those
edits; move personal rules into `profile/` first.

You cannot use a GitHub fork instead: a fork of a public repository is always
public, and your profile and drafts would be visible.

To do the first merge by hand instead (or ask Claude Code to):

```bash
git remote add upstream https://github.com/DanB13/article-forge.git
git fetch upstream --tags
git merge <newest tag> --allow-unrelated-histories -X theirs
python .claude/skills/article-forge/scripts/scaffold_profile.py
```

## Updates arrive as pull requests

The `engine-update` workflow (`.github/workflows/engine-update.yml`) runs every
Monday in your repo. It runs `tools/engine_update.py`, which:

1. finds the newest **final release** upstream (a version tag such as `v1.3.1`),
   or, if you opted in, the newest **release candidate** (`v1.3.1-rc1`);
2. merges it on a branch named `engine-update/<tag>`;
3. refuses the update, and opens an issue instead, if it would change any file
   in `profile/` or `articles/`;
4. opens a pull request with that release's changelog.

If a merge conflicts, it opens an issue instead of a pull request. If an earlier
run pushed the branch but never opened the pull request, the next run opens it.

Merge engine update PRs with **Create a merge commit**, never *Squash and
merge* or *Rebase and merge*. The merge commit is how git knows which upstream
version you already have. Without it, the next update repeats old changes and
can conflict.

### Set it up once

1. **Settings > Actions > General > Workflow permissions**: tick *Allow GitHub
   Actions to create and approve pull requests*, then **Save**.
2. Create a fine-grained personal access token for your repo only, with
   **Contents** and **Workflows** set to *Read and write*. Save it in your repo
   as the secret `ENGINE_UPDATE_TOKEN` (**Settings > Secrets and variables >
   Actions**). The token only pushes the update branch: GitHub refuses workflow
   file changes from the default token. The workflow's own token opens the pull
   request.
3. Optional: to try release candidates before everyone else, add the
   repository **variable** `ENGINE_CHANNEL` with the value `rc` on the same page
   (Variables tab).

Check both settings at any time (needs the GitHub CLI, `gh`, signed in):

```bash
python .claude/skills/article-forge/scripts/check_setup.py
```

To update by hand: `git fetch upstream --tags && git merge <tag>`.

### Profile migrations

When a release changes the profile format, it ships a migration. The next time
you use the skill, Claude tells you what each waiting migration changes and asks
before running it. You can also run it yourself:

```bash
python .claude/skills/article-forge/scripts/migrate.py status       # what is waiting
python .claude/skills/article-forge/scripts/migrate.py plan         # the exact changes
python .claude/skills/article-forge/scripts/migrate.py apply --yes  # apply them
```

Migrations run in order, so skipping releases is safe. Before a file changes, a
copy goes to `profile/.backups/`.

### Undo an update

Every update is one merge commit, so it can be undone in one step:

- on GitHub: open the merged update pull request and click **Revert**, then
  merge the revert pull request; or
- locally: `git revert -m 1 <merge commit>` and push.

If the update also ran a migration, restore the files from `profile/.backups/`.

## Claude.ai users

1. Download the new release ZIP from the upstream repo's Releases page.
2. Settings > Capabilities > Skills: remove the old article-forge skill and
   upload the new ZIP.
3. Your Project knowledge (voice profile, corpus) is untouched.

## Version check

The skill ships a VERSION file. Ask Claude "what version of article-forge am I
running?" and compare it with the latest entry in `CHANGELOG.md`.

## Customising the engine

Keep personal rules in `profile/`; the skill always defers to your profile. If
you change engine files locally, git will flag conflicts on the next update.
Propose engine changes upstream as pull requests instead, with a spec (see
`specs/README.md`).
