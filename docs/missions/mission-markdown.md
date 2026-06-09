# Mission markdown (Brief / Debrief)

The app uses **[Python-Markdown](https://python-markdown.github.io/)** with **[PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)** (`pymdown-extensions`, `Pygments` on PyPI):

- `pymdownx.highlight` + `pymdownx.superfences` — fenced code (including inside lists), optional syntax highlighting when a language is given
- `markdown.extensions.sane_lists` — stable list numbering when items have multiple blocks
- `markdown.extensions.tables` — pipe tables

## Code blocks

Use triple backticks. Add a language tag (e.g. `python`, `bash`, `json`) when you want syntax highlighting; a bare fence renders as plain monospace with no highlighting.

**At document root**, fences start at column 0:

````markdown
```python
print("hello")
```
````

**Inside a list item**, indent the fence and its contents to the list **content column** (typically four spaces after the list marker). The same applies to images, tables, and paragraphs that belong to that item.

````markdown
* Step one

    ```python
    print("hello")
    ```

* Step two
````

Classic **indented code blocks** (extra four spaces per line, no backticks) still work and are valid Markdown; fences are preferred for mission briefs.

Each mission pack stores prose in `{slug}/brief.md` and `{slug}/debrief.md`. Images in markdown must use external `https://` URLs (not repo-local paths).

## Presenting data for submission

When a brief tells agents to submit **data**, show the exact payload in a fenced code block so they can copy it. The value in `storyline.yaml` `completion_data` must match **byte-for-byte** (including line breaks and indentation after the opening `[` or `{`).

For multi-line JSON or other structured data:

- Author the canonical string in YAML with a `|` block (see [authoring-guide.md](authoring-guide.md)).
- Paste the same formatting into the brief code fence.
- Tell agents to submit the exact data, including line breaks.

## Clearance in prose

When a brief mentions a **clearance code**, use the same string as `clearance_code` in YAML. QR codes link to the same clearance flow.

## Collapsible sections

Append ` ???` (space + three question marks) to a `##` or `###` heading to collapse that section in the app. In a plain markdown editor the heading still renders normally, with `???` visible at the end.

**Rules:**

- Only `##` and `###` headings may use ` ???`.
- Section body runs until the next heading of the **same or higher** level, a `---` line, or end of file.
- `---` always ends the current section and is rendered as a horizontal rule.
- Nested collapsibles are not allowed (use `---` or an intervening `##` heading between collapsible blocks).

**Example — fieldwork gated until ready:**

```markdown
## Read this now

Visible introduction.

## Read when ready ???

Instructions agents should open later.

---

To complete this mission, submit …
```

**Example — hints after a segment break:**

```markdown
## Fieldwork ???

Main puzzle instructions.

---

### Hint 1 ???

First hint.

### Hint 2 ???

Second hint.

---

Submit line (always visible).
```

`seed_storyline PACK --check` validates collapsible structure in brief and debrief files.
