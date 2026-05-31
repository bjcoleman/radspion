# Operator setup

V1: you configure the system directly with **SQL** (schema + seed scripts). A read-only **operator progress** UI (story arcs → missions → agent status) is in V1; mission editing stays SQL until a later admin UI.

Set `users.is_operator = 1` for your account (SQLite stores booleans as integers).

## Registration access codes

Rows in `registration_access_codes` gate **new account creation** only. Use separate codes per audience so you can rotate one without changing the others (e.g. CS recruitment, DevOps class, external invite). Comparison is **case-sensitive** after trimming whitespace.

```sql
-- Add or rotate a code
INSERT INTO registration_access_codes (code) VALUES ('your-secret-code');

-- Revoke a code (blocks new signups with that code; existing users unaffected)
DELETE FROM registration_access_codes WHERE code = 'old-code';
```

Default seed placeholders: [`seed_registration_access_codes.sql`](../../src/radspion/sql/seed_registration_access_codes.sql). Replace `CHANGE-ME-*` before production.

## Configure a story arc (mission pack)

1. Create a `groups` row (story-arc name)  
2. Insert `missions` with `group_id`, `access_rule`, `completion_code`, paths under `content/missions/<slug>/`, `title`  
3. If `unlock_code` → row in `mission_unlock_codes` (typical arc entry)  
4. If `requires_complete` → rows in `mission_list_requires`  
5. Trigger status **sync** for affected agents (app does this on login/unlock/complete when live; in SQL-only workflows, sign-in or a future CLI will reconcile)  

Mission pack content and seeds live in **radspion-missions** (sibling repo). Infrastructure seeds (`schema.sql`, `seed_orientation.sql`) live in this repo.

## Operator progress view

- **Groups:** all story arcs; show **Orientation** last on the list page  
- **Missions:** all missions in the arc  
- **Progress grid:** agents with status on missions in that arc → **not started** (no row), **active**, or **complete**  

## Example

See [04-example-data-walkthrough.md](04-example-data-walkthrough.md). SQL: [`seed_orientation.sql`](../../src/radspion/sql/seed_orientation.sql) (default). Example class pack: [`radspion-missions/example-class/`](../../../radspion-missions/example-class/) (seed pending rework; bootstrap via `bootstrap_sample_class.sh` in that repo).
