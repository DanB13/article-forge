# Migrations

A migration changes the files in a writer's `profile/` when the engine's profile
format changes. `scripts/migrate.py` runs the waiting ones in number order, only
after the writer approves, and backs up every file first.

Add one as `NNNN_short_name.py` with:

```python
from pathlib import Path

ID = "0102"
DESCRIPTION = "Adds a '## Density limits' section to the voice profile"

def plan(root: Path) -> dict[str, str]:
    """Return {relative path: new content}. Return {} when nothing needs to change,
    so that running it again is safe."""
```

Rules:
- Never delete the writer's words. Add, rename or move; keep their text.
- `plan` must return `{}` once its change is present (it must be safe to run twice).
- Add the profile your migration expects to `tests/fixtures/profiles/` and keep
  the upgrade matrix in spec 015 passing.

Engine migrations are numbered from 0101 (0001 to 0099 are kept for the test
samples in `tests/fixtures/migrations/`).

| ID | Release | Change |
|---|---|---|
| 0101 | v1.4 | Adds `profile/settings.yaml` and `profile/samples/` |
