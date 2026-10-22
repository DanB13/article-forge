"""A private migration the writer has not run yet (fixture for spec 015-08)."""
from pathlib import Path

ID = "L0001"
DESCRIPTION = "Adds a '## Headlines' section with the writer's headline rules to the voice profile"
VOICE = "profile/voice-profile.md"
SECTION = "## Headlines\n- Under 70 characters\n- A verb in every headline\n"


def plan(root: Path) -> dict[str, str]:
    text = (root / VOICE).read_text(encoding="utf-8")
    if "## Headlines" in text:
        return {}
    return {VOICE: text.rstrip("\n") + "\n\n" + SECTION}
