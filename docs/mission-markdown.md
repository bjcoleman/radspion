# Mission markdown (Brief / Debrief)

The app uses **[Python-Markdown](https://python-markdown.github.io/)** (`markdown` on PyPI), not Mistune. For coursework write-ups with **fenced code blocks** (triple backticks), including blocks inside numbered or bulleted lists, enable:

- `markdown.extensions.fenced_code` — ``` blocks between paragraphs
- `markdown.extensions.sane_lists` — stable list numbering when items have multiple blocks
- `markdown.extensions.tables` — optional pipe tables

**List + code:** In CommonMark, a fenced block inside a list item must be indented to the **content column** of that item (typically four spaces past the list marker). Example:

```markdown
1. Run diagnostics:

   ```bash
   git status
   ```

2. Continue with the next step.
```

Mistune and minimal converters often break nested fences or list numbering; Python-Markdown with `sane_lists` is the recommended default for this project.

Mission files live under `content/missions/` (live) and `content/samples/` (example packs). See [content/README.md](../content/README.md).
