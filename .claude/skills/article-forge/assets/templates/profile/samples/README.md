# Your writing samples

Your own unaided writing: the reference the "is it me?" meter measures drafts
against. Add one file per source. Each sample starts with a header:

```
---
kind: written            # written, spoken (a transcript of you talking), or description
source: "LinkedIn article"
date: 2020-09
register: article        # for example article, work message, podcast
published: true          # only published text is ever sent to an outside detector
human_only: true         # written without AI help
---
The text, word for word.
```

- Only `written` samples judge rhythm. `spoken` samples count for phrasing only.
- A `description` (a summary of your style) is kept for reference, never measured.
- Replace names and private details with placeholders such as [PERSON] or [CUSTOMER];
  the meters ignore them.
- `fingerprint.md` (optional) lists your signature phrases and phrases to leave out:

```
---
signature_phrases: [have a crack, fair play]
leave_out: [I mean, you know]
---
```

Check what is used: `python .claude/skills/article-forge/scripts/samples.py`
