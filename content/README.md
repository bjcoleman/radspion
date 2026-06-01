# Mission content (Brief / Debrief)

Markdown files referenced by `missions.brief_path` and `missions.debrief_path` in the database.
Paths are relative to the project root (e.g. `content/missions/<slug>/brief.md`).

## Layout

| Path | Purpose |
|------|---------|
| `content/missions/` | **Live** mission files served in production and referenced by operator SQL |
| `content/missions/basic-training/` | Default system mission  |

Each mission directory is named by **slug** and contains `brief.md` and `debrief.md`.

