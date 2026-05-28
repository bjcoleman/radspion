# Mission content (Brief / Debrief)

Markdown files referenced by `missions.brief_path` and `missions.debrief_path` in the database.
Paths are relative to the project root (e.g. `content/missions/<slug>/brief.md`).

## Layout

| Path | Purpose |
|------|---------|
| `content/missions/` | **Live** mission files served in production and referenced by operator SQL |
| `content/missions/basic-training/` | Default system mission (always in git) |
| `content/samples/example-class/` | Example-class pack (five missions); source for local demo |

Each mission directory is named by **slug** and contains `brief.md` and `debrief.md`.

## Default vs sample

- **Production / `create_empty_db.sh`:** database has Orientation + `basic-training` only; disk needs `content/missions/basic-training/`.
- **Local demo / `bootstrap_sample_class.sh`:** copies the five sample missions into `content/missions/`, then loads the example-class SQL seed (Alice, DevOps group, progress rows).

Copied example missions under `content/missions/` are gitignored; edit sources under `content/samples/example-class/` and re-run bootstrap to refresh.

**UI mockups** in [`docs/ui/`](../docs/ui/) inline brief/debrief HTML for layout review; production content lives under `content/missions/`. When refreshing mockup copy, use `content/missions/<slug>/` or `content/samples/example-class/` as the source of truth.

When authoring lists with fenced code blocks, indent the opening ` ``` ` to align with list text (CommonMark). The app renders Brief/Debrief with **Python-Markdown** (`fenced_code`, `sane_lists`, `tables`) — see [docs/mission-markdown.md](../docs/mission-markdown.md).
