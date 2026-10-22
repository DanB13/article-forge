"""Sample migration for spec 015: adds a section."""
from pathlib import Path

ID = "0001"
DESCRIPTION = "Adds a '## Density limits' section to the voice profile"
VOICE = "profile/voice-profile.md"


def plan(root: Path) -> dict[str, str]:
    text = (root / VOICE).read_text(encoding="utf-8")
    if "## Density limits" in text:
        return {}
    return {VOICE: text.rstrip("\n") + "\n\n## Density limits\n"}
