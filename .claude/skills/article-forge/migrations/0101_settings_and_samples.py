"""Adds profile/settings.yaml and the profile/samples/ folder (v1.4, spec 028-07)."""
from pathlib import Path

ID = "0101"
DESCRIPTION = "Adds profile/settings.yaml (informality dial, allowed words, optional modules) and profile/samples/"

TEMPLATES = Path(__file__).resolve().parents[1] / "assets" / "templates" / "profile"
FILES = {"profile/settings.yaml": TEMPLATES / "settings.yaml",
         "profile/samples/README.md": TEMPLATES / "samples" / "README.md"}


def plan(root: Path) -> dict[str, str]:
    """Only files that do not exist yet; an existing file is never changed."""
    return {rel: src.read_text(encoding="utf-8") for rel, src in FILES.items() if not (root / rel).exists()}
