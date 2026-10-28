"""Steps for specs/014-upgrade-safety.feature: tools/engine_update.py on throwaway git repos."""

import subprocess
from pathlib import Path

import pytest
import yaml
from pytest_bdd import given, parsers, scenarios, then, when

import engine_update

ROOT = Path(__file__).resolve().parents[1]
scenarios("../specs/014-upgrade-safety.feature")

WRITER_FILES = {
    "profile/voice-profile.md": "# Voice Profile\nMY OWN RULES\n",
    "profile/context.md": "# Author Context\nI write about MSPs.\n",
    "articles/my-piece/draft.md": "# My piece\nA line only I would write.\n",
}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout


def write(repo: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def snapshot(repo: Path, folders=("profile", "articles")) -> dict[str, bytes]:
    return {p.relative_to(repo).as_posix(): p.read_bytes()
            for f in folders for p in sorted((repo / f).rglob("*")) if p.is_file()}


def engine_files(version: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    files = {
        ".claude/skills/article-forge/VERSION": version + "\n",
        ".claude/skills/article-forge/SKILL.md": f"# Article Forge {version}\n",
        "CHANGELOG.md": f"# Changelog\n\n## v{version}\n\n- Release {version}.\n",
        "tools/engine_update.py": "# tool\n",
    }
    files.update(extra or {})
    return files


@pytest.fixture
def world(tmp_path, monkeypatch):
    for k, v in {"GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "t@example.com",
                 "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "t@example.com"}.items():
        monkeypatch.setenv(k, v)
    up = tmp_path / "upstream"
    up.mkdir()
    git(up, "init", "-q", "-b", "main")
    return {"tmp": tmp_path, "upstream": up, "pending": [], "pr_open": False}


def release(world, tag: str, extra: dict[str, str] | None = None, remove: tuple[str, ...] = ()) -> None:
    up = world["upstream"]
    for rel in remove:
        (up / rel).unlink()
    write(up, engine_files(tag[1:], extra))
    git(up, "add", "-A")
    git(up, "commit", "-q", "-m", f"Release {tag}")
    git(up, "tag", tag)


def run_update(world):
    return engine_update.run(world["writer"], str(world["upstream"]), "release",
                             pr_is_open=lambda repo, branch: world["pr_open"])


@given(parsers.parse('a writer\'s repo made from engine release "{tag}", with a filled-in profile and an article'))
def writer_repo(world, tag):
    release(world, tag, {"README.md": "Engine readme\n"})
    origin = world["tmp"] / "origin.git"
    git(world["tmp"], "init", "-q", "--bare", "-b", "main", str(origin))
    writer = world["tmp"] / "writer"
    writer.mkdir()
    git(writer, "init", "-q", "-b", "main")
    # A template copy: the engine files without upstream's history, plus the writer's own work.
    for rel in git(world["upstream"], "ls-files").split():
        (writer / rel).parent.mkdir(parents=True, exist_ok=True)
        (writer / rel).write_bytes((world["upstream"] / rel).read_bytes())
    write(writer, WRITER_FILES)
    git(writer, "add", "-A")
    git(writer, "commit", "-q", "-m", "Initial commit from template")
    git(writer, "remote", "add", "origin", str(origin))
    git(writer, "push", "-q", "origin", "main")
    world["writer"] = writer
    world["before"] = snapshot(writer)


@given(parsers.parse('newer engine releases "{a}" and "{b}"'))
def newer_releases(world, a, b):
    world["pending"] = [
        (a, {".claude/skills/article-forge/references/new.md": "New reference\n"}, ("README.md",)),
        (b, {".claude/skills/article-forge/SKILL.md": "# Article Forge, rewritten\n"}, ()),
    ]


@given(parsers.re(r'a newer engine release "(?P<tag>[^"]+)" that adds "(?P<path>[^"]+)"'))
def release_touching_profile(world, tag, path):
    release(world, tag, {path: "UPSTREAM DEFAULTS\n"})


@given(parsers.re(r'a newer engine release "(?P<tag>[^"]+)"$'))
def newer_release(world, tag):
    release(world, tag)


@given(parsers.parse('the update branch for "{tag}" was pushed but no pull request is open'))
def half_done(world, tag):
    result = run_update(world)
    assert result.action == "open_pr", result.message
    git(world["writer"], "checkout", "-q", "main")
    world["branch_sha"] = git(world["writer"], "ls-remote", "origin", f"refs/heads/engine-update/{tag}").split()[0]


@when("the engine update runs after each release, and the writer merges each update")
def update_each(world):
    for tag, extra, remove in world["pending"]:
        release(world, tag, extra, remove)
        result = run_update(world)
        assert result.action == "open_pr", result.message
        git(world["writer"], "checkout", "-q", "main")
        git(world["writer"], "merge", "-q", "--no-ff", "--no-edit", result.branch)
    world["last_tag"] = world["pending"][-1][0]


@when("the engine update runs")
def update_once(world):
    world["result"] = run_update(world)


@then("the writer's profile/ and articles/ are byte-identical to before")
def untouched(world):
    assert snapshot(world["writer"]) == world["before"]


@then(parsers.parse('the engine files match release "{tag}"'))
def engine_matches(world, tag):
    diff = git(world["writer"], "diff", "--name-only", tag, "HEAD", "--", ".", ":!profile", ":!articles")
    assert diff.strip() == "", diff


@then("no update branch is pushed")
def nothing_pushed(world):
    assert world["result"].action == "refused", world["result"].message
    assert git(world["writer"], "ls-remote", "--heads", "origin", "engine-update/*").strip() == ""


@then(parsers.parse('it reports "{path}" as a refused file'))
def refused_file(world, path):
    assert path in world["result"].files


@then("it asks for a pull request for that branch")
def asks_for_pr(world):
    r = world["result"]
    assert (r.action, r.branch) == ("open_pr", "engine-update/v1.1.0"), r


@then("it pushes nothing new")
def no_new_push(world):
    now = git(world["writer"], "ls-remote", "origin", "refs/heads/engine-update/v1.1.0").split()[0]
    assert now == world["branch_sha"]


@given("the engine repo")
def engine_repo():
    pass


@when("I list the files the engine repo tracks")
def tracked(world):
    world["tracked"] = git(ROOT, "ls-files").split()


@then("none is under profile/ or articles/")
def no_writer_folders(world):
    assert [p for p in world["tracked"] if p.startswith(("profile/", "articles/"))] == []


@given("the engine-update workflow")
def workflow(world):
    world["wf"] = yaml.safe_load((ROOT / ".github/workflows/engine-update.yml").read_text(encoding="utf-8"))


def _step(world, name):
    return next(s for s in world["wf"]["jobs"]["update"]["steps"] if s.get("name", "").startswith(name))


@then("the step that opens the pull request uses the workflow's own token")
def pr_step_token(world):
    assert _step(world, "Open pull request")["env"]["GH_TOKEN"] == "${{ github.token }}"


@then("the step that opens the pull request calls the REST pulls endpoint, not gh pr create")
def pr_step_rest(world):
    run = _step(world, "Open pull request")["run"]
    assert 'gh api "repos/${{ github.repository }}/pulls"' in run and "gh pr create" not in run


@then("it uses the workflow's own token")
def pr_step_own_token(world):
    pr_step_token(world)


@then("a step runs only when opening the pull request failed")
def fallback_condition(world):
    pr = _step(world, "Open pull request")
    assert pr.get("continue-on-error") is True and pr.get("id") == "pr"
    assert _step(world, "If the pull request could not be opened")["if"] == "steps.pr.outcome == 'failure'"


@then("that step opens an issue whose body links to the compare page for the update branch")
def fallback_issue(world):
    run = _step(world, "If the pull request could not be opened")["run"]
    assert "gh issue create" in run and "/compare/${BASE}...${BRANCH}?expand=1" in run


@then("that step makes the run fail")
def fallback_fails(world):
    assert _step(world, "If the pull request could not be opened")["run"].rstrip().endswith("exit 1")


@then("only the checkout uses the ENGINE_UPDATE_TOKEN secret")
def only_checkout(world):
    job = world["wf"]["jobs"]["update"]
    users = [s.get("name") or s.get("uses") for s in job["steps"] if "ENGINE_UPDATE_TOKEN" in yaml.safe_dump(s)]
    assert users == ["actions/checkout@v4"], users
    assert "ENGINE_UPDATE_TOKEN" not in yaml.safe_dump(job.get("env", {}))


@given(parsers.parse('a newer engine release "{tag}" that changes a workflow file'))
def release_changing_workflow(world, tag):
    release(world, tag, {".github/workflows/ci.yml": "name: ci\n# changed upstream\n"})


@when("the engine update runs without the ENGINE_UPDATE_TOKEN secret")
def update_without_token(world):
    # GitHub refuses a push that changes workflow files unless the token allows it.
    hook = world["tmp"] / "origin.git" / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\nwhile read old new ref; do\n"
                    "  if git diff --name-only refs/heads/main \"$new\" | grep -q '^.github/workflows/'; then\n"
                    "    echo 'refusing to allow an app to update workflows' >&2; exit 1; fi\n"
                    "done\n", encoding="utf-8")
    hook.chmod(0o755)
    world["result"] = run_update(world)


@then("no branch is pushed, because the token is missing")
def nothing_pushed_needs_token(world):
    assert world["result"].action == "needs_token", world["result"].message
    assert ".github/workflows/ci.yml" in world["result"].files
    assert git(world["writer"], "ls-remote", "--heads", "origin", "engine-update/*").strip() == ""


@then(parsers.parse('it asks for the manual-merge issue for "{tag}"'))
def asks_manual_issue(world, tag):
    assert (world["result"].action, world["result"].tag) == ("needs_token", tag)


@then("a step runs only when the update needs the token")
def needs_token_condition(world):
    assert _step(world, "If the update needs the token")["if"] == "steps.update.outputs.action == 'needs_token'"


@then("that step opens an issue whose body gives the git commands to merge the release by hand")
def needs_token_issue(world):
    run = _step(world, "If the update needs the token")["run"]
    assert "gh issue create" in run
    assert all(c in run for c in ("git fetch upstream --tags", "git merge %s", "git push -u origin"))


@then("that step marks the run with a warning, not a failure")
def needs_token_warns(world):
    run = _step(world, "If the update needs the token")["run"]
    assert "::warning::" in run and "exit 1" not in run
