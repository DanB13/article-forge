"""Sample migration for spec 015: needs 0002's line."""
from pathlib import Path

ID = "0003"
DESCRIPTION = "Notes in context.md that the density limits were reviewed"
VOICE = "profile/voice-profile.md"
CONTEXT = "profile/context.md"
NOTE = "Density limits reviewed after migration 0002."


def plan(root: Path) -> dict[str, str]:
    if "contrast per section" not in (root / VOICE).read_text(encoding="utf-8"):
        raise RuntimeError("0003 needs the line that 0002 adds")
    text = (root / CONTEXT).read_text(encoding="utf-8")
    if NOTE in text:
        return {}
    return {CONTEXT: text.rstrip("\n") + f"\n\n{NOTE}\n"}
