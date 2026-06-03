# Radspion UI mockups (V1)

Static HTML/CSS prototypes for **Flask + Jinja SSR**. Each file is a fixed snapshot—no backend. Modal animations use **inline scripts** on dedicated outcome pages; production uses server-rendered pages plus `fetch` to **`POST /api/submit`** ([06-agent-experience.md](../design/06-agent-experience.md), [api.yaml](../api.yaml)). Personas and seed states: [05-testing-storyline.md](../design/05-testing-storyline.md) (Alice mid-progress on **Testing Storyline**).

**Design reference:** [06-agent-experience.md](../design/06-agent-experience.md) · [use-cases.md](../design/use-cases.md) · [05-testing-storyline.md](../design/05-testing-storyline.md) · [COLOR_USAGE.md](COLOR_USAGE.md)

**Assets:** styles in [`css/radspion.css`](css/radspion.css) are kept in sync with production [`src/radspion/static/css/radspion.css`](../../src/radspion/static/css/radspion.css) (mockup rules + app-only rules for flash, content pages, disabled controls). Logos in [`logos/`](../../logos/). Mission brief and debrief copy is **inlined in HTML** on mission detail mockups (production loads markdown from the database).

**Sample data alignment:** Story arcs **Orientation** and **Testing Storyline** (`es-*` missions); **`unlock_code`** or **`requires_complete`** listing — never both on one mission.

**Mock vs production:** Modal outcome pages hard-code copy and animation; no `fetch`. Production calls **`POST /api/submit`** with `{ "data": "..." }` per [`api.yaml`](../api.yaml). Responses use `outcome`: `success`, `invalid`, or `already_done`, with `kind` (`unlock` | `complete`) and `new_missions` on success.

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
| [agent-dashboard.html](agent-dashboard.html) | done | Alice; Testing Storyline expanded (`es-alpha` done, `es-beta`/`es-gamma` active) | UC-013, UC-019, UC-026 |
| [agent-dashboard-hidden.html](agent-dashboard-hidden.html) | done | Same list; **Show completed missions** off | UC-013 |
| [agent-dashboard-submit-success.html](agent-dashboard-submit-success.html) | done | Submit listing data success modal (header submit) | UC-019, UC-027 |
| [agent-dashboard-submit-invalid.html](agent-dashboard-submit-invalid.html) | done | Submit invalid data modal | UC-020 |

### Mission detail

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [mission-detail-active.html](mission-detail-active.html) | done | **Alice / es-beta** active: Brief only (submit via header) | UC-009, UC-016 |
| [mission-detail-completed.html](mission-detail-completed.html) | done | **Alice / es-alpha** completed; collapsible Mission Debrief + Mission Brief | UC-010, UC-018, UC-021 |
| [mission-detail-submit-success.html](mission-detail-submit-success.html) | done | Completion success modal (no new missions) | UC-021 |
| [mission-detail-submit-success-lists.html](mission-detail-submit-success-lists.html) | done | Complete **es-alpha** + **es-gamma** listed | UC-021, UC-032 |
| [mission-detail-submit-invalid.html](mission-detail-submit-invalid.html) | done | Invalid data modal | UC-020, UC-022 |

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

1. `css/radspion.css` ✓  
2. Auth landing + modals ✓  
3. `agent-dashboard.html` + modal outcome variants ✓  
4. `mission-detail-active.html` → completed + submit outcome pages ✓  
5. Operator pages (TODO)

---

## Per-page checklist

### Agent dashboard
- Header **Submit data** field on all signed-in agent mockups.
- Story-arc sections with collapsible groups; toggle for completed missions.
- Modal outcomes → open `agent-dashboard-submit-*.html` for listing-data success / invalid.

### Mission detail (active)
- Mission Brief only; agents submit data from the header.

### Mission detail (completed)
- Recovered Data → collapsible Mission Debrief (open) → collapsible Mission Brief (closed).

### Modal outcome pages
- Hard-coded transmission modal after header submit; see `mission-detail-submit-*.html` for completion outcomes.
