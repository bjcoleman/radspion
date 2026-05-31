# Example seed: data in tables

> **Pending missions-pack rework.** The narrative below describes the **target** model (story arcs, no rosters, list prereqs only). The SQL seed in [`radspion-missions/example-class/seed_example_class.sql`](../../../radspion-missions/example-class/seed_example_class.sql) still uses the old roster and `mission_complete_requires` tables and **will not load** against the current schema until updated.

Reference seed for development and use-case work. Load with (after seed is updated):

```bash
# From radspion-missions repo:
./example-class/bootstrap_sample_class.sh
```

That script expects a checkout of **radspion** alongside **radspion-missions** for schema and orientation seeds. For orientation-only data, use `./scripts/create_empty_db.sh` in **radspion**.

The schema and seed files run `PRAGMA foreign_keys = ON;` at the start of each script.

**Story arcs:** `Orientation` (id 1), `220.2 DevOps` (id 2).

## missions (target)

| id | slug | title | group_id | access_rule | completion_code (abbrev) |
|----|------|-------|----------|-------------|--------------------------|
| 1 | basic-training | Welcome to Radspion | 1 | open | WELCOME-AGENT-OK |
| 2 | global-hidden | Training: Confidential Briefing | 1 | unlock_code | CONFIDENTIAL-BRIEF-OK |
| 3 | read-the-manual | Training: Read the Manual | 2 | unlock_code * | READ-MANUAL-OK |
| 4 | learn-the-system | Training: Learn the System | 2 | requires_complete * | LEARN-SYSTEM-OK |
| 5 | remote-access | Training: Remote Access | 2 | requires_complete | (SSH private key example) |
| 6 | identify-the-traitor | Training: Identify the Traitor | 2 | requires_complete | TRAITOR-IDENTIFIED-OK |

\* **Pending pack rework:** DevOps arc entry and list graph are TBD. The old seed used roster-gated `open` starters and `mission_complete_requires` on remote-access; the target model gates the arc with `unlock_code` and expresses order via `mission_list_requires` only.

**Listing (two mechanisms, never combined on one mission):**

- **`unlock_code`** — agent redeems `mission_unlock_codes` (sample: `global-hidden`; DevOps arc entry TBD).
- **`requires_complete`** — agent sees the mission after completing all `mission_list_requires` targets.

## mission_unlock_codes (target)

| mission_id | unlock_code |
|------------|-------------|
| 2 | UNLOCK-BLINDFOLD |

## mission_list_requires (target — illustrative)

Exact rows depend on pack rework. Example intent:

| mission_id | required_mission_id | meaning |
|------------|---------------------|---------|
| 5 | 4 | remote-access listed after learn-the-system complete |
| 6 | 3 | identify-the-traitor listed after read-the-manual complete |
| 6 | 5 | identify-the-traitor listed after remote-access complete |

## agent_mission_status (target personas)

When `status = completed`, the app shows `missions.completion_code` for that mission.

Personas (Alice, Bob, Charlie, Diana) and per-agent rows will be revised when the seed is reworked. See [05-example-class.md](05-example-class.md) for the intended acceptance scenarios.

## Queries

**Missions in a story arc:**

```sql
SELECT slug, title, access_rule
FROM missions
WHERE group_id = (SELECT id FROM groups WHERE name = '220.2 DevOps');
```

**List prereqs for a mission by slug:**

```sql
SELECT m.slug
FROM mission_list_requires mlr
JOIN missions target ON target.id = mlr.mission_id
JOIN missions m ON m.id = mlr.required_mission_id
WHERE target.slug = 'identify-the-traitor';
```
