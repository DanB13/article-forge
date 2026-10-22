---
type: llm
focus: last_message
weight: 2
---
PASS if the reply handles the survey-size correction as its own change, and treats the "punchier" request as a separate style round: it proposes options, asks what "punchier" should mean, or says it will do the style pass next, rather than rewriting the whole draft for style in the same pass as the fact fix.

FAIL if the reply reports that it fixed the fact and rewrote the whole draft for style in one combined pass.
