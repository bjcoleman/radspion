# Operator setup

V1: you configure the system directly with **SQL** (schema + seed scripts). A read-only **operator progress** UI (groups → missions → roster status) is in V1; mission/roster editing stays SQL until a later admin UI. CLI helpers for roster/sync are a later convenience.

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

## Configure a class

1. Create `groups` row and `group_members` for agents (every class member must also be in **Orientation**)  
2. Insert `missions` with `group_id`, `access_rule`, `completion_code`, paths under `content/missions/<slug>/`, `title`  
3. If `unlock_code` → row in `mission_unlock_codes`  
4. If `requires_complete` → rows in `mission_list_requires`  
5. Add `mission_complete_requires` where completion must be gated  
6. Trigger status **sync** for affected agents (app does this on insert when live; in SQL-only workflows, sign-in or a future CLI will reconcile)  

## Operator progress view

- **Groups:** all groups; show **Orientation** last on the list page  
- **Missions:** all missions in the group  
- **Roster grid:** each student in the group → **locked** (no status row), **active**, or **complete**  

## Example

See [04-example-data-walkthrough.md](04-example-data-walkthrough.md). SQL: [`seed_orientation.sql`](../../src/radspion/sql/seed_orientation.sql) (default), [`seed_example_class.sql`](../../src/radspion/sql/seed_example_class.sql) (demo). Sample content: `content/samples/example-class/` (installed by `scripts/bootstrap_sample_class.sh`).
