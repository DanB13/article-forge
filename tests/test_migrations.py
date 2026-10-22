"""Steps for specs/015-migrations.feature: scripts/migrate.py with sample migrations."""

import shutil
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

import check_profile
import migrate
import scaffold_profile

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
ENGINE_MIGRATIONS = ROOT / ".claude" / "skills" / "article-forge" / "migrations"
scenarios("../specs/015-migrations.feature")


def files(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


@pytest.fixture
def mig(tmp_path):
    return {"root": tmp_path, "dirs": []}


def _ids(text: str) -> list[str]:
    return [x.strip() for x in text.split(",")]


@given("a writer's profile with no migration record")
def profile_no_record(mig):
    shutil.copytree(FIXTURES / "profiles" / "v1.3.0" / "profile", mig["root"] / "profile")
    mig["voice_before"] = (mig["root"] / "profile/voice-profile.md").read_text(encoding="utf-8")


@given(parsers.parse('a profile from engine version "{version}"'))
def profile_from(mig, version):
    shutil.copytree(FIXTURES / "profiles" / f"v{version}" / "profile", mig["root"] / "profile")


@given(parsers.parse('sample migrations "{ids}", where each builds on the one before'))
def samples(mig, ids):
    mig["dirs"] = [FIXTURES / "migrations"]
    assert [m.id for m in migrate.discover(mig["root"], mig["dirs"])] == _ids(ids)


@when("the writer approves and the migrations run")
def run_yes(mig):
    mig["lines"], mig["changed"] = migrate.apply(mig["root"], migrate.discover(mig["root"], mig["dirs"]), yes=True)


@when("the writer approves and the engine's and the sample migrations run")
def run_engine_and_samples(mig):
    mig["dirs"] = [ENGINE_MIGRATIONS, *mig["dirs"]]
    run_yes(mig)


@when("the migrations run without approval")
def run_no(mig):
    mig["before"] = files(mig["root"])
    mig["lines"], mig["changed"] = migrate.apply(mig["root"], migrate.discover(mig["root"], mig["dirs"]), yes=False)


@when("the writer approves and the migrations run twice")
def run_twice(mig):
    run_yes(mig)
    mig["after_first"] = files(mig["root"])
    mig["lines2"], mig["changed2"] = migrate.apply(mig["root"], migrate.discover(mig["root"], mig["dirs"]), yes=True)


@when("I ask which migrations are waiting")
def ask_waiting(mig):
    mig["waiting"] = [m.id for m in migrate.waiting(mig["root"], migrate.discover(mig["root"], mig["dirs"]))]


@then(parsers.parse('"{ids}" are recorded as applied, in that order'))
def recorded(mig, ids):
    assert [a["id"] for a in migrate.read_record(mig["root"])] == _ids(ids)


@then("the profile shows the change from each migration")
def shows_changes(mig):
    voice = (mig["root"] / "profile/voice-profile.md").read_text(encoding="utf-8")
    context = (mig["root"] / "profile/context.md").read_text(encoding="utf-8")
    assert "## Density limits" in voice and "contrast per section" in voice
    assert "Density limits reviewed after migration 0002." in context


@then("the proposed changes are shown")
def shown(mig):
    text = "\n".join(mig["lines"])
    assert "+## Density limits" in text and "contrast per section" in text and "0003" in text, text


@then("no file is changed")
def unchanged(mig):
    assert files(mig["root"]) == mig["before"]


@then("the second run changes no file")
def second_run(mig):
    assert mig["changed2"] == [] and files(mig["root"]) == mig["after_first"]


@then(parsers.parse('"{ids}" are waiting'))
def are_waiting(mig, ids):
    assert mig["waiting"] == _ids(ids)


@then("the profile passes the profile check")
def profile_ok(mig):
    assert check_profile.problems(mig["root"]) == []


@then("no migration is waiting")
def none_waiting(mig):
    assert migrate.waiting(mig["root"], migrate.discover(mig["root"], mig["dirs"])) == []


@then("a backup holds the voice profile as it was before")
def backup(mig):
    copies = sorted((mig["root"] / migrate.BACKUPS).glob("*-0001/profile/voice-profile.md"))
    assert copies and copies[0].read_text(encoding="utf-8") == mig["voice_before"]


@given("an empty repo")
def empty_repo(mig, monkeypatch, tmp_path):
    # Point the engine at the sample migrations, so a fresh profile has something to mark.
    skill = tmp_path / "skill"
    shutil.copytree(FIXTURES / "migrations", skill / "migrations")
    monkeypatch.setattr(migrate, "SKILL_DIR", skill)
    mig["root"] = tmp_path / "repo"
    mig["root"].mkdir()


@when("I run the profile scaffold")
def run_scaffold(mig):
    scaffold_profile.scaffold(mig["root"])


@then("no engine migration is waiting")
def no_engine_waiting(mig):
    assert (mig["root"] / migrate.RECORD).exists()
    assert len(migrate.read_record(mig["root"])) == 3
    assert migrate.waiting(mig["root"], migrate.discover(mig["root"])) == []
