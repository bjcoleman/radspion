# Overview

## What Radspion is

A web app where students act as **agents** in a spy-agency fiction. **Missions** are real assignments (labs, git, cloud, puzzles) wrapped in a **Mission Brief** and **Debrief**. Agents enter codes where applicable and complete prerequisites so further missions unlock; missions reach the dashboard either by **redeeming an unlock code** or **automatic listing after required missions are finished** (`requires_complete`). The same mission never mixes those two gates.

## V1 goals

| In scope | Out of scope (post-V1) |
|----------|------------------------------------------|
| Google OAuth (any account); registration code on first signup | Faculty self-service wizard |
| SQLite data model below | Story templates / publish pipeline |
| **Groups** as story arcs (dashboard organization) | Audit log, timestamps |
| Mission Brief / Debrief (markdown paths) | Per-agent keyed codes |
| `access_rule`: open, unlock_code, requires_complete | |
| `mission_unlock_codes`, `mission_list_requires` | |
| **Operator** (you)—configure via SQL seed | |
| Operator **progress** UI (`is_operator`, read-only) | |

## Access

- **New agents:** valid `registration_access_codes` row, then Google OAuth (any Google account). First sign-in creates a `users` row.
- **Returning agents:** Google OAuth only (no registration code).
- **Mission visibility:** `access_rule` + unlock/list constraints — not group membership. Story-arc entry uses `unlock_code` or `open` missions (e.g. `basic-training`).
- Seed welcome mission: `basic-training` (“Welcome to Radspion”) in the **Orientation** story arc.

## Stack

- **Flask + Jinja** for server-rendered pages; JSON API at `/api/` (access, unlock, mission submit) — see [api.yaml](../api.yaml)
- SQLite 3
- Mission Brief/Debrief markdown in DB (`brief_markdown` / `debrief_markdown`), seeded from **radspion-missions**; UI mockups in `docs/ui/` inline HTML for layout review
## Core entities

- **Group** — story arc (`missions.group_id`); organizes the dashboard, does not gate access
- **Mission** — one group, `access_rule`, `completion_code`, story paths
- **Constraints** — unlock codes (one per mission; code strings may be shared), list prereqs (`mission_list_requires`)
- **AgentMissionStatus** — per agent per mission: `active` or `completed`

Details: [02-entities.md](02-entities.md), [03-database-schema.md](03-database-schema.md).

