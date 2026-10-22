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

## Why the first update is different

A repo created with **Use this template** starts with its own first commit. It
shares no history with upstream, so a plain `git merge` stops with
`refusing to merge unrelated histories`. You need one merge with the flag. That
merge links the two histories, and every later update is an ordinary merge.

You cannot use a GitHub fork instead: a fork of a public repository is always
public, and your profile and drafts would be visible.

## One-time setup (Claude Code / git users)

```bash
git remote add upstream https://github.com/DanB13/article-forge.git
git fetch upstream
git merge upstream/main --allow-unrelated-histories -X theirs
```

Why `-X theirs`: with no shared history, git sees every engine file that
differs between your copy and upstream as an add/add conflict. `-X theirs`
resolves those in favour of upstream, which owns the engine. Your `profile/` and
`articles/` are not affected, because upstream does not ship them. (Tested on a
real v1.1 copy: zero conflicts, profile unchanged byte for byte.) If you had
edited engine files yourself, those edits are replaced; move personal rules into
`profile/` first. Or ask Claude Code to do the merge for you.

Use `-X theirs` for this first merge only. Later merges are normal, so git will
flag any real conflict instead of choosing for you.

Run the scaffold once afterwards. It adds any new template files and keeps
everything you already have:

```bash
python .claude/skills/article-forge/scripts/scaffold_profile.py
```

## After that: updates arrive as pull requests

The `engine-update` workflow (`.github/workflows/engine-update.yml`) runs every
Monday in your repo. When upstream has new commits it merges them on a branch
named `engine-update/v<version>-<sha>` and opens a pull request with the
changelog. You review and merge it in GitHub. If the merge conflicts, it opens
an issue instead.

Merge engine update PRs with **Create a merge commit**, never *Squash and
merge* or *Rebase and merge*. The merge commit is how git knows which upstream
version you already have. Without it, the next update repeats old changes and
can conflict.

Enable it once in your repo: **Settings > Actions > General > Workflow
permissions**: choose *Read and write permissions* and tick *Allow GitHub
Actions to create and approve pull requests*.

Updates that change `.github/workflows/` need a token with the Workflows
permission, because GitHub's default token may not push workflow changes. Add a
fine-grained personal access token (Contents, Pull requests and Workflows: read
and write, for your repo only) as the `ENGINE_UPDATE_TOKEN` secret.

To update by hand at any time: `git fetch upstream && git merge upstream/main`.

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
