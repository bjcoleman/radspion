# Radspion UI mockups (V1)

Static HTML/CSS prototypes for **Flask + Jinja SSR**. Each file is a fixed snapshot—no backend. Modal animations use **inline scripts** on dedicated outcome pages; production will use server-rendered pages plus `fetch` to the JSON API ([06-agent-experience.md](../design/06-agent-experience.md), [api.yaml](../api.yaml)). Personas and seed states: [05-testing-storyline.md](../design/05-testing-storyline.md) (Alice mid-progress on **Testing Storyline**).

**Design reference:** [06-agent-experience.md](../design/06-agent-experience.md) (clearance + data) · [use-cases.md](../design/use-cases.md) · [05-testing-storyline.md](../design/05-testing-storyline.md) · [COLOR_USAGE.md](COLOR_USAGE.md)

**Assets:** styles in [`css/radspion.css`](css/radspion.css) are kept in sync with production [`src/radspion/static/css/radspion.css`](../../src/radspion/static/css/radspion.css) (mockup rules + app-only rules for flash, content pages, disabled controls). Logos in [`logos/`](../../logos/). Mission brief and debrief copy is **inlined in HTML** on mission detail mockups (production loads markdown from the database).

**Target layout:** Sticky site header with **Clearance** field + **Request**; Mission Dashboard **without** a clearance field; mission detail **Data** panel with **textarea** + **Submit data**; distinct clearance vs data transmission modals.

**Sample data alignment:** Story arcs **Orientation** and **Testing Storyline** (`es-*` missions); **`unlock_code`** or **`requires_complete`** listing — never both on one mission.

**Mock vs production:** Modal outcome pages hard-code copy and animation; no `fetch`. Production will call `POST /api/unlock` (clearance) and `POST /api/missions/<slug>/submit` (data) per [`api.yaml`](../api.yaml). API `outcome` values are `success`, `invalid`, `already_done` (shared [`MissionListResponse`](../api.yaml) with `new_missions`). Clearance success may list one or many missions; data submit **success-unlocks** simulates `success` with a non-empty `new_missions` array.

---

## How to use this folder

1. Open HTML files in a browser (double-click or a local static server).
2. Open the dedicated **modal outcome** HTML files to preview transmission animations and dialogs.
3. Iterate on layout and copy before implementing Jinja templates + JSON endpoints.

---

## File index

### Errors

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [not-found.html](not-found.html) | done | HTTP 404 — unverified path / lost signal | — |

### Auth & landing

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [index.html](index.html) | done | Signed-out landing; Sign in with Google | UC-006 |
| [secure_login_modal.html](secure_login_modal.html) | done | Landing + Google sign-in modal | UC-006 |

### Agent dashboard

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [agent-dashboard.html](agent-dashboard.html) | **update** | Alice; Testing Storyline expanded; sticky header clearance | UC-013, UC-019, UC-026 |
| [agent-dashboard-hidden.html](agent-dashboard-hidden.html) | **update** | Same list; **Show completed missions** off | UC-013 |
| [agent-dashboard-unlock-success.html](agent-dashboard-unlock-success.html) | **rename/update** | Clearance granted modal | UC-020, UC-027 |
| [agent-dashboard-unlock-bad-code.html](agent-dashboard-unlock-bad-code.html) | **rename/update** | Invalid clearance modal | UC-020 |

### Mission detail

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [mission-detail-active.html](mission-detail-active.html) | **update** | **Alice / es-beta** active: Brief, Data textarea | UC-009, UC-016, UC-017 |
| [mission-detail-completed.html](mission-detail-completed.html) | **update** | **Alice / es-alpha** completed; agency archives + Debrief | UC-010, UC-018, UC-021 |
| [mission-detail-submit-success.html](mission-detail-submit-success.html) | **update** | Data accepted (no new missions) | UC-021 |
| [mission-detail-submit-success-unlocks.html](mission-detail-submit-success-unlocks.html) | **update** | Submit **es-alpha** success + **es-gamma** listed | UC-021, UC-032 |
| [mission-detail-submit-invalid.html](mission-detail-submit-invalid.html) | **update** | Invalid data | UC-022 |

### Operator (read-only)

| File | Status | Use cases |
|------|--------|-----------|
| [operator-groups.html](operator-groups.html) | TODO | UC-033, UC-034 |
| [operator-group-missions.html](operator-group-missions.html) | TODO | UC-035 |
| [operator-mission-roster.html](operator-mission-roster.html) | TODO | UC-036, UC-037 |

---

## Shared assets

| File | Purpose |
|------|---------|
| [css/radspion.css](css/radspion.css) | Theme, layout, modals, `.outcome-missions` list |
| [COLOR_USAGE.md](COLOR_USAGE.md) | Color roles for mockups |
| [transmission-modal-demo.html](transmission-modal-demo.html) | Browser demo for production `transmission-modal.js` |

---

## Suggested build order

1. `css/radspion.css` — sticky header + clearance field ✓ (target)  
2. Auth landing + modals ✓  
3. `agent-dashboard.html` — header clearance, no dashboard field  
4. `mission-detail-active.html` → completed + data submit outcome pages  
5. Distinct clearance vs data modal mockups  
6. Operator pages (TODO)

---

## Per-page checklist

### Site header (all agent pages)

- Sticky header with clearance input + **Request**
- Agent identity + sign out

### Agent dashboard

- Story-arc sections with collapsible groups; toggle for completed missions.
- **No** clearance field in dashboard body — use header modals (`agent-dashboard-unlock-*.html` until renamed) for clearance outcomes.

### Mission detail (active)

- Mission Brief; **Data** textarea + **Submit data** → open `mission-detail-submit-*.html` for each outcome.

### Mission detail (completed)

- Agency archives (submitted data) → collapsible Mission Debrief (open) → collapsible Mission Brief (closed).
