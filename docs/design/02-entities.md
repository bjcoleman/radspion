# Data model

SQLite. **Groups** are story arcs (organization for the dashboard and operator views). **Missions** belong to one group. **Constraints** are keyed by `mission_id`. Mission availability is controlled by `access_rule` and constraint tables — not group membership.

## Agent vocabulary

Agents work with **clearance** and **data**. The database and API use the names below.

| Agent term | Database / API | UI label |
|------------|----------------|----------|
| Clearance code | `mission_clearance_codes.clearance_code`, `POST /api/clearance` → `clearance_code` | Header placeholder **Clearance code**; button **Request Access** |
| Recovered data | `missions.completion_data`, `POST /api/missions/<slug>/submit` → `completion_data` | **Recovered Data** panel (active and completed); button **Submit data** on active missions |

Format rules, layout, and modal copy: [06-agent-experience.md](06-agent-experience.md). Mockups: [`docs/ui/README.md`](../ui/README.md).

## Groups

- `groups` — named story arcs (e.g. **Orientation**, **Testing Storyline**, **Last Transmission**)
- `missions.group_id` — which arc a mission belongs to (UI sections, operator reports)
- Groups do **not** gate access; any signed-in agent is evaluated against each mission's `access_rule`

## Missions

| Field | Purpose |
|-------|---------|
| `slug` | Stable internal id |
| `title` | Agent-visible name |
| `brief_markdown`, `debrief_markdown` | Mission Brief / Debrief markdown |
| `group_id` | Story arc for dashboard grouping |
| `access_rule` | How the mission gets on the agent's list |
| `completion_data` | Completion data — exact text required to mark the mission completed (may be multi-line) |

### `access_rule` (one per mission)

A mission is surfaced by **clearance**, by **`open`** listing, or **automatic listing after completions**. A mission with `clearance_code` access has no `mission_list_requires` rows.

| Value | Listed when |
|-------|-------------|
| `open` | Any signed-in agent (sync creates `active` row) |
| `clearance_code` | Agent requests matching clearance (`mission_clearance_codes`) |
| `requires_complete` | Agent completed all `mission_list_requires` missions |

## Constraint tables

### `mission_clearance_codes` (one row per mission)

Each `clearance_code` mission has exactly one row in this table (`mission_id` PK). The **`clearance_code` string is not unique** across rows — the same clearance code may gate multiple missions; granting it lists every matching mission not yet on the agent's dashboard. Clearance gating is mutually exclusive with automatic listing (**`mission_list_requires`**) on the same mission.

**Authoring convention:** clearance codes use letters, digits, and hyphens only; human-readable strings are encouraged.

### `mission_list_requires` (1:many)

Must **complete** `required_mission_id` before this mission is **listed**.  
Used with `requires_complete`. Prereqs may span story arcs if you design them that way; in-arc chains are the common case.

## Users

Each agent has two names:

| Field | Source | Visibility |
|-------|--------|------------|
| `display_name` | Google OAuth profile | Private — Personnel File and operator views only |
| `codename` | Assigned at first sign-in | Public — site header, Field Activity; readonly on Personnel File |
| `created_at` | Set on first sign-in (`DEFAULT datetime('now')`) | Personnel File **Recruited on**; service record **Enlisted** |

- **`is_operator`**: SQLite `INTEGER` `0` or `1` (not a native boolean); `1` may use read-only operator progress UI (V1)
- Signed-in agents are provisioned on first OAuth; the operator uses one `users` row (`is_operator = 1`)
- **Default codename:** on first sign-in the system allocates the next sequential name (`AGENT0001`, `AGENT0002`, …) via `codename_counter` in the same transaction as user creation. The agent does not choose a codename at signup.
- **Codename on Personnel File:** readonly input; **Update** disabled. Hint copy references 4–20 characters ([06-agent-experience.md](06-agent-experience.md)).

### Service record (Personnel File)

The **Service Record** on the Agent Personnel File is **derived at read time** — not stored in a separate audit table. Events are assembled from `users.created_at` and `agent_mission_status` timestamps, sorted newest first:

| Verb | Source | Detail |
|------|--------|--------|
| **Enlisted** | `users.created_at` | Fixed copy: *Personnel file opened* |
| **Clearance Granted** | `agent_mission_status.listed_at` | Mission `title` — one row per status row (includes `open` sync and `requires_complete` auto-listing, not only clearance codes) |
| **Mission Completed** | `agent_mission_status.completed_at` | Mission `title` — only rows where `completed_at` is set |

**Field Status** counts on the same page: `completed` and `active` rows in `agent_mission_status` for the signed-in agent.

## Agent progress

**`agent_mission_status`**: `(user_id, mission_id, status)` — `active` | `completed`, plus:

| Column | Purpose |
|--------|---------|
| `listed_at` | When the mission was added to the agent's dashboard (`DEFAULT datetime('now')` on insert) |
| `completed_at` | Set when `status` becomes `completed`; `NULL` while `active` |

- Completed missions may display `missions.completion_data` (data); never expose it for `active` missions
- **No row** means not listable yet (clearance not granted, or list prereqs not met). Missions that are not listable are **hidden** from the agent dashboard — not shown as locked placeholders
- For listable `open` missions, a missing row is a **sync error**

## Operator progress (V1, read-only)

Organize by story arc (`groups` → `missions`). For each mission, show agents who have **any** `agent_mission_status` row on missions in that arc, or all signed-in users for globally `open` missions (TBD in UI implementation).

| Label | Rule |
|-------|------|
| complete | status row `completed` |
| active | status row `active` |
| not started | signed-in user, no status row on this mission |

## Runtime (summary)

Keep **`agent_mission_status` current immediately** on login, clearance grant, and data submit — agent dashboard and operator views read this table.

1. Signed-in agent  
2. **List:** per `access_rule` + `mission_list_requires` → ensure `active` row exists when listable  
3. **Complete:** mission is `active` and submitted data matches `completion_data` → `completed`  
4. On complete → sync: create `active` rows for missions whose `mission_list_requires` are now satisfied  

## Diagram

```mermaid
erDiagram
    groups ||--o{ missions : contains
    missions ||--o| mission_clearance_codes : optional_clearance
    missions ||--o{ mission_list_requires : lists_after
    users ||--o{ agent_mission_status : progress
    missions ||--o{ agent_mission_status : on
```

## SQL reference

[03-database-schema.md](03-database-schema.md) · [04-example-data-walkthrough.md](04-example-data-walkthrough.md)
