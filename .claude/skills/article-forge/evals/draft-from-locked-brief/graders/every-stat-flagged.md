---
type: regex
target: { source: file, path: articles/ai-policy/draft.md }
pattern: "\\d+(\\.\\d+)?%(?![^.\\n]*\\[UNVERIFIED)"
match: not_contains
weight: 2
---
