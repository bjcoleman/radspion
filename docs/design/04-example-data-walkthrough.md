# Example seed: data in tables

Reference seed for development and use-case work. Load with:

```bash
./scripts/bootstrap_sample_class.sh
```

This installs sample mission files and loads schema + orientation + example-class seeds. For orientation-only data, use `./scripts/create_empty_db.sh`.

The schema and seed files run `PRAGMA foreign_keys = ON;` at the start of each script.

**Groups:** `Orientation` (id 1), `220.2 DevOps` (id 2).

## group_members

| user | Orientation (1) | 220.2 DevOps (2) |
|------|-----------------|------------------|
| Alice | ✓ | ✓ |
| Bob | ✓ | ✓ |
| Charlie | ✓ | ✓ |
| Diana | ✓ | — |

## missions

| id | slug | title | group_id | access_rule | completion_code (abbrev) |
|----|------|-------|----------|-------------|--------------------------|
| 1 | basic-training | Welcome to Radspion | 1 | open | WELCOME-AGENT-OK |
| 2 | global-hidden | Training: Confidential Briefing | 1 | unlock_code | CONFIDENTIAL-BRIEF-OK |
| 3 | read-the-manual | Training: Read the Manual | 2 | open | READ-MANUAL-OK |
| 4 | learn-the-system | Training: Learn the System | 2 | open | LEARN-SYSTEM-OK |
| 5 | remote-access | Training: Remote Access | 2 | requires_complete | (SSH private key example) |
| 6 | identify-the-traitor | Training: Identify the Traitor | 2 | requires_complete | TRAITOR-IDENTIFIED-OK |

**Listing (two mechanisms, never combined on one mission):**

- **`unlock_code`** — agent redeems `mission_unlock_codes` (sample: only `global-hidden`).
- **`requires_complete`** — agent sees the mission after completing all `mission_list_requires` targets (sample: `remote-access` after `learn-the-system`; `identify-the-traitor` after `read-the-manual` and `remote-access`).

## mission_unlock_codes

| mission_id | unlock_code |
|------------|-------------|
| 2 | UNLOCK-BLINDFOLD |

## mission_list_requires

| mission_id | required_mission_id | meaning |
|------------|---------------------|---------|
| 5 | 4 | remote-access listed after learn-the-system complete |
| 6 | 3 | identify-the-traitor listed after read-the-manual complete |
| 6 | 5 | identify-the-traitor listed after remote-access complete |

## mission_complete_requires

| mission_id | required_mission_id | meaning |
|------------|---------------------|---------|
| 5 | 3 | complete remote-access only after read-the-manual |

**identify-the-traitor** has no `mission_complete_requires` rows: it is not listable until **read-the-manual** and **remote-access** are both `completed` (`mission_list_requires`), so separate completion gates would be redundant.

## agent_mission_status

When `status = completed`, the app shows `missions.completion_code` for that mission.

### Alice (user 1)

| mission_id | slug | status |
|------------|------|--------|
| 1 | basic-training | completed |
| 3 | read-the-manual | completed |
| 4 | learn-the-system | completed |
| 5 | remote-access | active |
| — | global-hidden | no row |
| — | identify-the-traitor | no row |
| — | (unlock not redeemed for global-hidden) | |

### Bob (user 2)

| mission_id | status |
|------------|--------|
| 1–6 | all completed |

### Charlie (user 3)

| mission_id | slug | status |
|------------|------|--------|
| 1 | basic-training | active |
| 3 | read-the-manual | active |
| 4 | learn-the-system | completed |
| 5 | remote-access | active |
| — | identify-the-traitor | no row |

Charlie has **remote-access** on his list (`requires_complete` satisfied via **learn-the-system** completed) but cannot **complete** it until **read-the-manual** is `completed` (`mission_complete_requires`: remote-access requires read-the-manual).

### Diana (user 4)

| mission_id | status |
|------------|--------|
| 1 | active |
| 2–6 | no rows (`unlock_code` for `global-hidden` until redeemed; not in DevOps roster for missions 3–6) |

## Queries

**Alice’s 220.2 DevOps missions:**

```sql
SELECT m.slug, ams.status, m.completion_code
FROM agent_mission_status ams
JOIN missions m ON m.id = ams.mission_id
WHERE ams.user_id = 1 AND m.group_id = 2;
```

**List prereqs for identify-the-traitor (mission 6):**

```sql
SELECT m.slug
FROM mission_list_requires mlr
JOIN missions m ON m.id = mlr.required_mission_id
WHERE mlr.mission_id = 6;
```
