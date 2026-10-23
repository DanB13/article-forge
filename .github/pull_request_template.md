## What and why

<!-- One or two sentences: what changes, and which spec it serves. -->

## Definition of done

- [ ] The maintainer approved the scenarios before the build (new or changed specs)
- [ ] `python tools/check_specs.py` and `pytest` pass locally; CI is green
- [ ] Any change to a released test (scenario wording, grader, case, fixture, step file, pass rules) has a record in `specs/test-changes.yaml`
- [ ] No scenario or eval case removed without a retire record in `specs/retired.yaml`
- [ ] If the engine changed: the affected eval cases ran (or the full T2 run, for a release)
- [ ] CHANGELOG and CAPABILITIES updated (not needed for docs-only changes)

## Grader, test or fixture changes

<!-- None, or each change with its reason. -->

## Merge with

- Feature PRs on the public repo: **Squash and merge**
- Engine update PRs in a writer's repo: **Create a merge commit**
