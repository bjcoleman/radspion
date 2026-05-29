# Agent experience

## Sign-in

- **New agents:** submit a registration access code (trim whitespace; match is case-sensitive), then Google OAuth (any Google account).
- **Returning agents:** Google OAuth only.
- First sign-in creates the agent and adds them to **Orientation** (campus-wide group).
- After login (and immediately when roster membership changes), the app **syncs** `agent_mission_status` so the mission list is current. A listable `open` mission without an `active` row is a system error.

## Groups

Agents see missions where they are in `group_members` for `missions.group_id`. Class missions require a class roster row; **Orientation** missions are available to every signed-in agent.

## Listing (`missions.access_rule`)

A mission is added to the roster either by **redeeming an unlock code** (`unlock_code`) or **automatically after completing prerequisite missions** (`requires_complete`). Those two mechanisms are never combined on the same mission.

| Rule | Behavior |
|------|----------|
| `open` | On dashboard when in group (sync ensures `active` row) |
| `unlock_code` | After `mission_unlock_codes` redeemed |
| `requires_complete` | After all `mission_list_requires` missions completed |

## Mission detail

- **Mission Brief** from `brief_path` when the mission is on the agent’s list.
- **Debrief** from `debrief_path` only after **completed**.
- After **completed**, show captured value from `missions.completion_code` (never expose to `active` missions in API).

## Completion

1. Agent in mission’s group; mission on status list.
2. **`mission_complete_requires`** satisfied — else generic “not yet”.
3. Input matches **`completion_code`** — else “not recognized”.
4. `agent_mission_status.status = completed`; sync list for other missions.

## Interactive actions (hybrid SSR + JSON)

Pages are **Flask + Jinja** (dashboard, mission detail). Code validation, unlock, and field submission call the **JSON API** under `/api/` with the same session cookie (except access, which is pre-signup) so the browser can run the secure-channel modal (progress animation) and render outcome-specific copy without a full page reload.

Canonical request/response shapes: [`docs/api.yaml`](../api.yaml). Static mockups in `docs/ui/` **hard-code** modal outcomes (no `fetch`); production uses `RadspionTransmission.transmit()` against these endpoints.

Business failures return **HTTP 200** with an `outcome` field (invalid code, not cleared, not yet) so the modal always completes its animation before showing the result.

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

**Response** (`outcome` discriminates UI branch):

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Valid code for a mission in the agent’s group; status row created | `mission`: `{ "title", "slug", "group_name" }` — show in modal; roster updates on OK |
| `invalid` | Code not found | Optional `message` — no mission hints (UC-020) |
| `not_cleared` | Code exists but agent not in mission’s group | Stealth-style optional `message` |

**HTTP 401** when not signed in.

### `POST /api/missions/<slug>/submit`

**Auth:** signed-in agent (session cookie).

**Path:** mission `slug` (e.g. `read-the-manual`).

**Request:** `{ "completion_code": "..." }`

**Response:**

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Code matches; complete prereqs met; mission marked completed | `new_missions`: array of `{ "title", "slug", "group_name" }` for missions that became listable (may be **empty**) |
| `invalid` | Code wrong | Optional generic `message` |
| `not_yet` | Complete prereqs not met | Stealth-style optional `message` |

**HTTP 401** when not signed in. **HTTP 404** when the slug is unknown or the mission is not on the agent’s roster.

**Success UX fork:**

- `new_missions` **empty** — congratulate; **OK** → mission detail **completed** view (debrief).
- `new_missions` **non-empty** — congratulate; list each new mission (title, slug, group name); **OK** → same completed view (agent reads debrief; new missions appear on roster after sync).

Unlock success always includes the **one** unlocked mission in `mission`. Completion success may surface **zero or more** newly listable missions after sync (missions that use `requires_complete` and whose list prerequisites were just satisfied).
