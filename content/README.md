# Mission content (Brief / Debrief)

Markdown files referenced by `missions.brief_path` and `missions.debrief_path` in the database.
Paths are relative to the project root (e.g. `content/missions/<slug>/brief.md`).

## Layout

| Path | Purpose |
|------|---------|
| `content/missions/` | **Live** mission files served in production and referenced by operator SQL |
| `content/missions/basic-training/` | Default system mission (always in git) |

Each mission directory is named by **slug** and contains `brief.md` and `debrief.md`.

Mission packs (example class, Last Transmission, etc.) live in the sibling **radspion-missions** repo. Bootstrap scripts there copy markdown into `content/missions/` when loading a pack seed.

## Default database

**Production / `create_empty_db.sh`:** schema + Orientation arc + `basic-training` only; disk needs `content/missions/basic-training/`.

**UI mockups** in [`docs/ui/`](../docs/ui/) inline brief/debrief HTML for layout review; production content lives under `content/missions/` or **radspion-missions** pack directories.

When authoring lists with fenced code blocks, indent the opening ` ``` ` to align with list text (CommonMark). The app renders Brief/Debrief with **Python-Markdown** (`fenced_code`, `sane_lists`, `tables`) — see [docs/mission-markdown.md](../docs/mission-markdown.md).
