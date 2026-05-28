# Database schema

**Engine:** SQLite 3  
**DDL:** [`src/radspion/sql/schema.sql`](../../src/radspion/sql/schema.sql)  
**Seed:** [`seed_orientation.sql`](../../src/radspion/sql/seed_orientation.sql), [`seed_registration_access_codes.sql`](../../src/radspion/sql/seed_registration_access_codes.sql), [`seed_example_class.sql`](../../src/radspion/sql/seed_example_class.sql)

Enable foreign keys on each connection: `PRAGMA foreign_keys = ON;` (included at the top of the SQL files).

## Enumerated columns (`CHECK` constraints)

SQLite has no separate enum types. Allowed values are enforced on the column:

| Column | Table | Allowed values |
|--------|-------|----------------|
| `access_rule` | `missions` | `open`, `unlock_code`, `requires_complete` |
| `status` | `agent_mission_status` | `active`, `completed` |

## Tables

### `users`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `email` | `TEXT` | NOT NULL, UNIQUE |
| `google_subject_id` | `TEXT` | NOT NULL, UNIQUE |
| `display_name` | `TEXT` | NOT NULL |
| `is_operator` | `INTEGER` | NOT NULL, DEFAULT `0`, CHECK `IN (0, 1)` |

### `registration_access_codes`

| Column | Type | Constraints |
|--------|------|-------------|
| `code` | `TEXT` | PK |

Signup gate only: a new agent must submit a valid row before first Google OAuth creates a `users` row. **Not** tied to groups or missions; class content still uses `group_members`. Trim whitespace on input; comparison is **case-sensitive**. Returning agents (existing `users` row) sign in with Google only. Seed: [`seed_registration_access_codes.sql`](../../src/radspion/sql/seed_registration_access_codes.sql).

### `groups`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `name` | `TEXT` | NOT NULL, UNIQUE |

### `group_members`

| Column | Type | Constraints |
|--------|------|-------------|
| `group_id` | `INTEGER` | PK, FK → `groups` |
| `user_id` | `INTEGER` | PK, FK → `users` |

### `missions`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `slug` | `TEXT` | NOT NULL, UNIQUE |
| `title` | `TEXT` | NOT NULL |
| `brief_path` | `TEXT` | NOT NULL |
| `debrief_path` | `TEXT` | NOT NULL |
| `group_id` | `INTEGER` | NOT NULL, FK → `groups` |
| `access_rule` | `TEXT` | NOT NULL, CHECK (see enums above) |
| `completion_code` | `TEXT` | NOT NULL |

**Consistency rules:**

| `access_rule` | Requires |
|---------------|----------|
| `open` | No `mission_unlock_codes`; no `mission_list_requires` |
| `unlock_code` | Exactly one row in `mission_unlock_codes`; **no** `mission_list_requires` rows for this mission (code unlock vs automatic listing are mutually exclusive) |
| `requires_complete` | One or more `mission_list_requires` |

**V1 product rule (sample data follows this):** A mission never combines **`unlock_code`** with **`mission_list_requires`**, and never **`unlock_code`** with **`mission_complete_requires`** rows where this mission is `mission_id` (no “code + prerequisite completions” missions). Use either a redeemable code **or** automatic listing/prereqs, not both.

`required_mission_id` in require tables should reference a mission with the same `group_id` as `mission_id`.

### `mission_unlock_codes`

| Column | Type | Constraints |
|--------|------|-------------|
| `mission_id` | `INTEGER` | PK, FK → `missions` |
| `unlock_code` | `TEXT` | NOT NULL |

### `mission_list_requires`

| Column | Type | Constraints |
|--------|------|-------------|
| `mission_id` | `INTEGER` | PK, FK → `missions` |
| `required_mission_id` | `INTEGER` | PK, FK → `missions` |

### `mission_complete_requires`

| Column | Type | Constraints |
|--------|------|-------------|
| `mission_id` | `INTEGER` | PK, FK → `missions` |
| `required_mission_id` | `INTEGER` | PK, FK → `missions` |

Use when a mission can be **listed** before all submission prerequisites are met (e.g. **remote-access** lists after learn-the-system but cannot be completed until read-the-manual). Skip rows when **`mission_list_requires`** already forces every prerequisite to be `completed` before the mission is visible (e.g. **identify-the-traitor** in the sample seed).

### `agent_mission_status`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `user_id` | `INTEGER` | NOT NULL, FK → `users` |
| `mission_id` | `INTEGER` | NOT NULL, FK → `missions` |
| `status` | `TEXT` | NOT NULL, CHECK (see enums above) |

**Unique:** `(user_id, mission_id)`.

After `completed`, UI may show `missions.completion_code` for that mission.

## Runtime summary

**Sync policy:** maintain `agent_mission_status` **immediately** on `group_members` insert, login, unlock, and complete. A listable `open` mission without an `active` row is an error. No row on `unlock_code` missions until redeem is expected (operator: **locked**).

1. Agent in `group_members` for `missions.group_id`  
2. **List:** `open` → `active` row; `unlock_code` → after redeem; `requires_complete` → after all list prereqs completed  
3. **Complete:** all complete prereqs done → match `completion_code` → `completed`  
4. On complete (and on login) → sync `active` rows for missions whose list prereqs are now satisfied  
