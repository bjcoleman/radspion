# Overview

## What Radspion is

A web app where students act as **agents** in a spy-agency fiction. **Missions** are real assignments (labs, git, cloud, puzzles) wrapped in a **Mission Brief** and **Debrief**. Agents enter codes where applicable and complete prerequisites so further missions unlock; missions reach the roster either by **redeeming an unlock code** or **automatic listing after required missions are finished** (`requires_complete`). The same mission never mixes those two gates. Stealth messaging hides completion-order spoilers in the UI.

## V1 goals

| In scope | Out of scope (post-V1) |
|----------|------------------------------------------|
| Google OAuth (any account); registration code on first signup; auto-join **Orientation** | Faculty self-service wizard |
| SQLite data model below | Story templates / publish pipeline |
| Campus-wide **groups** (e.g. **Orientation**) + class **groups** (roster) | Audit log, timestamps |
| Mission Brief / Debrief (markdown paths) | Per-agent keyed codes |
| `access_rule`: open, unlock_code, requires_complete | |
| `mission_unlock_codes`, `mission_list_requires`, `mission_complete_requires` | |
| Stealth completion prereqs (generic errors) | |
| **Operator** (you)—configure via SQL seed | |
| Operator **progress** UI (`is_operator`, read-only) | |
| Canonical **example class** seed (Alice, Bob, Charlie, Diana) | |

## Access

- **New agents:** valid `registration_access_codes` row, then Google OAuth (any Google account). First sign-in creates a `users` row and adds them to **Orientation**.
- **Returning agents:** Google OAuth only (no registration code).
- Class missions still require `group_members` roster rows; registration codes do not grant class access.
- Seed welcome mission: `basic-training` (“Welcome to Radspion”).

## Stack

- **Flask + Jinja** for server-rendered pages; JSON API for unlock and mission submit
- SQLite 3
- Markdown files on disk for Brief/Debrief under `content/missions/<slug>/`; UI mockups in `docs/ui/` inline HTML for layout review

## Core entities

- **Group** — roster (`group_members`); every signed-in agent is in the campus-wide group (seed: **Orientation**)
- **Mission** — one group, `access_rule`, `completion_code`, story paths
- **Constraints** — unlock code (1:1), list prereqs, complete prereqs
- **AgentMissionStatus** — per agent per mission: `active` or `completed`

Details: [02-entities.md](02-entities.md), [03-database-schema.md](03-database-schema.md).

## Canonical example

The **220.2 DevOps** example seed + four agents (Alice, Bob, Charlie, Diana) is the reference for tests and use cases: [05-example-class.md](05-example-class.md), [04-example-data-walkthrough.md](04-example-data-walkthrough.md).
