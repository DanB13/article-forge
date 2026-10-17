# Behaviour evals

Each folder is one eval case for `claude plugin eval`. Each case maps to an
`@eval:<case>` scenario in `specs/`.

| Case | Spec | Checks |
|---|---|---|
| provenance-subcut | 002 | A breakdown claim gets its own record and is rejected when the source measures something else |
| onboarding-keeps-existing-profile | 001 | Onboarding never overwrites a filled-in profile |

## Run

From the repo root (each run is a real model call and uses your plan or API credit):

```bash
claude plugin eval .claude/skills/article-forge --scaffold --allow-tools Bash Write Edit \
  --threshold 0.8 --max-cost-usd 10
```

- `--scaffold` runs each case's `setup.sh`, which copies `resources/` into the empty workspace.
- `--allow-tools` grants the write tools the skill needs; without it they are removed.
- Iterate on one case cheaply: add `--case provenance-subcut --runs 1 --ablation none`.

Fixtures are synthetic (fictional "Acme Research"), so they are stable and
free of third-party text.
