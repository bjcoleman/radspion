# Mission content (Brief / Debrief)

Markdown files referenced by `missions.brief_path` and `missions.debrief_path` in the database.
Paths are relative to the project root (e.g. `content/missions/<slug>/brief.md`).

## Layout

| Path | Purpose |
|------|---------|
| `content/missions/` | Mission Brief and Debrief markdown referenced by `missions` rows |
| `content/missions/basic-training/` | Default orientation mission (production) |
| `content/missions/es-*/` | Testing Storyline missions (dev/test only; see `seed_testing_storyline.sql`) |

Each mission directory is named by **slug** and contains `brief.md` and `debrief.md`.

