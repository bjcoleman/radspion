# Radspion UI mockups (V1)

Static HTML/CSS prototypes for **Flask + Jinja SSR**. Each file is a fixed snapshot—no backend. Modal animations use **inline scripts** on dedicated outcome pages; production will use server-rendered pages plus `fetch` to the JSON API ([06-agent-experience.md](../design/06-agent-experience.md), [api.yaml](../api.yaml)). Personas and seed states: [05-example-storyline.md](../design/05-example-storyline.md) (Alice mid-progress on **Example Storyline**).

**Design reference:** [06-agent-experience.md](../design/06-agent-experience.md) (includes hybrid JSON endpoints) · [use-cases.md](../design/use-cases.md) · [05-example-storyline.md](../design/05-example-storyline.md) · [COLOR_USAGE.md](COLOR_USAGE.md)

**Assets:** styles in [`css/radspion.css`](css/radspion.css) are kept in sync with production [`src/radspion/static/css/radspion.css`](../../src/radspion/static/css/radspion.css) (mockup rules + app-only rules for flash, content pages, disabled controls). Logos in [`logos/`](../../logos/). Mission brief and debrief copy is **inlined in HTML** on mission detail mockups (production loads markdown from the database).

**Sample data alignment:** Story arcs **Orientation** and **Example Storyline** (`es-*` missions); **`unlock_code`** or **`requires_complete`** listing — never both on one mission.

**Mock vs production:** Modal outcome pages hard-code copy and animation; no `fetch`. Production will call `POST /api/access`, `POST /api/unlock`, and `POST /api/missions/<slug>/submit` per [`api.yaml`](../api.yaml). API `outcome` values: access — `success`, `invalid`; unlock and submit — `success`, `invalid`, `already_done` (shared [`MissionListResponse`](../api.yaml) with `new_missions`). Unlock success may list one or many missions; submit **success-unlocks** simulates `success` with a non-empty `new_missions` array.

---

## How to use this folder

1. Open HTML files in a browser (double-click or a local static server).
2. Open the dedicated **modal outcome** HTML files to preview transmission animations and dialogs.
3. Iterate on layout and copy before implementing Jinja templates + JSON endpoints.

---

## File index

### Auth & landing

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [index.html](index.html) | done | Signed-out landing; access code + Secure Login | UC-006 |
| [bad_access_code_submitted.html](bad_access_code_submitted.html) | done | Landing + failed access-code modal | UC-006 |
| [good_access_code_submitted.html](good_access_code_submitted.html) | done | Landing + success modal → Secure Login | UC-006 |
| [secure_login_modal.html](secure_login_modal.html) | done | Landing + Google sign-in modal | UC-006 |

### Agent dashboard

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [agent-dashboard.html](agent-dashboard.html) | done | Alice; Example Storyline expanded (`es-alpha` done, `es-beta`/`es-gamma` active) | UC-013, UC-019, UC-026 |
| [agent-dashboard-hidden.html](agent-dashboard-hidden.html) | done | Same list; **Show completed missions** off | UC-013 |
| [agent-dashboard-unlock-success.html](agent-dashboard-unlock-success.html) | done | Unlock success modal | UC-020, UC-027 |
| [agent-dashboard-unlock-bad-code.html](agent-dashboard-unlock-bad-code.html) | done | Unlock invalid modal | UC-020 |

### Mission detail

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [mission-detail-active.html](mission-detail-active.html) | done | **Alice / es-beta** active: Brief, Recovered Data | UC-009, UC-016, UC-017 |
| [mission-detail-completed.html](mission-detail-completed.html) | done | **Alice / es-alpha** completed; collapsible Mission Debrief + Mission Brief | UC-010, UC-018, UC-021 |
| [mission-detail-submit-success.html](mission-detail-submit-success.html) | done | Submit success (no new missions) | UC-021 |
| [mission-detail-submit-success-unlocks.html](mission-detail-submit-success-unlocks.html) | done | Submit **es-alpha** success + **es-gamma** listed | UC-021, UC-032 |
| [mission-detail-submit-invalid.html](mission-detail-submit-invalid.html) | done | Submit invalid code | UC-022 |

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
3. `agent-dashboard.html` + unlock/hidden variants ✓  
4. `mission-detail-active.html` → completed + submit outcome pages ✓  
5. Operator pages (TODO)

---

## Per-page checklist

### Agent dashboard
- Story-arc sections with collapsible groups; toggle for completed missions.
- Unlock code field → open `agent-dashboard-unlock-*.html` for each outcome.

### Mission detail (active)
- Mission Brief; Recovered Data submit → open `mission-detail-submit-*.html` for each outcome.

### Mission detail (completed)
- Recovered Data → collapsible Mission Debrief (open) → collapsible Mission Brief (closed).
