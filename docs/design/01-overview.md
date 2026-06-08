# Overview

## What Radspion is

A web app where students act as **agents** in a spy-agency fiction. **Missions** are real assignments (labs, git, cloud, puzzles) wrapped in a **Mission Brief** and **Debrief**. Agents submit **clearance codes** to list new missions and **data** to complete missions. Missions reach the dashboard by **clearance**, by **`open`** listing (rare), or **automatic listing after required missions are finished** (`requires_complete`). The same mission never mixes clearance gating with `requires_complete` on one row.

## V1 goals

| In scope | Out of scope (post-V1) |
|----------|------------------------------------------|
| Google OAuth (any account) | Faculty self-service wizard |
| SQLite data model below | Story templates / publish pipeline |
| **Groups** as story arcs (dashboard organization) | Full audit log (append-only event history) |
| **Agent Personnel File** (`GET /agent/personnel`) — personal info, field status, service record | Agent codename update on Personnel File |
| Mission Brief / Debrief (markdown paths) | |
| Event timestamps (`users.created_at`, listing/completion times on `agent_mission_status`) | |
| `access_rule`: open, clearance_code, requires_complete | Per-agent keyed codes |
| `mission_clearance_codes`, `mission_list_requires` | |
| **Operator** (you)—configure via SQL seed | |
| Operator **progress** UI (`is_operator`, read-only) | |

## Access

- Agents sign in with Google OAuth (any Google account). First sign-in creates a `users` row.
- **Mission visibility:** `access_rule` + clearance/list constraints — not group membership.
- **`open` missions** are rare (minimal prerequisites, walk-up puzzle content). Most story arcs list missions via clearance or completion prerequisites.
- **Orientation** is a public story arc that teaches clearance and data submission. Other arcs may require clearance from briefs, QR codes, LMS assignments, or field contacts.

## Stack

- **Flask + Jinja** for server-rendered pages; JSON API at `/api/clearance` and `/api/missions/<slug>/submit` — see [api.yaml](../api.yaml). Agent UI copy: [06-agent-experience.md](06-agent-experience.md); mockups: [ui/README.md](../ui/README.md)
- SQLite 3
- Mission Brief/Debrief markdown in DB (`brief_markdown` / `debrief_markdown`), seeded from **radspion-missions**; UI mockups in `docs/ui/` inline HTML for layout review

## Core entities

- **Group** — story arc (`missions.group_id`); organizes the dashboard, does not gate access
- **Mission** — one group, `access_rule`, `completion_data` (completion data), story paths
- **Constraints** — clearance codes in `mission_clearance_codes` (strings may be shared across missions), list prereqs (`mission_list_requires`)
- **AgentMissionStatus** — per agent per mission: `active` or `completed`

Details: [02-entities.md](02-entities.md), [03-database-schema.md](03-database-schema.md). Agent UI: [06-agent-experience.md](06-agent-experience.md).
