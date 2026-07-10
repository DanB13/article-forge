# Phase 2 — Research

Goal: test whether the thesis has evidence behind it, and stock the larder. Nothing collected here is trusted yet.

## Process

1. **Broad searches first** to test the thesis. If the evidence is thin or contradicts the argument, tell the user now, before a draft exists.
2. **Verify every anchor fact** the user supplied before it goes near a draft (e.g. "has that vulnerability been patched since?" — checking mid-process has previously turned a would-be inaccuracy into a better line).
3. **Collect more statistics than will be used**; selection is for narrative fit later, not volume. Record each stat WITH its claimed source, and mark every one `[UNVERIFIED]`.
4. **Prefer primary sources** (IBM, PwC, Gartner, Zscaler, Netskope, government/CISA, peer-reviewed) over aggregators — but even "primary-looking" citations get full provenance checks in Phase 4.
5. **If the article uses a historical parallel**, find contemporary evidence from the era (period articles, surveys from the time). That's what makes an analogy feel researched rather than asserted.
6. **Hunt for one authentic human artefact** — a Reddit/forum thread, a quote from practice, a real screenshot. These outperform analyst quotes for authenticity every time. Ask the user if they've seen one; their finds are usually the best.
7. **Check the user's own back catalogue** (past conversation search / their corpus in `profile/corpus/`) for prior articles to reference or build on.

## Output

`articles/<slug>/research.md`: candidate stats table (claim, claimed source, URL, why it might fit), anchor-fact checks, historical evidence, human artefacts, internal references. All stats flagged `[UNVERIFIED]`.

## Tooling note

Ordinary web search finds a stat; it rarely finds where the stat actually came from. Full provenance tracing happens in Phase 4 and may need the platform's deep-research capability — don't pretend a single search settled a number's origin.
