# Third-party markdown theme CSS

Vendored styles for pluggable mission Brief / Debrief rendering. See `radspion.markdown_themes`.

| File | Source | License |
|------|--------|---------|
| `github-markdown-light.css` | [sindresorhus/github-markdown-css](https://github.com/sindresorhus/github-markdown-css) | MIT (`LICENSE-github-markdown-css`) |
| `github-markdown-dark.css` | [sindresorhus/github-markdown-css](https://github.com/sindresorhus/github-markdown-css) | MIT (`LICENSE-github-markdown-css`) |
| `latex.css` | [vincentdoerig/latex-css](https://github.com/vincentdoerig/latex-css) | MIT (`LICENSE-latex-css`) |
| `latex-scoped.css` | Generated from `latex.css` via `scripts/scope_latex_css.py` | MIT (same as LaTeX.css) |

Pygments stylesheets in `../pygments-*.css` are generated with `pygmentize -S STYLE -f html`.

Regenerate scoped LaTeX CSS after updating `latex.css`:

```bash
.venv/bin/python scripts/scope_latex_css.py
```
