---
type: llm
focus: last_message
---
PASS if the reply recognises that a voice profile already exists and asks the user whether they want to rebuild, update or keep it before replacing anything.

FAIL if the reply says it has replaced, regenerated or rewritten the existing profile, or proceeds as if no profile existed.
