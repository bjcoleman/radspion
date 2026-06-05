# Radspion UI Color Usage Spec

This spec defines consistent color roles for static UI mockups in `docs/ui/`.

## Core Tokens

- `--color-accent` (`#c4a35a`): mission accent / emphasized headings
- `--color-text` (`#e8eaed`): primary readable text
- `--color-text-muted` (`#9aa3ad`): supporting copy
- `--color-text-faint` (`#6b7580`): metadata / tertiary labels

## Usage Rules

1. **Emphasized headings use accent**
   - Use accent for key panel/section headings and outcome titles.
   - Do not use accent for long paragraphs.

2. **Body copy stays muted or primary**
   - Explanatory text: `--color-text-muted`
   - Primary content text: `--color-text`

3. **Button semantics are role-based**
   - **App-native primary actions** (Request Access, Submit data, OK): accent button.
   - **Identity provider handoff** (Google OAuth): white Google-style button.

4. **Keep visual hierarchy stable**
   - Avoid introducing additional button color variants unless a new semantic role is needed.
   - Avoid making all buttons white; reserve white for provider handoff.

5. **Accessibility intent**
   - Maintain strong contrast on dark backgrounds.
   - Prefer muted/faint text only for non-critical content.

## Current Mapping in Mockups

- Accent buttons: **Request Access**, **Submit data**, **OK**
- White provider buttons: **Sign in with Google**
- Accent headings: Data / Recovered Data panels, modal progress titles and outcome headings
- Muted body copy: instructional text, modal body messages, dashboard lede
