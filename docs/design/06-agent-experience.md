# Agent experience

## Clearance and data

Agents interact with Radspion through **two channels** — clearance and data. They use different controls, different verbs, and different transmission animations.

| Channel | Purpose | API |
|---------|---------|-----|
| **Clearance** | List new mission(s) on the dashboard | `POST /api/unlock` with `unlock_code` |
| **Data** | Mark an **active** mission **completed** | `POST /api/missions/<slug>/submit` with `completion_code` |

### Clearance codes

- **Format (convention):** letters (`A–Z`, `a–z`), digits (`0–9`), and hyphen (`-`) only. Human-readable strings are encouraged (e.g. `RADSPION-QR-TRAINING`). No spaces.
- **Source:** mission briefs, QR codes, field handouts, campus contacts, course assignments (LMS).
- **Effect:** Command **grants clearance** and lists every matching mission that is not already on the agent's dashboard. One clearance code may match **multiple** missions.
- **Minimum outcome:** a successful clearance request always lists at least one new mission, unless the agent already had clearance for every match (`already_done`).

### Data

- **Format:** any text the mission author defines — including spaces, punctuation, Unicode, and **newlines** (e.g. JSON, hex, prose).
- **Comparison:** case-sensitive exact match after **leading and trailing** whitespace is trimmed on submit. Internal newlines and spacing must match the stored value.
- **After completion:** the submitted value is shown in agency archives on the completed mission view.

### Orientation

The **Orientation** story arc is public and teaches this model. Orientation **data** values are intentionally **not** shaped like clearance codes.

## Sign-in

- Agents sign in with Google OAuth (any Google account).
- First sign-in creates the agent (`users` row).
- After login, the app **syncs** `agent_mission_status` so the mission list is current. A listable `open` mission without an `active` row is a system error.

## Layout

### Site header

The agent header is **sticky** on dashboard and mission pages. It includes brand, agent identity, a **clearance** field with **Request**, and sign out. The Mission Dashboard does **not** include a second clearance field.

### Mission detail

- **Mission Brief** from `missions.brief_markdown` when the mission is on the agent's list.
- **Data** panel on active missions — multi-line input and **Submit data**.
- **Debrief** from `missions.debrief_markdown` only after **completed**.
- After **completed**, show the captured value from `missions.completion_code` in agency archives (never expose to `active` missions in API).

## Groups (story arcs)

The dashboard groups missions by story arc (`groups.name` via `missions.group_id`). Collapsible sections help agents navigate many missions. Visibility within a section depends on `access_rule` and progress — not group membership.

A story arc's **first mission** (clear title, e.g. `LT: Overview`) carries arc onboarding in its Mission Brief: premise, prerequisites, estimated effort, and links. There is no separate storyline overview page.

## Listing (`missions.access_rule`)

A mission is added to the dashboard by **granting clearance** (`unlock_code` in the database), by **`open`** listing, or **automatically after completing prerequisite missions** (`requires_complete`). Those mechanisms are never combined on the same mission.

| Rule | Behavior |
|------|----------|
| `open` | On dashboard for any signed-in agent (sync ensures `active` row). Used sparingly — walk-up / escape-room style content with minimal prerequisites. |
| `unlock_code` | After clearance is granted via `mission_unlock_codes` |
| `requires_complete` | After all `mission_list_requires` missions completed |

Missions that are not yet listable are **not shown** on the dashboard.

## Completion

1. Mission on status list (`active`).
2. Submitted data matches **`completion_code`** — else invalid outcome.
3. `agent_mission_status.status = completed`; sync list for other missions.

## Interactive actions (hybrid SSR + JSON)

Pages are **Flask + Jinja** (dashboard, mission detail). Clearance and data call the **JSON API** under `/api/` with the same session cookie so the browser can run a transmission modal (progress animation) and render outcome-specific copy without a full page reload.

Canonical request/response shapes: [`docs/api.yaml`](../api.yaml). Static mockups in `docs/ui/` **hard-code** modal outcomes (no `fetch`); production uses `RadspionTransmission.transmit()` against these endpoints.

Business failures return **HTTP 200** with an `outcome` field (invalid) so the modal always completes its animation before showing the result.

### Transmission modals

Clearance and data use **distinct** modal presets — different titles, step copy, progress styling, and success/failure messages. Both run the same four-step timing (~3 seconds with jitter) unless the user prefers reduced motion.

| Preset | Typical success copy |
|--------|----------------------|
| Clearance | Clearance granted; new mission(s) listed |
| Data | Data accepted; mission completed |

### Clearance links (`GET /unlock/<token>`)

**Auth:** none to view; granting clearance requires a signed-in agent.

QR codes and field handouts link to `https://…/unlock/<token>` where `<token>` is the URL-encoded clearance code. The landing page confirms clearance before calling `POST /api/unlock`.

- **Signed in:** confirm → clearance transmission modal.
- **Signed out:** Sign in with Google → after OAuth, the server grants the staged clearance and redirects to the dashboard with the same clearance modal.

### `POST /api/unlock`

**Auth:** signed-in agent (session cookie).

**Request:** `{ "unlock_code": "..." }`

**Response:** [`MissionListResponse`](../api.yaml) (`outcome`, optional `message`, `new_missions`).

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Valid clearance; one or more matching missions newly listed | `new_missions`: array of `{ "title", "slug", "group_name" }` — one or many when the code is shared |
| `already_done` | Valid clearance; every matching mission already on the agent's list (`active` or `completed`) | `new_missions`: `[]`; optional `message` |
| `invalid` | Clearance not found | Optional `message` — no mission hints (UC-020) |

**HTTP 401** when not signed in.

Granting clearance creates an `active` row for each matching `unlock_code` mission that has no status row yet. The same `unlock_code` value may appear on multiple missions.

### `POST /api/missions/<slug>/submit`

**Auth:** signed-in agent (session cookie).

**Path:** mission `slug` (e.g. `es-alpha`).

**Request:** `{ "completion_code": "..." }`

**Response:** [`MissionListResponse`](../api.yaml).

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Data matches; mission marked `completed`; listing sync ran | `new_missions`: array of missions that became listable (may be **empty**) |
| `already_done` | Mission already `completed` for this agent (re-submit) | `new_missions`: `[]`; optional `message` |
| `invalid` | Data does not match | Optional generic `message` |

**HTTP 401** when not signed in. **HTTP 404** when the slug is unknown or the mission is not on the agent's list.

**Success UX fork:**

- `new_missions` **empty** — clearance: confirm clearance recorded (nothing new); data: congratulate completion; **OK** → dashboard refresh or mission detail **completed** view (debrief).
- `new_missions` **non-empty** — list each new mission (title, slug, group name); **OK** → dashboard refresh (clearance) or completed view (data).

**Already done UX:** show optional `message`; **OK** dismisses without changing the list.

Clearance and data submission both return **`new_missions`** for missions newly added to the dashboard after the action.
