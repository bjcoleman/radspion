# Agent experience

## Clearance and data

Agents interact with Radspion through **two channels** — clearance and data. They use different controls, different verbs, and different transmission animations.

| Channel | Purpose | API |
|---------|---------|-----|
| **Clearance** | List new mission(s) on the dashboard | `POST /api/clearance` with `clearance_code` |
| **Data** | Mark an **active** mission **completed** | `POST /api/missions/<slug>/submit` with `completion_data` |

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
- First sign-in creates the agent (`users` row) with default **`codename`** (`AGENT0001`, `AGENT0002`, … from `codename_counter`) and **`created_at`** (first sign-in time).
- After login, the app **syncs** `agent_mission_status` so the mission list is current. A listable `open` mission without an `active` row is a system error.

## Layout

Static mockups in [`docs/ui/`](../ui/README.md) are the reference for agent-facing copy. Production templates and API `message` fields should match.

### Site header

The agent header is **sticky** on dashboard, mission, and Personnel File pages. It includes brand, the agent's **codename** (link), a **clearance** field, **Request Access**, and sign out (text-only control, not a filled button).

| Control | Copy / behavior |
|---------|-----------------|
| Codename link | Agent `codename` → `GET /agent/personnel`; on the Personnel File page the link uses `--current` and `aria-current="page"` |
| Clearance input placeholder | `Clearance code` |
| Submit clearance | **Request Access** |

Clearance works from the header on every page that includes it (dashboard, mission detail, Personnel File). The Mission Dashboard does **not** include a second clearance field in the body.

### Agent Personnel File

Route: **`GET /agent/personnel`** (signed-in only). Mockup: [`agent-personnel-file.html`](../ui/agent-personnel-file.html).

| Element | Copy |
|---------|------|
| Page title | **Agent Personnel File** |
| Back nav | **← Mission Dashboard** (top and bottom) |
| Stamp | Confidential / your-eyes-only image (decorative) |

**Personal Information**

| Field | Source | Notes |
|-------|--------|-------|
| Sign-in name | `users.display_name` | Read-only |
| Email | `users.email` | Read-only; monospace |
| Codename | `users.codename` | Editable; **Update** calls `POST /api/codename` |
| Codename hint | — | *Your codename should be appropriate for public display (4–20 characters).* |
| Recruited on | `users.created_at` | Formatted date (`<time>`) |
| Scope note | — | *Your sign-in name and email are retained only for Radspion Command operations.* |

**Field Status** — counts from `agent_mission_status`: **Missions completed** (`completed`), **Active missions** (`active`).

**Service Record** — scrollable list, newest first. Verbs and sources: [02-entities.md](02-entities.md) (*Service record*). Each row: date, verb, detail (mission title or *Personnel file opened* for **Enlisted**).

**Codename update** — separate outcome modal (same visual chrome as transmission modals; no progress animation). Client validates unchanged codename and length before calling the API.

| Case | Outcome header | Message |
|------|----------------|---------|
| Updated | **Codename** / **Updated** | Your codename has been updated. |
| Unchanged (client only) | **Codename** / **Unchanged** | Your codename is unchanged. |
| Invalid length | **Verification** / **Failed** | Codenames must be 4–20 characters. |
| Duplicate | **Verification** / **Failed** | Another agent is using this codename. |
| Network / server error | **Verification** / **Failed** | Update could not be completed. Try again. |

Success **OK** reloads the page (header codename and form value). Invalid **OK** dismisses the modal; the input keeps the typed value.

### Mission Dashboard

| Element | Copy |
|---------|------|
| Heading | **Mission Dashboard** |
| Toggle | **Show completed missions** |
| Lede | Missions are assigned by Command, or listed when you are granted clearance for a new assignment. |

Missions are grouped by story arc (`groups.name`). Collapsible sections; completed missions may be hidden via the toggle.

### Mission detail (active)

- **Mission Brief** from `missions.brief_markdown`.
- **Recovered Data** panel — same title as the completed archives section; lede and control make clear this is for submission.

| Element | Copy |
|---------|------|
| Panel title | **Recovered Data** |
| Lede | Enter the data you recovered from this mission. Spacing and line breaks must be exact. |
| Input | Multi-line textarea; placeholder `Field data` |
| Submit | **Submit data** |

Paste from clipboard must preserve internal spacing and line breaks. Only leading and trailing whitespace is trimmed on submit.

### Mission detail (completed)

Section order: **Recovered Data** (agency archives) → **Mission Debrief** (expanded) → **Mission Brief** (collapsed).

| Element | Copy |
|---------|------|
| Archives title | **Recovered Data** |
| Archives lede | The following data is secured in agency archives. |
| Display | Stored `completion_data` (recovered data) in a `<pre>` block; multi-line; height fits content |
| Copy control | Clipboard button on the archives block |

Never expose `completion_data` to **active** missions in API or UI.

### Site footer (agent pages)

Single row: **What is Radspion?** · **Moravian University · Educational Use** · **Privacy Policy**

## Groups (story arcs)

The dashboard groups missions by story arc (`groups.name` via `missions.group_id`). Collapsible sections help agents navigate many missions. Visibility within a section depends on `access_rule` and progress — not group membership.

A story arc's **first mission** (clear title, e.g. `LT: Overview`) carries arc onboarding in its Mission Brief: premise, prerequisites, estimated effort, and links. There is no separate storyline overview page.

## Listing (`missions.access_rule`)

A mission is added to the dashboard by **granting clearance** (`clearance_code` in the database), by **`open`** listing, or **automatically after completing prerequisite missions** (`requires_complete`). Those mechanisms are never combined on the same mission.

| Rule | Behavior |
|------|----------|
| `open` | On dashboard for any signed-in agent (sync ensures `active` row). Used sparingly — walk-up / escape-room style content with minimal prerequisites. |
| `clearance_code` | After clearance is granted via `mission_clearance_codes` |
| `requires_complete` | After all `mission_list_requires` missions completed |

Missions that are not yet listable are **not shown** on the dashboard.

## Completion

1. Mission on status list (`active`).
2. Submitted data matches **`completion_data`** — else invalid outcome.
3. `agent_mission_status.status = completed`; sync list for other missions.

## Interactive actions (hybrid SSR + JSON)

Pages are **Flask + Jinja** (dashboard, mission detail, Personnel File). Clearance, data, and codename updates call the **JSON API** under `/api/` with the same session cookie so the browser can show outcome modals without a full page reload until the agent dismisses success.

Canonical request/response shapes: [`docs/api.yaml`](../api.yaml). Static mockups in `docs/ui/` **hard-code** modal outcomes (no `fetch`); production uses `RadspionTransmission.transmit()` against these endpoints.

Business failures return **HTTP 200** with an `outcome` field (invalid) so the modal always completes its animation before showing the result.

### Transmission modals

Clearance and data use **distinct** modal presets — different progress titles, step copy, outcome headers, and messages. Agent-facing copy uses **clearance** / **data** vocabulary (not legacy terms or “validate”). Honor `prefers-reduced-motion` (skip animation; show outcome immediately).

**Shared outcome chrome**

- Progress-phase title uses accent color (Radspion gold).
- Outcome: Radspion mark left of a **two-line stacked** heading; mark opacity by outcome — **100%** success, **75%** already done, **55%** invalid.
- New missions: grouped under story-arc headings; each line **Title** `(slug)` in monospace.
- Dismiss: gold **OK** button.

**Clearance preset** (~3s after intro hold)

| Phase | Copy |
|-------|------|
| Progress title | **Requesting clearance** |
| Intro | Initializing secure channel… |
| Steps | Initiating secure connection… → Establishing agent identity… → Transferring clearance code… → Checking agency records… |
| Success header | **Clearance** / **Granted** |
| Success body | Your request for further clearance was approved, and Command has added the following mission(s) to your dashboard: — then mission list (singular/plural as needed) |
| Invalid header | **Verification** / **Failed** |
| Invalid body | Command could not verify this clearance code against agency records. Check the code and try again. |
| Already done header | **Previously** / **Granted** |
| Already done body | You have already been granted this clearance. |

**Data preset** (~3.6s total)

| Phase | Copy |
|-------|------|
| Progress title | **Transmitting field data** |
| Prep step | Compressing and Encrypting data — same progress bar fills 0→100% (~600ms), then resets |
| Steps | Initiating secure connection… → Establishing agent identity… → Transferring field data… → Checking agency records… (~3s) |
| Success header | **Data** / **Accepted** |
| Success body | Lab verification confirmed your field data. This mission is now marked as completed. |
| Debrief line | Read the debrief for your after-action summary. |
| Success + missions | The data you recovered has produced additional missions: — then mission list — then debrief line |
| Invalid header | **Verification** / **Failed** |
| Invalid body | We received your transmission, but the recovered data does not match mission parameters. Continue your fieldwork and submit again when you have the correct value. |

### Clearance links (`GET /clearance/<token>`)

**Auth:** none to view; granting clearance requires a signed-in agent.

QR codes and field handouts link to `https://…/clearance/<token>` where `<token>` is the URL-encoded clearance code. The landing page confirms clearance before calling `POST /api/clearance`.

- **Signed in:** confirm → clearance transmission modal.
- **Signed out:** Sign in with Google → after OAuth, the server grants the staged clearance and redirects to the dashboard with the same clearance modal.

### `POST /api/clearance`

**Auth:** signed-in agent (session cookie).

**Request:** `{ "clearance_code": "..." }`

**Response:** [`MissionListResponse`](../api.yaml) (`outcome`, optional `message`, `new_missions`).

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Valid clearance; one or more matching missions newly listed | `new_missions`: array of `{ "title", "slug", "group_name" }` — one or many when the code is shared |
| `already_done` | Valid clearance; every matching mission already on the agent's list (`active` or `completed`) | `new_missions`: `[]`; optional `message` |
| `invalid` | Clearance not found | Optional `message` — no mission hints (UC-020) |

**HTTP 401** when not signed in.

Granting clearance creates an `active` row for each matching `clearance_code` mission that has no status row yet. The same `clearance_code` value may appear on multiple missions.

### `POST /api/codename`

**Auth:** signed-in agent (session cookie).

**Request:** `{ "codename": "..." }`

**Response:** [`CodenameResponse`](../api.yaml) — not `MissionListResponse`.

| `outcome` | When | Response body |
|-----------|------|----------------|
| `success` | Valid codename; row updated, or trimmed value equals current codename (no write) | `message`: *Your codename has been updated.* |
| `invalid` | Length out of range, or another agent has this codename (case-sensitive exact match) | `message`: see codename update table under *Agent Personnel File* |

**HTTP 400** when `codename` is missing or empty after trim. **HTTP 401** when not signed in.

### `POST /api/missions/<slug>/submit`

**Auth:** signed-in agent (session cookie).

**Path:** mission `slug` (e.g. `es-alpha`).

**Request:** `{ "completion_data": "..." }`

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

On **Mission Dashboard** and **Agent Personnel File**, clearance **success** **OK** reloads the page (so the mission list or service record reflects new listings). Invalid and already-done outcomes dismiss without reload. Other pages keep their existing OK behavior (e.g. clearance landing → dashboard).

**Already done UX:** show optional `message`; **OK** dismisses without changing the list.

Clearance and data submission both return **`new_missions`** for missions newly added to the dashboard after the action.
