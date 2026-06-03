# Testing Storyline: data in tables

Reference **local test** seed for development and acceptance scenarios. Not used in production.

Load with `./scripts/create_test_db.sh`, or let pytest build temporary databases from `seed_testing_storyline.sql`.

SQL files run `PRAGMA foreign_keys = ON;` at the start of each script.

**Story arcs:** `Orientation` (includes `basic-training`), `Testing Storyline` (five test missions).

## Mission graph

```text
EXAMPLE UNLOCK ──► es-alpha ──► es-gamma ──┐
              └──► es-beta ────────────────┼──► es-delta (finale)
                                           │
HIDDEN UNLOCK ──► es-hidden (dead end)     │
```

- **`unlock_code`** — agent submits listing data from `mission_unlock_codes` (no `mission_list_requires` on the same mission).
- **`requires_complete`** — mission lists after all `mission_list_requires` targets are `completed`.

## missions

| slug | title | group | access_rule | completion_code |
|------|-------|-------|-------------|-----------------|
| basic-training | Welcome to Radspion | Orientation | open | WELCOME-AGENT-OK |
| es-alpha | ES: Alpha | Testing Storyline | unlock_code | COMPLETE es-alpha |
| es-beta | ES: Beta | Testing Storyline | unlock_code | COMPLETE es-beta |
| es-hidden | ES: Hidden | Testing Storyline | unlock_code | COMPLETE es-hidden |
| es-gamma | ES: Gamma | Testing Storyline | requires_complete | COMPLETE es-gamma |
| es-delta | ES: Delta | Testing Storyline | requires_complete | COMPLETE es-delta |

## mission_unlock_codes

| mission slug | unlock_code |
|--------------|-------------|
| es-alpha | EXAMPLE UNLOCK |
| es-beta | EXAMPLE UNLOCK |
| es-hidden | HIDDEN UNLOCK |

Submitting **EXAMPLE UNLOCK** lists both **es-alpha** and **es-beta** (same string, two missions).

## mission_list_requires

| mission slug | requires completed |
|--------------|-------------------|
| es-gamma | es-alpha |
| es-delta | es-beta, es-gamma |

## agent_mission_status (seed personas)

When `status = completed`, the app shows recovered data (`missions.completion_code`) for that mission.

| user | Storyline state (summary) |
|------|---------------------------|
| Diana | `basic-training` only — no storyline missions listed |
| Alice | `es-alpha` completed; `es-beta` and `es-gamma` active |
| Charlie | `es-beta` completed; `es-alpha` active; `es-gamma` not listed |
| Bob | All storyline missions `completed` (including `es-hidden`) |

See [05-testing-storyline.md](05-testing-storyline.md) for acceptance scenarios.

## Queries

**Missions in the Testing Storyline arc:**

```sql
SELECT slug, title, access_rule
FROM missions
WHERE group_id = (SELECT id FROM groups WHERE name = 'Testing Storyline');
```

**List prereqs for es-delta:**

```sql
SELECT m.slug
FROM mission_list_requires mlr
JOIN missions target ON target.id = mlr.mission_id
JOIN missions m ON m.id = mlr.required_mission_id
WHERE target.slug = 'es-delta';
```
