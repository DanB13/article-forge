"""Steps for specs/019-package-and-secrets.feature."""

import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest
import yaml
from pytest_bdd import given, scenarios, then, when

import secret_scan

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".claude" / "skills" / "article-forge"
scenarios("../specs/019-package-and-secrets.feature")

# A skill-relative path in backticks or prose, not part of a longer path like articles/<slug>/assets/.
SKILL_PATH = re.compile(r"(?<![\w/<>.\-])((?:references|scripts|assets|migrations)/[A-Za-z0-9_.\-/]*[A-Za-z0-9_])")
PRIVATE_MARKERS = re.compile(r"(?i)(^local/|rory|style-packs/private)")


def mentioned_paths() -> set[str]:
    sources = [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]
    return {m.group(1) for f in sources for m in SKILL_PATH.finditer(f.read_text(encoding="utf-8"))}


@pytest.fixture
def pkg():
    return {}


@given("the engine repo")
def engine_repo(pkg):
    pkg["root"] = ROOT


@when("I build the skill ZIP")
def build_zip(pkg, tmp_path):
    assert shutil.which("zip"), "zip must be installed to build the skill ZIP"
    work = tmp_path / "repo"
    shutil.copytree(ROOT / ".claude", work / ".claude", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(ROOT / "tools", work / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    subprocess.run(["bash", str(work / "tools" / "package_skill.sh")], check=True, capture_output=True)
    with zipfile.ZipFile(next(work.glob("article-forge-skill-*.zip"))) as z:
        pkg["zip_names"] = set(z.namelist())


@then("every skill file that SKILL.md or a reference file mentions is in the ZIP")
def zip_complete(pkg):
    names = pkg["zip_names"]
    missing = [p for p in sorted(mentioned_paths())
               if f"article-forge/{p}" not in names and not any(n.startswith(f"article-forge/{p}/") for n in names)]
    assert missing == [], missing


@when("I read SKILL.md and the reference files")
def read_refs(pkg):
    pkg["mentioned"] = mentioned_paths()


@then("every skill file they mention exists")
def refs_exist(pkg):
    assert len(pkg["mentioned"]) > 5  # the scan itself works
    assert [p for p in sorted(pkg["mentioned"]) if not (SKILL / p).exists()] == []


@when("I list the files the engine repo tracks")
def tracked(pkg):
    pkg["tracked"] = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True,
                                    check=True).stdout.split()


@then("none is under local/ or names a private style pack")
def no_private(pkg):
    assert [p for p in pkg["tracked"] if PRIVATE_MARKERS.search(p)] == []


@when("I scan the tracked files for keys and tokens")
def scan_repo(pkg):
    pkg["findings"] = secret_scan.scan(secret_scan.tracked_files(ROOT))


@then("none is found")
def none_found(pkg):
    assert pkg["findings"] == []


@given("a file that holds a GitHub token")
def planted(pkg, tmp_path):
    p = tmp_path / "notes.md"
    p.write_text("My token is " + "ghp_" + "a1B2" * 9 + " for later.\n", encoding="utf-8")
    pkg["file"] = p


@when("I scan it for keys and tokens")
def scan_file(pkg):
    pkg["findings"] = secret_scan.scan([pkg["file"]])


@then("the token is reported")
def reported(pkg):
    assert any("GitHub token" in f for f in pkg["findings"]), pkg["findings"]


@given("the CI and release workflows")
def workflows(pkg):
    pkg["workflows"] = {n: yaml.safe_load((ROOT / ".github/workflows" / n).read_text(encoding="utf-8"))
                        for n in ("ci.yml", "release.yml")}


@then("each installs its test tools from requirements-dev.txt")
def installs_pinned(pkg):
    for name, wf in pkg["workflows"].items():
        runs = [s.get("run", "") for job in wf["jobs"].values() for s in job["steps"]]
        installs = [r for r in runs if "pip install" in r]
        assert installs and all("-r requirements-dev.txt" in r for r in installs), (name, installs)


@then("every package in requirements-dev.txt is pinned to one version")
def all_pinned(pkg):
    lines = [l.strip() for l in (ROOT / "requirements-dev.txt").read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.startswith("#")]
    assert lines and all(re.fullmatch(r"[A-Za-z0-9_.\-]+==[0-9][0-9A-Za-z.]*", l) for l in lines), lines
