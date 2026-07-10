# Phase 4 — Evidence verification (the phase most people skip)

Every statistic the article relies on gets a full provenance record before publish. This phase exists because real production runs have caught, in a single article: a headline stat misattributed to the wrong publisher AND carrying the wrong denominator; a vendor's arithmetic derivation of two other stats dressed up as primary research; a 2012 figure recycled as current-year data with the wrong geography; and four broken source URLs on publish day. Any one of these is fatal to a piece whose credibility rests on data.

## Per-statistic record (all seven required)

For each stat, establish and record in `articles/<slug>/evidence.md`:

1. **Originating report** — title, publisher, publication date. Not the place the stat was first seen.
2. **Exact original wording** — verbatim, no rounding, no paraphrase.
3. **Precise population/denominator** — and confirm it matches how the article uses it.
4. **Measured or derived** — if derived, either drop it or label it as derived in the article.
5. **Methodology and sample size.**
6. **A live, stable URL** — see link-stability rules below.
7. **Age check** — is it acceptable, and is a newer edition imminent?

## Failure patterns to actively expect

- **Misattribution chains**: vendor blog re-quotes a report; a second blog cites the first; the stat ends up credited to the re-quoter.
- **Derived stats sold as primary**: two real numbers multiplied together and published as a finding.
- **Population drift**: "97% of *breached* organisations" quietly becomes "97% of organisations" through repetition.
- **Zombie stats**: decade-old figures circulating with new dates.
- **Single-vendor market sizes presented as consensus**: check whether competing analysts publish materially different numbers.

**Heuristic: the more impressive and widely quoted a number is, the MORE suspicious you should be.** The most-shared numbers are the most laundered.

## Tooling (tiered: automatic first, escalate only what won't resolve)

Ordinary single searches find the stat; provenance means finding where it came from. Work each stat in tiers:

1. **Automatic agentic trace (do this yourself, no user action).** Fetch the page making the claim; follow its citation upstream; fetch THAT source; repeat until you reach the originating report; pull the report itself (or its press release) and confirm exact wording, denominator, methodology, and date. In Claude Code, parallelise across stats with subagents where available.
2. **Escalate the unresolved.** If the chain dead-ends, loops between secondary sources, or the "original" can't be reached, don't guess: hand the user a ready-made deep-research prompt (stat, every claimed source found, and the specific open question) to run through the platform's Research feature, then ingest the findings. Expect this for the most-laundered numbers only.
3. **Never** mark a stat verified on the strength of secondary coverage alone, however many secondary sources agree; agreement is how laundering looks.

## Recency refresh

Before publish, ask explicitly: "is there anything newer?" Maintain and check `profile/report-calendar.md` — the annual reports in the user's topic area and their usual publication months. If publishing within a few weeks of a major report's usual date, either publish before it lands or wait and refresh. A refresh has previously turned a closing *prediction* into a documented *fact*; it's worth the delay.

## Link stability rules

Verify every link resolves **on publish day**, not the day it was found. Stability by source type, best to worst:

- Big-vendor evergreen report pages, wire services (GlobeNewswire), major news outlets, Gartner/Microsoft newsroom: good to excellent.
- Vendor newsroom press releases: fragile — slugs change.
- Company newsrooms post-rebrand and acquired-company content: fragile to very fragile.

For dead primary sources, substitute in this order: wire-service press release in the publisher's own words → hosted PDF of the original report → reputable trade-press coverage quoting the figures.

## Output

`evidence.md` with the per-stat records, plus a **link map**: each URL paired with the exact phrase in the article it should be anchored to. Only now do stats lose their `[UNVERIFIED]` flags — and only now should the headline be finalised, since the two strongest verified numbers often become the headline.
