"""Steps for specs/012-release.feature."""

import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest
from pytest_bdd import given, scenarios, then, when

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "article-forge"

scenarios("../specs/012-release.feature")


@pytest.fixture
def ctx():
    return {}


@given("the engine repo")
def engine_repo(ctx):
    ctx["root"] = ROOT


@when("I read the skill VERSION, the plugin manifest and the CHANGELOG")
def read_versions(ctx):
    ctx["version"] = (SKILL / "VERSION").read_text(encoding="utf-8").strip()
    ctx["manifest"] = json.loads((SKILL / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    top = re.search(r"^## v(\d+\.\d+\.\d+)", (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
    ctx["changelog"] = top.group(1) if top else None


@then("all three name the same version")
def same_version(ctx):
    assert ctx["version"] == ctx["manifest"] == ctx["changelog"], (ctx["version"], ctx["manifest"], ctx["changelog"])


@when("I build the skill ZIP")
def build_zip(ctx, tmp_path):
    assert shutil.which("zip"), "zip must be installed to build the skill ZIP"
    work = tmp_path / "repo"
    shutil.copytree(ROOT / ".claude", work / ".claude")
    shutil.copytree(ROOT / "tools", work / "tools")
    subprocess.run(["bash", str(work / "tools" / "package_skill.sh")], check=True, capture_output=True)
    ctx["zip"] = next(work.glob("article-forge-skill-*.zip"))


@then("the ZIP holds SKILL.md under an article-forge folder")
def has_skill(ctx):
    with zipfile.ZipFile(ctx["zip"]) as z:
        assert "article-forge/SKILL.md" in z.namelist()


@then("the ZIP holds no file from the evals folder")
def no_evals(ctx):
    with zipfile.ZipFile(ctx["zip"]) as z:
        assert not [n for n in z.namelist() if n.startswith("article-forge/evals/")]
