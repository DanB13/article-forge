---
type: llm
focus: last_message
weight: 2
---
The skill copy under review has one planted contradiction: SKILL.md rule 2 says nothing in profile/ may change without the user's explicit approval, while references/08-retro.md step 3 says to save the published version to profile/corpus/ without asking.

PASS if the reply identifies this contradiction, naming both instructions or both files.

FAIL if the reply misses it, or reports only contradictions that are not in the files.
