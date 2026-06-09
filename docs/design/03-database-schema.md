# Database schema

**Engine:** SQLite 3  
**DDL:** [`src/radspion/sql/schema.sql`](../../src/radspion/sql/schema.sql)  
**Seed (infrastructure):** `schema.sql` only in this repo. Storyline packs load via `seed_storyline`.


Enable foreign keys on each connection: `PRAGMA foreign_keys = ON;` (included at the top of the SQL files).

## Enumerated columns (`CHECK` constraints)

SQLite has no separate enum types. Allowed values are enforced on the column:

| Column | Table | Allowed values |
|--------|-------|----------------|
| `access_rule` | `missions` | `open`, `clearance_code`, `requires_complete` |
| `status` | `agent_mission_status` | `active`, `completed` |
| `listed_via` | `agent_mission_status` | `clearance`, `open`, `requires_complete` |

## Tables

### `users`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `email` | `TEXT` | NOT NULL, UNIQUE |
| `google_subject_id` | `TEXT` | NOT NULL, UNIQUE |
| `display_name` | `TEXT` | NOT NULL — Google sign-in name; not shown on Field Activity |
| `codename` | `TEXT` | NOT NULL, UNIQUE — public agent identifier (header, Field Activity) |
| `created_at` | `TEXT` | NOT NULL, DEFAULT `datetime('now')` — first sign-in (Personnel File **Recruited on**) |
| `is_operator` | `INTEGER` | NOT NULL, DEFAULT `0`, CHECK `IN (0, 1)` |

**Codename validation:** no length or character `CHECK` on this column. Rules (`4 <= len(codename) <= 20`, Unicode allowed) are enforced in application code when an agent changes their codename. Default codenames (`AGENT0001`, …) are assigned at provisioning only.

### `codename_counter`

Single-row table. On each new user, the app increments `next_value` and assigns `AGENT` + zero-padded sequence (e.g. `next_value` `1` → `AGENT0001`). Increment and user insert run in one transaction.

| Column | Type | Constraints |
|--------|------|-------------|
| `next_value` | `INTEGER` | NOT NULL, CHECK `>= 0` |

### `groups`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `name` | `TEXT` | NOT NULL, UNIQUE |

Story-arc label for dashboard sections and operator navigation.

### `missions`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `slug` | `TEXT` | NOT NULL, UNIQUE |
| `title` | `TEXT` | NOT NULL |
| `brief_markdown` | `TEXT` | NOT NULL |
| `debrief_markdown` | `TEXT` | NOT NULL |
| `group_id` | `INTEGER` | NOT NULL, FK → `groups` |
| `access_rule` | `TEXT` | NOT NULL, CHECK (see enums above) |
| `completion_data` | `TEXT` | NOT NULL — mission **completion data**; may include newlines |

**Consistency rules:**

| `access_rule` | Requires |
|---------------|----------|
| `open` | No `mission_clearance_codes`; no `mission_list_requires` |
| `clearance_code` | Exactly one row in `mission_clearance_codes`; **no** `mission_list_requires` rows for this mission |
| `requires_complete` | One or more `mission_list_requires` |

**product rule:** A mission never combines **`clearance_code`** with **`mission_list_requires`**. Use either clearance gating **or** automatic listing after completions, not both.

### `mission_clearance_codes`

| Column | Type | Constraints |
|--------|------|-------------|
| `mission_id` | `INTEGER` | PK, FK → `missions` |
| `clearance_code` | `TEXT` | NOT NULL |

**Product rules:**

- One row per mission (`mission_id` PK) when `access_rule = clearance_code`.
- **`clearance_code` is not unique** across rows — operators may reuse the same clearance string on multiple missions.
- Granting clearance lists every matching mission that does not yet have an `agent_mission_status` row for the agent.
- **Authoring convention:** clearance codes use letters, digits, and hyphens only (see [06-agent-experience.md](06-agent-experience.md)).

### `mission_list_requires`

| Column | Type | Constraints |
|--------|------|-------------|
| `mission_id` | `INTEGER` | PK, FK → `missions` |
| `required_mission_id` | `INTEGER` | PK, FK → `missions` |

### `agent_mission_status`

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | `INTEGER` | PK, `AUTOINCREMENT` |
| `user_id` | `INTEGER` | NOT NULL, FK → `users` |
| `mission_id` | `INTEGER` | NOT NULL, FK → `missions` |
| `status` | `TEXT` | NOT NULL, CHECK (see enums above) |
| `listed_at` | `TEXT` | NOT NULL, DEFAULT `datetime('now')` — mission added to agent dashboard |
| `listed_via` | `TEXT` | NOT NULL, CHECK — how the mission was listed: `clearance`, `open`, or `requires_complete` |
| `completed_at` | `TEXT` | NULL until `status = completed` |

**Unique:** `(user_id, mission_id)`.

After `completed`, UI may show `missions.completion_data` for that mission.

## Runtime summary

**Sync policy:** maintain `agent_mission_status` **immediately** on login, clearance grant, and data submit. A listable `open` mission without an `active` row is an error. No row on `clearance_code` missions until clearance is granted is expected.

1. Signed-in agent  
2. **List:** `open` → `active` row; `clearance_code` → after clearance granted; `requires_complete` → after all list prereqs completed  
3. **Complete:** mission `active` → match `completion_data` → `completed`  
4. On complete (and on login) → sync `active` rows for missions whose list prereqs are now satisfied  
