# Agent experience

## Sign-in

- **New agents:** submit a registration access code (trim whitespace; match is case-sensitive), then Google OAuth (any Google account).
- **Returning agents:** Google OAuth only.
- First sign-in creates the agent (`users` row).
- After login, the app **syncs** `agent_mission_status` so the mission list is current. A listable `open` mission without an `active` row is a system error.

## Groups (story arcs)

The dashboard groups missions by story arc (`groups.name` via `missions.group_id`). Collapsible sections help agents navigate many missions. Visibility within a section depends on `access_rule` and progress — not group membership.

## Listing (`missions.access_rule`)

A mission is added to the dashboard either by **redeeming an unlock code** (`unlock_code`) or **automatically after completing prerequisite missions** (`requires_complete`). Those two mechanisms are never combined on the same mission.

| Rule | Behavior |
|------|----------|
| `open` | On dashboard for any signed-in agent (sync ensures `active` row) |
| `unlock_code` | After `mission_unlock_codes` redeemed |
| `requires_complete` | After all `mission_list_requires` missions completed |

Missions that are not yet listable are **not shown** on the dashboard.

## Mission detail

- **Mission Brief** from `missions.brief_markdown` when the mission is on the agent’s list.
- **Debrief** from `missions.debrief_markdown` only after **completed**.
- After **completed**, show captured value from `missions.completion_code` (never expose to `active` missions in API).

## Completion

1. Mission on status list (`active`).
2. Input matches **`completion_code`** — else “not recognized”.
3. `agent_mission_status.status = completed`; sync list for other missions.

## Interactive actions (hybrid SSR + JSON)

Pages are **Flask + Jinja** (dashboard, mission detail). Code validation, unlock, and field submission call the **JSON API** under `/api/` with the same session cookie (except access, which is pre-signup) so the browser can run the secure-channel modal (progress animation) and render outcome-specific copy without a full page reload.

Canonical request/response shapes: [`docs/api.yaml`](../api.yaml). Static mockups in `docs/ui/` **hard-code** modal outcomes (no `fetch`); production uses `RadspionTransmission.transmit()` against these endpoints.

Business failures return **HTTP 200** with an `outcome` field (invalid code) so the modal always completes its animation before showing the result.

### `POST /api/access`

**Auth:** none (prospective agent on landing page).

**Request:** `{ "access_code": "..." }`

**Response:**

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Row in `registration_access_codes` | Session flag set for signup OAuth (UC-006); modal → Continue with Google |
| `invalid` | Code not found | Optional `message` — generic only |

### `POST /api/unlock`

**Auth:** signed-in agent (session cookie).

**Request:** `{ "unlock_code": "..." }`

**Response:** same shape as submit — [`MissionListResponse`](../api.yaml) (`outcome`, optional `message`, `new_missions`).

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Valid code; one or more matching missions newly listed | `new_missions`: array of `{ "title", "slug", "group_name" }` — one or many when the code is shared |
| `already_done` | Valid code; every matching mission already on the agent's list (`active` or `completed`) | `new_missions`: `[]`; optional `message` |
| `invalid` | Code not found | Optional `message` — no mission hints (UC-020) |

**HTTP 401** when not signed in.

Redeem creates an `active` row for each matching `unlock_code` mission that has no status row yet. The same `unlock_code` value may appear on multiple missions.

### `POST /api/missions/<slug>/submit`

**Auth:** signed-in agent (session cookie).

**Path:** mission `slug` (e.g. `es-alpha`).

**Request:** `{ "completion_code": "..." }`

**Response:** same shape as unlock — [`MissionListResponse`](../api.yaml).

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Code matches; mission marked `completed`; listing sync ran | `new_missions`: array of missions that became listable (may be **empty**) |
| `already_done` | Mission already `completed` for this agent (re-submit) | `new_missions`: `[]`; optional `message` |
| `invalid` | Code wrong | Optional generic `message` |

**HTTP 401** when not signed in. **HTTP 404** when the slug is unknown or the mission is not on the agent’s list.

**Success UX fork** (unlock and submit share the same modal branches):

- `new_missions` **empty** — unlock: confirm code accepted (nothing new); submit: congratulate completion; **OK** → dashboard refresh or mission detail **completed** view (debrief).
- `new_missions` **non-empty** — list each new mission (title, slug, group name); **OK** → dashboard refresh (unlock) or completed view (submit).

**Already done UX:** show optional `message`; **OK** dismisses without changing the list.

Unlock and submit both return **`new_missions`** for missions newly added to the dashboard. A mission can only already be listed if the agent unlocked or completed it (or sync listed an `open` / `requires_complete` mission) — hence the shared `already_done` outcome.
