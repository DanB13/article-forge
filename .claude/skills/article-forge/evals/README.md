# Behaviour evals

Each folder is one eval case for `claude plugin eval`, used by one or more
`@eval:<case>` scenarios in `specs/`. `_fixtures/base/` is a small fictional
author's repo that every case's `setup.sh` copies in first.

| Case | Spec | Checks |
|---|---|---|
| brief-ambiguous-asks | 004 | Rule 1: questions, not a draft, on an ambiguous theme |
| draft-from-locked-brief | 004, 006 | Full first draft in one pass; stats flagged; mechanics applied |
| edit-asks-intent | 005 | Rule 2: no silent edit; asks intent or offers options |
| user-rewrite-kept | 005 | Rule 4: the writer's line goes in word for word |
| provenance-subcut | 002 | A breakdown claim gets its own record and is rejected |
| provenance-secondary-only | 006 | Secondary-only stat not verified; derived number labelled |
| voice-edit-mechanics | 007 | Em dashes and banned words removed; contrasts capped; nothing invented |
| retro-proposes-not-applies | 008 | Profile changes proposed, never applied; piece archived |
| imagery-real-first | 009 | Rule 6: real material first |
| confirm-lived-facts | 011 | Rule 5: the writer's role is not inflated |
| edit-rounds-separate | 011 | Rule 7: fact fix and style rewrite in separate rounds |
| onboarding-keeps-existing-profile | 001 | Onboarding never overwrites a filled-in profile |

## Run

From the repo root (every run is a real model call on your plan or API key):

```bash
claude plugin eval .claude/skills/article-forge --scaffold --allow-tools Bash Write Edit \
  --threshold 0.8 --max-cost-usd 10
```

- `--scaffold` runs each case's `setup.sh`.
- `--allow-tools` grants the write tools the skill needs.
- One cheap run of one case: add `--case <name> --runs 1 --ablation none`.

Every fixture is invented (Sam Carter, Acme Research, TechNewsDaily), so the
cases are stable and hold no third-party text.
