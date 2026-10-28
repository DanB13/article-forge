---
type: regex
target:
  source: file
  path: articles/ai-policy/draft.md
pattern: "(?:(rattle\\ the\\ cabinet|for\\ what\\ it['\u2019]s\\ worth|honest\\ answer|fair\\ question|here['\u2019]s\\ the\\ thing)[\\s\\S]*?){4}"
flags: i
match: not_contains
---
