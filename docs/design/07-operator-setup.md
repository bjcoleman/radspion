# Operator setup

V1: you configure the system directly with **SQL** (schema + seed scripts). A read-only **operator progress** UI (story arcs → missions → agent status) is in V1; mission editing stays SQL until a later admin UI.

Set `users.is_operator = 1` for your account (SQLite stores booleans as integers).

## Configure a story arc (mission pack)

1. Create a `groups` row (story-arc name)  
2. Insert `missions` with `group_id`, `access_rule`, `completion_data`, `brief_markdown`, `debrief_markdown`, `title` (author in **radspion-missions**, then run `seed_storyline` from **radspion**)  
3. If `clearance_code` → row in `mission_clearance_codes` (clearance code). The same string may appear on multiple missions so one **Request Access** lists several entries.  
4. If `requires_complete` → rows in `mission_list_requires`  
5. Trigger status **sync** for affected agents (app does this on login, clearance grant, and data submit when live; in SQL-only workflows, sign-in or a future CLI will reconcile)  

Infrastructure: `schema.sql` in this repo. Storyline mission prose is authored in **radspion-missions** (`storyline.yaml` + markdown) and loaded with `seed_storyline`.

Authoring conventions: [missions/authoring-guide.md](../missions/authoring-guide.md) (clearance vs data, YAML multiline data, first-mission briefs).

## Access rules in practice

| `access_rule` | When to use |
|---------------|-------------|
| `open` | Rare — walk-up puzzles with no clearance ritual |
| `clearance_code` | Agent must **request clearance** (header, QR, LMS, field) |
| `requires_complete` | Lists automatically after prerequisite missions are completed |

The **first mission** in a pack should have a clear title and a brief that explains the arc (premise, prerequisites, time, difficulty). Course-specific requirements (graded, due dates) live in the LMS, not in Radspion copy.

## Operator progress view

- **Groups:** all story arcs; show **Orientation** last on the list page  
- **Missions:** all missions in the arc  
- **Progress grid:** agents with status on missions in that arc → **not started** (no row), **active**, or **complete**  

## Example

See [04-example-data-walkthrough.md](04-example-data-walkthrough.md) for the **Testing Storyline** test graph. Production missions load from **radspion-missions** storyline packs via `seed_storyline` (set `RADSPION_MISSIONS_ROOT` in `.env`).
