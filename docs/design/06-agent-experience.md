# Agent experience

## Sign-in

- Agents sign in with Google OAuth (any Google account).
- First sign-in creates the agent (`users` row).
- After login, the app **syncs** `agent_mission_status` so the mission list is current. A listable `open` mission without an `active` row is a system error.

## Groups (story arcs)

The dashboard groups missions by story arc (`groups.name` via `missions.group_id`). Collapsible sections help agents navigate many missions. Visibility within a section depends on `access_rule` and progress — not group membership.

## Listing (`missions.access_rule`)

A mission is added to the dashboard either by **submitting listing data** (`unlock_code` missions) or **automatically after completing prerequisite missions** (`requires_complete`). Those two mechanisms are never combined on the same mission.

| Rule | Behavior |
|------|----------|
| `open` | On dashboard for any signed-in agent (sync ensures `active` row) |
| `unlock_code` | After matching data is submitted via `mission_unlock_codes` |
| `requires_complete` | After all `mission_list_requires` missions completed |

Missions that are not yet listable are **not shown** on the dashboard.

## Mission detail

- **Mission Brief** from `missions.brief_markdown` when the mission is on the agent’s list and `active`.
- **Debrief** from `missions.debrief_markdown` only after **completed**.
- After **completed**, show captured value from `missions.completion_code` (never expose to `active` missions in API).

## Submitting data

Agents submit **field data** from the signed-in header on any agent page. The server resolves each string as either:

1. **Listing data** — matches `mission_unlock_codes` (checked first), or
2. **Completion data** — matches `missions.completion_code` for a mission that is **`active`** on the agent’s list.

Unknown data, wrong data, and completion data for a mission not yet on the list all return the same **`invalid`** outcome (no mission hints).

After a successful completion, listing sync runs for `requires_complete` missions (UC-024).

## Interactive actions (hybrid SSR + JSON)

Pages are **Flask + Jinja** (dashboard, mission detail). Data submission calls **`POST /api/submit`** with the session cookie. The browser runs a secure transmission modal (progress animation, then request), then either shows an outcome modal or redirects.

Canonical request/response shapes: [`docs/api.yaml`](../api.yaml). Static mockups in `docs/ui/` **hard-code** modal outcomes (no `fetch`).

Business failures return **HTTP 200** with `outcome: invalid` so the modal always completes its animation before showing the result.

### Data links (`GET /link/<token>`)

**Auth:** none to view; submission requires a signed-in agent.

QR codes and handouts may link to `https://…/link/<token>` where `<token>` is URL-encoded field data. Anonymous visitors stage `pending_submit_data` in session (and in OAuth pending state) until they sign in.

- **Signed in:** confirm on the link page → `POST /api/submit` (transmission modal).
- **Signed out:** Sign in with Google → after OAuth, the server submits pending data and redirects to the dashboard with a staged modal result.

### `POST /api/submit`

**Auth:** signed-in agent (session cookie).

**Request:** `{ "data": "..." }`

**Response:** [`SubmitDataResponse`](../api.yaml) — `outcome`, optional `message`, `new_missions`, and on success `kind` (`list` | `complete`) plus `mission_slug` when `kind` is `complete`.

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Valid listing data newly listed one or more missions, **or** valid completion data marked a mission complete | `kind`, `new_missions` (may be empty), `mission_slug` when complete |
| `already_done` | Listing data but every matching mission already on the list, **or** completion data for an already completed mission | `new_missions`: `[]`; optional `message` |
| `invalid` | Unknown data, wrong data, or completion data for a mission not on the agent’s list | `message` — generic; no mission hints |

**HTTP 401** when not signed in.

Listing success creates an `active` row for each matching `unlock_code` mission with no status row yet. The same listing string may appear on multiple missions.

### Success UX

1. Progress animation runs, then `POST /api/submit`.
2. On **`success`**, the server stages a one-shot result in session; the client navigates to the **dashboard** (`kind: list`) or **mission detail** (`kind: complete`).
3. The destination page shows the success outcome modal directly (no second animation).

### Error UX

On **`invalid`** or **`already_done`**, show the outcome modal on the **current page**; dismiss without navigation.
