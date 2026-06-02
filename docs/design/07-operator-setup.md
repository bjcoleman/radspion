# Operator setup

V1: you configure the system directly with **SQL** (schema + seed scripts). A read-only **operator progress** UI (story arcs → missions → agent status) is in V1; mission editing stays SQL until a later admin UI.

Set `users.is_operator = 1` for your account (SQLite stores booleans as integers).

## Configure a story arc (mission pack)

1. Create a `groups` row (story-arc name)  
2. Insert `missions` with `group_id`, `access_rule`, `completion_code`, `brief_markdown`, `debrief_markdown`, `title` (author in **radspion-missions**, then run `scripts/generate_radspion_sql.py`)  
3. If `unlock_code` → row in `mission_unlock_codes` (typical arc entry). The same `unlock_code` string may appear on multiple missions if you want one redeem to list several entries.
4. If `requires_complete` → rows in `mission_list_requires`  
5. Trigger status **sync** for affected agents (app does this on login/unlock/complete when live; in SQL-only workflows, sign-in or a future CLI will reconcile)  

Infrastructure seeds (`schema.sql`, `seed_orientation.sql`) live in this repo. Storyline mission prose is authored in the private **radspion-missions** repo and generated into `seed_*.sql` via `scripts/generate_radspion_sql.py`.

## Operator progress view

- **Groups:** all story arcs; show **Orientation** last on the list page  
- **Missions:** all missions in the arc  
- **Progress grid:** agents with status on missions in that arc → **not started** (no row), **active**, or **complete**  

## Example

See [04-example-data-walkthrough.md](04-example-data-walkthrough.md) for the **Example Storyline** test graph. Production default: [`seed_orientation.sql`](../../src/radspion/sql/seed_orientation.sql) only (`basic-training`).
