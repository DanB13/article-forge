"""Sample migration for spec 015: needs 0001's section, so it proves the order."""
from pathlib import Path

ID = "0002"
DESCRIPTION = "Adds the contrast limit under '## Density limits'"
VOICE = "profile/voice-profile.md"
LINE = "- At most one 'X, not Y' contrast per section"


def plan(root: Path) -> dict[str, str]:
    text = (root / VOICE).read_text(encoding="utf-8")
    if LINE in text:
        return {}
    if "## Density limits" not in text:
        raise RuntimeError("0002 needs the '## Density limits' section that 0001 adds")
    return {VOICE: text.replace("## Density limits\n", f"## Density limits\n{LINE}\n", 1)}
