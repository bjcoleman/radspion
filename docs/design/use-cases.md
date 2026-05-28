# Use cases (V1)

Ordered by **dependency** — build from the top down. Each case lists **Requires** (other UC ids that must work first). Agent scenarios at the end assume the example seed ([04-example-data-walkthrough.md](04-example-data-walkthrough.md), [`src/radspion/sql/seed_example_class.sql`](../../src/radspion/sql/seed_example_class.sql)).

**Reference agents:** Alice, Bob, Charlie, Diana — [05-example-class.md](05-example-class.md). Mission names are **slugs** everywhere (e.g. `read-the-manual`, not numeric ids).

## Resolved decisions

| Topic | Decision |
|-------|----------|
| Who can sign in | Any `@moravian.edu` Google account |
| New agents | Auto-create `users` row; add to **Orientation** `group_members` |
| Campus vs class | **Orientation** group missions for all signed-in agents; class missions need roster row |
| Welcome | Seed includes `basic-training` in **Orientation** |
| Code vs automatic listing | A mission never mixes **`unlock_code`** with **`mission_list_requires`**; sample uses one code-only mission (`global-hidden`) |
| Mission list UX | After login, dashboard shows all missions the agent should have (group + rules + progress) |
| `agent_mission_status` | Keep table **in sync at all times** (login + unlock + complete + roster changes); dashboard reads this table |
| Debrief | Only after mission `completed` |
| Error copy (UC-020, UC-022, UC-023) | Wording TBD — you’ll review per case |
| Web framework | **Flask + Jinja** SSR; JSON API for unlock and mission submit |
| Brief/Debrief paths | Live missions under `content/missions/<slug>/`; example pack under `content/samples/example-class/` (bootstrap copies into live); UI mockups in `docs/ui/` inline HTML snapshots (not separate markdown files) |
| Operator config V1 | SQL/seed only — no in-app mission/roster editor |
| Operator progress V1 | Read-only UI: groups → missions → roster status (`locked` / `active` / `complete`) |
| `users.is_operator` | SQLite `INTEGER` `0`/`1` (app treats as boolean); gates operator routes |
| Sync timing | **Immediate** on `group_members` insert, login, unlock, complete — never deferred |
| Operator “locked” | Roster member, no `agent_mission_status` row (not unlocked / not listable yet) |
| Operator group list | All groups; **Orientation** (campus-wide) section at the **bottom** |
| Roster via SQL | New class member → add to **Orientation** + class group; run sync (CLI helpers later) |

**Sync invariant:** If an agent is in a group and a mission is listable (`open`, or `requires_complete` with prereqs met), an `active` row **must** exist. Missing row in that case is a **bug**, not a UI edge case.

**Why eager sync?** Dashboard and operator views read `agent_mission_status` directly. `unlock_code` missions intentionally have **no row** until redeem — operator sees that as **locked**.

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
Load [`src/radspion/sql/seed_example_class.sql`](../../src/radspion/sql/seed_example_class.sql) for **Orientation** + 220.2 DevOps groups, **six missions**, constraints, and sample `agent_mission_status` rows.

---

### UC-003 — Web app connects to SQLite

**Actor:** Developer  
**Requires:** UC-001  
Application stack connects to the Radspion SQLite database (`PRAGMA foreign_keys = ON` on each connection) using **Flask + Jinja** for pages and JSON endpoints for unlock/submit ([06-agent-experience.md](06-agent-experience.md)).

---

### UC-004 — ORM models match schema

**Actor:** Developer  
**Requires:** UC-003  
Models (or equivalent data layer) for `users` (including `is_operator`), `groups`, `group_members`, `missions`, constraint tables, and `agent_mission_status` with the same semantics as [03-database-schema.md](03-database-schema.md).

---

## Operator configuration (V1, no admin UI)

### UC-005 — Configure a class via SQL

**Actor:** Operator  
**Requires:** UC-001  
Create group, roster, missions, unlock/list/complete constraints, and optional seed progress per [07-operator-setup.md](07-operator-setup.md). When adding a student to a class group, also add them to **Orientation** and ensure status sync runs (UC-012). No in-app wizard in V1.

---

## Authentication

### UC-006 — Sign in with Google OAuth

**Actor:** Agent  
**Requires:** UC-004  
Agent authenticates with Google; app establishes a session tied to a `users` row.

---

### UC-007 — Resolve or provision agent from OAuth

**Actor:** System  
**Requires:** UC-006  
- Reject sign-in if Google email is not `@moravian.edu`.  
- If no `users` row: create one from OAuth profile (`email`, `google_subject_id`, `display_name`).  
- Ensure `group_members` row for **Orientation**.  
- Run mission-status sync (UC-012) before showing the dashboard.

---

## Mission content

### UC-008 — Mission Brief and Debrief on disk

**Actor:** Operator  
**Requires:** UC-002 (for example paths)  
Operator-authored markdown at paths stored on `missions` under `content/missions/<slug>/`. The example-class bootstrap copies from `content/samples/example-class/` and loads `seed_example_class.sql`. UI mockups inline representative brief/debrief in HTML (e.g. `mission-detail-active.html`, `mission-detail-completed.html`) — not one mockup file per mission.

---

### UC-009 — Render Mission Brief

**Actor:** Agent  
**Requires:** UC-006, UC-008  
Agent can view the Brief for a mission they are allowed to see (see UC-012, UC-013).

---

### UC-010 — Render Debrief after completion

**Actor:** Agent  
**Requires:** UC-016  
Agent can view the Debrief only when `agent_mission_status.status = completed` for that mission.

---

## Listing and visibility

### UC-011 — Missions scoped to agent groups

**Actor:** System  
**Requires:** UC-007  
Only missions where the agent has `group_members` for `missions.group_id` are considered (e.g. Diana has no 220.2 DevOps missions).

---

### UC-012 — Sync `agent_mission_status` (immediate)

**Actor:** System  
**Requires:** UC-011  
Keep status rows aligned with listing rules for all of the agent’s groups. Run **immediately** when:

- Agent added to a group (`group_members` insert)
- Agent signs in (UC-007)
- Unlock redeemed (UC-019)
- Mission completed (UC-024)

| `access_rule` | Sync behavior |
|---------------|---------------|
| `open` | `active` row if in group and not yet `completed` — **required**; absence is an error |
| `requires_complete` | `active` row when all `mission_list_requires` are `completed` |
| `unlock_code` | **No row** until redeem (UC-019) — not an error; operator reports as **locked** |

Do not remove rows for completed missions.

---

### UC-013 — Agent mission dashboard

**Actor:** Agent  
**Requires:** UC-012  
After login (post-sync), dashboard lists all `agent_mission_status` rows for missions in the agent’s groups (`active` or `completed`). This is the full set of missions available to work on or review.

---

### UC-014 — List mission after `unlock_code` redeemed

**Actor:** Agent  
**Requires:** UC-013  
For `access_rule = unlock_code`, create `active` status when the agent submits the correct `mission_unlock_codes.unlock_code` (e.g. global-hidden / mission 2).

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
Valid unlock code for a mission in the agent’s group → mission appears on list (`active`). Example: `UNLOCK-BLINDFOLD` for global-hidden.

---

### UC-020 — Redeem unlock code (failure)

**Actor:** Agent  
**Requires:** UC-019  
Invalid unlock code → clear error without revealing mission existence or codes. *(Wording TBD.)*

---

## Completion

### UC-021 — Complete mission (no complete prerequisites)

**Actor:** Agent  
**Requires:** UC-016, UC-017  
Agent submits correct `completion_code` for a mission with no `mission_complete_requires` → `status = completed`. Examples: basic-training; **read-the-manual** once listed.

---

### UC-022 — Reject completion when complete prerequisites not met (stealth)

**Actor:** Agent  
**Requires:** UC-021  
If any `mission_complete_requires` target is not `completed`, reject with a **generic** “not yet” message; inputs stay enabled ([06-agent-experience.md](06-agent-experience.md)).  
Example: Charlie has **remote-access** `active` (listed after learn-the-system) but cannot complete it until **read-the-manual** is `completed` (`mission_complete_requires` on mission 5).

---

### UC-023 — Reject wrong completion code

**Actor:** Agent  
**Requires:** UC-021  
Wrong code → “not recognized” (distinct from stealth prereq failure). *(Wording TBD.)*

---

### UC-024 — Re-sync listing after completion

**Actor:** System  
**Requires:** UC-021, UC-012  
When a mission becomes `completed`, run UC-012 so any newly listable `requires_complete` missions get `active` rows.

---

### UC-015 — List mission after list prerequisites completed

**Actor:** System  
**Requires:** UC-013, UC-024  
For `access_rule = requires_complete`, mission appears on the dashboard when all `mission_list_requires` targets are `completed` (e.g. **remote-access** after learn-the-system; **identify-the-traitor** after read-the-manual and remote-access). Same mechanism as UC-024; listed here as the agent-visible outcome.

---

## Canonical agent scenarios (acceptance)

These validate the full stack against seed data. Mission ids/slugs follow [04-example-data-walkthrough.md](04-example-data-walkthrough.md).

### UC-025 — Diana: orientation only

**Actor:** Diana  
**Requires:** UC-013, UC-011  
Sees basic-training (`active`); does not see 220.2 DevOps missions (not in group 2).

---

### UC-026 — Alice: 220.2 DevOps progress from seed

**Actor:** Alice  
**Requires:** UC-013, UC-018  
Class list includes read-the-manual and learn-the-system `completed`, **remote-access** `active`; **identify-the-traitor** not listed (remote-access not finished). **global-hidden** not listed until unlocked.

---

### UC-027 — Alice: Unlock global-hidden

**Actor:** Alice  
**Requires:** UC-019, UC-026  
Submit `UNLOCK-BLINDFOLD` → global-hidden appears `active`.

---

### UC-028 — Alice: Complete remote-access after read-the-manual

**Actor:** Alice  
**Requires:** UC-021, UC-022  
Can complete **remote-access** because **read-the-manual** is already `completed` (`mission_complete_requires` on mission 5).

---

### UC-029 — Charlie: Stealth block on remote-access

**Actor:** Charlie  
**Requires:** UC-022  
Has **remote-access** on list (`active`, listed via learn-the-system) but submission fails with generic “not yet” until **read-the-manual** is `completed`.

---

### UC-030 — Charlie: Complete read-the-manual when allowed

**Actor:** Charlie  
**Requires:** UC-021  
Can complete **read-the-manual** (no mission_complete_requires targeting mission 3).

---

### UC-031 — Bob: All missions completed

**Actor:** Bob  
**Requires:** UC-013, UC-018  
All six missions `completed`; can view all captured completion codes including orientation and DevOps finale (`identify-the-traitor` / TRAITOR-IDENTIFIED-OK).

---

### UC-032 — identify-the-traitor lists after DevOps prerequisites

**Actor:** Agent (e.g. Bob path)  
**Requires:** UC-015, UC-024  
**identify-the-traitor** appears on the roster only when **read-the-manual** and **remote-access** are both `completed` (`mission_list_requires` on mission 6). No `mission_complete_requires` on that mission — agents cannot see it until those prerequisites are done.

---

## Operator progress (read-only V1)

Operator-facing status is **derived** for display (not stored):

| Display | Meaning |
|---------|---------|
| **complete** | `agent_mission_status.status = completed` |
| **active** | `agent_mission_status.status = active` |
| **locked** | Agent in mission’s group roster, **no status row** (e.g. `unlock_code` not redeemed, or `requires_complete` list prereqs not met) |

Roster = `group_members` for `missions.group_id`. Example: Diana appears on **Orientation** missions; she does **not** appear on 220.2 DevOps mission rosters.

### UC-033 — Operator access (`is_operator`)

**Actor:** Operator  
**Requires:** UC-007  
Only `users.is_operator = 1` may access operator routes (SQLite; ORM may expose this as boolean). Same Google OAuth as agents; enforce on every operator request. *(Preferred: land on operator home after login — not critical.)*

---

### UC-034 — Operator: list groups

**Actor:** Operator  
**Requires:** UC-033  
Show all groups. List **class groups first**; **Orientation** group **last** (bottom of page).

---

### UC-035 — Operator: list missions for a group

**Actor:** Operator  
**Requires:** UC-034  
For a selected group, list all missions (`missions.group_id`).

---

### UC-036 — Operator: mission roster status grid

**Actor:** Operator  
**Requires:** UC-035, UC-012  
For a selected mission, list every agent in that mission’s group roster with status **locked**, **active**, or **complete** (table above).  
Examples from seed: Alice **locked** on global-hidden (no row); Charlie **locked** on identify-the-traitor (no row); Bob **complete** on identify-the-traitor.

---

### UC-037 — Diana: operator sees orientation only

**Actor:** Operator  
**Requires:** UC-036  
On 220.2 DevOps missions, Diana is **not** in the roster. On **Orientation** missions (e.g. basic-training), Diana appears with the same locked/active/complete rules as other orientation members.

---

## Out of scope for this list (V1)

Per [01-overview.md](01-overview.md) out-of-scope list: faculty wizard, story templates, audit log, per-agent keyed codes, in-app operator **configuration** (roster/mission editor), operator CLI helpers (later).
