# Use cases (V1)

Ordered by **dependency** — build from the top down. Each case lists **Requires** (other UC ids that must work first). Agent scenarios at the end assume the example seed once updated in **radspion-missions** ([04-example-data-walkthrough.md](04-example-data-walkthrough.md), [`example-class/seed_example_class.sql`](../../../radspion-missions/example-class/seed_example_class.sql) — **pending rework**).

**Reference agents:** Alice, Bob, Charlie, Diana — [05-example-class.md](05-example-class.md). Mission names are **slugs** everywhere (e.g. `read-the-manual`, not numeric ids).

## Resolved decisions

| Topic | Decision |
|-------|----------|
| Who can sign in | Google OAuth; **new** agents need a valid `registration_access_codes` row first |
| New agents | Valid registration code → OAuth → auto-create `users` row |
| Returning agents | Google OAuth only (existing `users` row) |
| Registration codes | Flat list in SQL; case-sensitive after trim; not stored on `users`; independent rotation per code |
| Story arcs | `groups` organize missions on the dashboard; **do not** gate access |
| Mission visibility | `access_rule` + `mission_unlock_codes` + `mission_list_requires` |
| Welcome | Seed includes `basic-training` (`open`) in **Orientation** arc |
| Code vs automatic listing | A mission never mixes **`unlock_code`** with **`mission_list_requires`** |
| Mission list UX | Dashboard shows missions with `agent_mission_status` rows, grouped by story arc |
| `agent_mission_status` | Keep table **in sync at all times** (login + unlock + complete); dashboard reads this table |
| Debrief | Only after mission `completed` |
| Error copy (UC-020, UC-022) | Wording TBD — you’ll review per case |
| Web framework | **Flask + Jinja** SSR; JSON API at `/api/access`, `/api/unlock`, `/api/missions/<slug>/submit` |
| Brief/Debrief paths | Live missions under `content/missions/<slug>/`; packs in **radspion-missions** |
| Operator config V1 | SQL/seed only — no in-app mission editor |
| Operator progress V1 | Read-only UI: story arcs → missions → agent status |
| `users.is_operator` | SQLite `INTEGER` `0`/`1`; gates operator routes |
| Sync timing | **Immediate** on login, unlock, complete — never deferred |
| Operator arc list | All groups; **Orientation** section at the **bottom** |

**Sync invariant:** If a mission is listable (`open`, or `requires_complete` with prereqs met), an `active` row **must** exist for that agent. Missing row in that case is a **bug**, not a UI edge case.

**Why eager sync?** Dashboard and operator views read `agent_mission_status` directly. `unlock_code` missions intentionally have **no row** until redeem.

---

## Platform and data

### UC-001 — Apply SQLite schema

**Actor:** Operator (dev)  
**Requires:** —  
Apply [`src/radspion/sql/schema.sql`](../../src/radspion/sql/schema.sql) so all V1 tables exist (with `CHECK` constraints for enumerated columns).

---

### UC-002 — Load example class seed

**Actor:** Operator (dev)  
**Requires:** UC-001  
Load example-class seed from **radspion-missions** for Orientation + 220.2 DevOps arcs, missions, constraints, and sample progress rows. **Pending pack rework** to match current schema.

---

### UC-003 — Web app connects to SQLite

**Actor:** Developer  
**Requires:** UC-001  
Application stack connects to the Radspion SQLite database (`PRAGMA foreign_keys = ON` on each connection) using **Flask + Jinja** for pages and JSON endpoints under `/api/` ([api.yaml](../api.yaml), [06-agent-experience.md](06-agent-experience.md)).

---

### UC-004 — ORM models match schema

**Actor:** Developer  
**Requires:** UC-003  
Models (or equivalent data layer) for `users` (including `is_operator`), `groups`, `missions`, constraint tables, and `agent_mission_status` with the same semantics as [03-database-schema.md](03-database-schema.md).

---

## Operator configuration (V1, no admin UI)

### UC-005 — Configure a story arc via SQL

**Actor:** Operator  
**Requires:** UC-001  
Create group (arc), missions, unlock/list constraints, and optional seed progress per [07-operator-setup.md](07-operator-setup.md). No in-app wizard in V1.

---

## Authentication

### UC-006 — Validate registration access code (new agents)

**Actor:** Agent (prospective)  
**Requires:** UC-004  
Agent submits a registration access code on the landing page (`POST /api/access`). App trims whitespace and checks `registration_access_codes` (case-sensitive). On success, mark the browser session cleared for signup OAuth; on failure, show invalid-code UI. Returning agents skip this step (UC-006b).

---

### UC-006b — Sign in with Google OAuth

**Actor:** Agent  
**Requires:** UC-004; UC-006 for first-time signup  
Agent authenticates with Google (any Google account); app establishes a session tied to a `users` row.

---

### UC-007 — Resolve or provision agent from OAuth

**Actor:** System  
**Requires:** UC-006b  
- If `users` row exists for `google_subject_id` or email → attach session (no registration code).  
- If no `users` row → require UC-006 session clearance; else reject provisioning.  
- Create user from OAuth profile (`email`, `google_subject_id`, `display_name`).  
- Run mission-status sync (UC-012) before showing the dashboard.

---

## Mission content

### UC-008 — Mission Brief and Debrief on disk

**Actor:** Operator  
**Requires:** UC-002 (for example paths)  
Operator-authored markdown at paths stored on `missions` under `content/missions/<slug>/`. Mission packs live in **radspion-missions**. UI mockups inline representative brief/debrief in HTML — not one mockup file per mission.

---

### UC-009 — Render Mission Brief

**Actor:** Agent  
**Requires:** UC-006b, UC-008  
Agent can view the Brief for a mission they are allowed to see (see UC-012, UC-013).

---

### UC-010 — Render Debrief after completion

**Actor:** Agent  
**Requires:** UC-016  
Agent can view the Debrief only when `agent_mission_status.status = completed` for that mission.

---

## Listing and visibility

### UC-011 — Evaluate mission listability

**Actor:** System  
**Requires:** UC-007  
For each mission, determine listability from `access_rule`, unlock redemption, and `mission_list_requires` — independent of group membership. Non-listable missions are hidden from the agent dashboard.

---

### UC-012 — Sync `agent_mission_status` (immediate)

**Actor:** System  
**Requires:** UC-011  
Keep status rows aligned with listing rules. Run **immediately** when:

- Agent signs in (UC-007)
- Unlock redeemed (UC-019)
- Mission completed (UC-024)

| `access_rule` | Sync behavior |
|---------------|---------------|
| `open` | `active` row if not yet `completed` — **required**; absence is an error |
| `requires_complete` | `active` row when all `mission_list_requires` are `completed` |
| `unlock_code` | **No row** until redeem (UC-019) |

Do not remove rows for completed missions.

---

### UC-013 — Agent mission dashboard

**Actor:** Agent  
**Requires:** UC-012  
After login (post-sync), dashboard lists all `agent_mission_status` rows (`active` or `completed`), grouped by story arc (`groups`). Toggle to show/hide completed missions.

---

### UC-014 — List mission after `unlock_code` redeemed

**Actor:** Agent  
**Requires:** UC-013  
For `access_rule = unlock_code`, create `active` status when the agent submits the correct `mission_unlock_codes.unlock_code` (e.g. global-hidden).

---

## Mission detail and secrets

### UC-016 — Open mission detail

**Actor:** Agent  
**Requires:** UC-013, UC-009  
Agent opens a listed mission: title, Brief link/body, status, completion UI as appropriate.

---

### UC-017 — Hide completion code while `active`

**Actor:** System  
**Requires:** UC-016  
API/UI never returns `missions.completion_code` for missions where the agent’s status is `active` ([06-agent-experience.md](06-agent-experience.md)).

---

### UC-018 — Show captured completion code after `completed`

**Actor:** Agent  
**Requires:** UC-017, UC-021  
After `completed`, agent sees the stored `completion_code` value for that mission (the “captured” secret).

---

## Unlock

### UC-019 — Redeem unlock code (success)

**Actor:** Agent  
**Requires:** UC-014  
Valid unlock code → mission appears on list (`active`). Example: `UNLOCK-BLINDFOLD` for global-hidden.

---

### UC-020 — Redeem unlock code (failure)

**Actor:** Agent  
**Requires:** UC-019  
Invalid unlock code → clear error without revealing mission existence or codes. *(Wording TBD.)*

---

## Completion

### UC-021 — Complete mission

**Actor:** Agent  
**Requires:** UC-016, UC-017  
Agent submits correct `completion_code` while mission is `active` → `status = completed`. Examples: basic-training; any listed mission with matching code.

---

### UC-022 — Reject wrong completion code

**Actor:** Agent  
**Requires:** UC-021  
Wrong code → “not recognized”. *(Wording TBD.)*

---

### UC-024 — Re-sync listing after completion

**Actor:** System  
**Requires:** UC-021, UC-012  
When a mission becomes `completed`, run UC-012 so any newly listable `requires_complete` missions get `active` rows.

---

### UC-015 — List mission after list prerequisites completed

**Actor:** System  
**Requires:** UC-013, UC-024  
For `access_rule = requires_complete`, mission appears on the dashboard when all `mission_list_requires` targets are `completed`. Same mechanism as UC-024; listed here as the agent-visible outcome.

---

## Canonical agent scenarios (acceptance)

These validate the full stack against seed data once **radspion-missions** example-class seed is updated. See [05-example-class.md](05-example-class.md).

### UC-025 — Diana: orientation only

**Actor:** Diana  
**Requires:** UC-013, UC-011  
Sees `basic-training` (`active` or `completed`); does not see DevOps arc missions (arc not entered).

---

### UC-026 — Alice: DevOps progress

**Actor:** Alice  
**Requires:** UC-013, UC-018  
DevOps list per updated seed; **global-hidden** not listed until unlocked.

---

### UC-027 — Alice: Unlock global-hidden

**Actor:** Alice  
**Requires:** UC-019, UC-026  
Submit `UNLOCK-BLINDFOLD` → global-hidden appears `active`.

---

### UC-028 — Alice: Complete remote-access

**Actor:** Alice  
**Requires:** UC-021  
Can complete **remote-access** when listed and code matches (no separate completion prereqs).

---

### UC-029 — Charlie: Partial DevOps progress

**Actor:** Charlie  
**Requires:** UC-013, UC-021  
Listed missions can be completed with correct code; unlisted missions remain hidden.

---

### UC-031 — Bob: All missions completed

**Actor:** Bob  
**Requires:** UC-013, UC-018  
All missions `completed`; can view all captured completion codes.

---

### UC-032 — identify-the-traitor lists after DevOps prerequisites

**Actor:** Agent (e.g. Bob path)  
**Requires:** UC-015, UC-024  
**identify-the-traitor** appears when **read-the-manual** and **remote-access** are both `completed` (`mission_list_requires`).

---

## Operator progress (read-only V1)

Operator-facing status is **derived** for display (not stored):

| Display | Meaning |
|---------|---------|
| **complete** | `agent_mission_status.status = completed` |
| **active** | `agent_mission_status.status = active` |
| **not started** | No status row for this mission |

### UC-033 — Operator access (`is_operator`)

**Actor:** Operator  
**Requires:** UC-007  
Only `users.is_operator = 1` may access operator routes. Same Google OAuth as agents.

---

### UC-034 — Operator: list story arcs

**Actor:** Operator  
**Requires:** UC-033  
Show all groups. List **Orientation** **last** (bottom of page).

---

### UC-035 — Operator: list missions for an arc

**Actor:** Operator  
**Requires:** UC-034  
For a selected group, list all missions (`missions.group_id`).

---

### UC-036 — Operator: mission progress grid

**Actor:** Operator  
**Requires:** UC-035, UC-012  
For a selected mission, list agents with status on missions in that arc (or all users for global `open` missions — implementation TBD).

---

### UC-037 — Diana: operator sees orientation progress only

**Actor:** Operator  
**Requires:** UC-036  
Diana has no DevOps status rows until she enters that arc.

---

## Out of scope for this list (V1)

Per [01-overview.md](01-overview.md): faculty wizard, story templates, audit log, per-agent keyed codes, in-app operator **configuration**, operator CLI helpers (later).
