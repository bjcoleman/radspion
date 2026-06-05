# Radspion UI mockups (V1)

Static HTML/CSS prototypes for **Flask + Jinja SSR**. Each file is a fixed snapshot—no backend. Modal animations use **inline scripts** on dedicated outcome pages; production will use server-rendered pages plus `fetch` to the JSON API ([06-agent-experience.md](../design/06-agent-experience.md), [api.yaml](../api.yaml)). Personas and seed states: [05-testing-storyline.md](../design/05-testing-storyline.md) (Alice mid-progress on **Testing Storyline**).

**Design reference:** [06-agent-experience.md](../design/06-agent-experience.md) (clearance + data) · [use-cases.md](../design/use-cases.md) · [05-testing-storyline.md](../design/05-testing-storyline.md) · [COLOR_USAGE.md](COLOR_USAGE.md)

**Assets:** styles in [`css/radspion.css`](css/radspion.css) are kept in sync with production [`src/radspion/static/css/radspion.css`](../../src/radspion/static/css/radspion.css) (mockup rules + app-only rules for flash, content pages, disabled controls). Logos in [`logos/`](../../logos/). Mission brief and debrief copy is **inlined in HTML** on mission detail mockups (production loads markdown from the database).

**Target layout:** Sticky site header with **Clearance** field + **Request Access**; Mission Dashboard **without** a body clearance field; mission detail **Data** panel with **textarea** + **Submit data**; distinct clearance vs data transmission modals.

**Sample data alignment:** Story arcs **Orientation** and **Testing Storyline** (`es-*` missions); **`clearance_code`** or **`requires_complete`** listing — never both on one mission.

**Mock vs production:** Modal outcome pages hard-code copy and animation; no `fetch`. Production will call `POST /api/clearance` (clearance) and `POST /api/missions/<slug>/submit` (data) per [`api.yaml`](../api.yaml). API `outcome` values are `success`, `invalid`, `already_done` (shared [`MissionListResponse`](../api.yaml) with `new_missions`). Clearance success may list one or many missions; data submit **success-lists** simulates `success` with a non-empty `new_missions` array.

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

### Agent dashboard

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [agent-dashboard.html](agent-dashboard.html) | done | Alice; sticky header clearance; title-row toggle | UC-013, UC-019, UC-026 |
| [agent-dashboard-hidden.html](agent-dashboard-hidden.html) | done | Same list; **Show completed missions** off | UC-013 |
| [agent-dashboard-clearance-success.html](agent-dashboard-clearance-success.html) | done | Diana; **EXAMPLE-CLEARANCE** granted modal | UC-020, UC-027 |
| [agent-dashboard-clearance-invalid.html](agent-dashboard-clearance-invalid.html) | done | Invalid clearance modal | UC-020 |
| [agent-dashboard-clearance-already-done.html](agent-dashboard-clearance-already-done.html) | done | **EXAMPLE-CLEARANCE** re-submitted (Alice) | UC-020 |

### Mission detail

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [mission-detail-active.html](mission-detail-active.html) | done | **Alice / es-beta** active: Brief, Data textarea | UC-009, UC-016, UC-017 |
| [mission-detail-completed.html](mission-detail-completed.html) | done | **Alice / es-alpha** completed; agency archives + Debrief | UC-010, UC-018, UC-021 |
| [mission-detail-submit-success.html](mission-detail-submit-success.html) | done | **es-beta** data accepted (no new missions) | UC-021 |
| [mission-detail-submit-success-lists.html](mission-detail-submit-success-lists.html) | done | **es-alpha** success + **es-gamma** listed | UC-021, UC-032 |
| [mission-detail-submit-invalid.html](mission-detail-submit-invalid.html) | done | Invalid data (**es-beta**) | UC-022 |

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

1. `css/radspion.css` — sticky header + clearance field ✓  
2. Auth landing + errors ✓  
3. Agent dashboard + clearance modals ✓  
4. Mission detail (active, completed, data modals) ✓  
5. Implement Jinja templates + `src/` against these mockups  
6. Operator pages (TODO)

---

## Per-page checklist

### Site header (all agent pages)

- Sticky header with clearance input + **Request Access**
- Agent identity + sign out

### Agent dashboard

- Story-arc sections with collapsible groups; toggle for completed missions.
- **No** clearance field in dashboard body — use header modals (`agent-dashboard-clearance-*.html`) for clearance outcomes.

### Mission detail (active)

- Mission Brief; **Data** textarea + **Submit data** → open `mission-detail-submit-*.html` for each outcome.

### Mission detail (completed)

- Agency archives (submitted data) → collapsible Mission Debrief (open) → collapsible Mission Brief (closed).
