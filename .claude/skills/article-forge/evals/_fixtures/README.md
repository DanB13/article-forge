# Shared eval fixtures

Not an eval case (no prompt.md). `base/` is a small fictional author's repo:
Sam Carter, a product leader writing about workplace AI governance. All text,
people, companies and figures here are invented for testing.

Each case's `setup.sh` copies `base/` into the empty workspace, then the case's
own `resources/` on top, so a case only stores what it changes.
