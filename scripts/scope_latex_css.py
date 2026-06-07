"""Scope a vendor stylesheet to .mission-markdown.latex-document."""

from __future__ import annotations

from pathlib import Path


def split_selectors(selector_text: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for ch in selector_text:
        if ch == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth = max(0, depth - 1)
        current.append(ch)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


def scope_selector(selector: str, prefix: str) -> str:
    selector = selector.strip()
    if not selector:
        return selector
    if selector.startswith("@"):
        return selector
    if selector in {"from", "to"}:
        return selector
    if selector == "body":
        return prefix
    if selector.startswith("body "):
        return prefix + selector[4:]
    if selector.startswith("body:"):
        return prefix + selector[4:]
    if selector == "html":
        return prefix
    if selector.startswith(":root"):
        return prefix
    return f"{prefix} {selector}"


def scope_rule(rule: str, prefix: str) -> str:
    brace = rule.find("{")
    if brace == -1:
        return rule
    selectors = split_selectors(rule[:brace])
    scoped = ", ".join(scope_selector(s, prefix) for s in selectors)
    return scoped + rule[brace:]


def scope_rules(css: str, prefix: str) -> str:
    parts: list[str] = []
    idx = 0
    while idx < len(css):
        chunk = css[idx:].lstrip()
        if chunk.startswith("@"):
            at = css.find("@", idx)
            end = css.find("}", at)
            block = css[at : end + 1]
            if block.startswith("@media"):
                inner_start = block.find("{") + 1
                inner = block[inner_start:-1]
                scoped_inner = scope_rules(inner, prefix)
                parts.append(block[:inner_start] + scoped_inner + "}")
            else:
                parts.append(block)
            idx = end + 1
            continue
        end = css.find("}", idx)
        if end == -1:
            parts.append(css[idx:])
            break
        parts.append(scope_rule(css[idx : end + 1], prefix))
        idx = end + 1
    return "".join(parts)


def scope_stylesheet(source: str, prefix: str) -> str:
    return scope_rules(source, prefix)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    vendor = root / "src" / "radspion" / "static" / "css" / "markdown" / "vendor"
    source = (vendor / "latex.css").read_text(encoding="utf-8")
    prefix = ".mission-markdown.latex-document"
    scoped = scope_stylesheet(source, prefix)
    header = "/* Scoped from LaTeX.css (MIT) — https://github.com/vincentdoerig/latex-css */\n"
    (vendor / "latex-scoped.css").write_text(header + scoped, encoding="utf-8")


if __name__ == "__main__":
    main()
