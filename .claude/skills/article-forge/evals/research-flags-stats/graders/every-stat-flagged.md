---
type: regex
target:
  source: file
  path: articles/four-day-week/research.md
pattern: ^(?![^\n]*UNVERIFIED)[^\n]*\d+(\.\d+)?%[^\n]*$
flags: m
match: not_contains
---
