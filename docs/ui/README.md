# Radspion UI mockups (V1)

Static HTML/CSS prototypes for **Flask + Jinja SSR**. Each file is a fixed snapshot—no backend. **JavaScript in this folder is mock-only** (hard-coded modal outcomes, query-string previews); production will use server-rendered pages plus `fetch` to the JSON API ([06-agent-experience.md](../design/06-agent-experience.md), [api.yaml](../api.yaml)). Use the [example class seed](../../src/radspion/sql/seed_example_class.sql) personas and states from [design docs](../design/).

**Design reference:** [06-agent-experience.md](../design/06-agent-experience.md) (includes hybrid JSON endpoints) · [use-cases.md](../design/use-cases.md) · [05-example-class.md](../design/05-example-class.md)

**Assets:** shared styles in `css/`; logos in [`logos/`](../../logos/); one sample **Mission Brief** and **Debrief** in [`sample_files/`](sample_files/) (`brief.md`, `debrief.md`) reused on mission detail pages — not a file per mission.

**Sample data alignment:** Six missions — **Orientation** (`basic-training`, `global-hidden` code-only), **DevOps** (`read-the-manual`, `learn-the-system` open starters; **`remote-access`** lists after LMS; **`identify-the-traitor`** finale). Adding a mission to the roster uses either a redeemable **`unlock_code`** or automatic **`requires_complete`** listing — never both (see seed + use cases).

**Mock vs production:** Modals animate progress in the browser, but outcomes are **hard-coded in JS** (no `fetch`). Production will call `POST /agent/api/unlock` and `POST /agent/api/missions/<slug>/submit` and render the same UI from JSON ([06-agent-experience.md](../design/06-agent-experience.md)). API `outcome` values: unlock — `success`, `invalid`, `not_cleared`; submit — `success`, `invalid`, `not_yet`. The mock-only `success-unlocks` preview simulates `success` with a non-empty `new_missions` array.

---

## How to use this folder

1. Open HTML files in a browser (double-click or a local static server).
2. Use **preview buttons** on the page or **`?unlock=` / `?outcome=`** query params, then click **Unlock** or **Submit**.
3. Iterate on layout and copy before implementing Jinja templates + JSON endpoints.

---

## File index

### Auth & agent

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [index.html](index.html) | done | Signed-out landing; “Sign in with Google”; `@moravian.edu` note | UC-006 |
| [agent-dashboard-alice.html](agent-dashboard-alice.html) | done | 220.2 DevOps + **Orientation**; **remote-access** active; learn-the-system + read-the-manual completed; global-hidden unlocked only via code demo | UC-013, UC-019, UC-020, UC-026, UC-027 |

### Mission detail

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [mission-detail-active.html](mission-detail-active.html) | done | **Alice / remote-access** active: Brief, Recovered Data, transmission modal | UC-009, UC-016, UC-017, UC-021–UC-023, UC-029 |
| [mission-detail-completed.html](mission-detail-completed.html) | done | **Alice / learn-the-system** completed (static shell shares layout for both completed DevOps starters in prototype) | UC-010, UC-018, UC-021 |

### Unlock (dashboard)

| Outcome | Preview | Open in browser (`?unlock=` then **Unlock**) |
|---------|---------|-----------------------------------------------|
| Success — **global-hidden** added (title, slug, clearance in modal; card on roster after OK) | Success button | [agent-dashboard-alice.html?unlock=success](agent-dashboard-alice.html?unlock=success) |
| Bad code | Bad code button | [agent-dashboard-alice.html?unlock=invalid](agent-dashboard-alice.html?unlock=invalid) |
| Wrong clearance | Wrong clearance button | [agent-dashboard-alice.html?unlock=not_cleared](agent-dashboard-alice.html?unlock=not_cleared) |

### Transmission / complete (active mission)

| Outcome | Preview | Open in browser (`?outcome=` then **Submit**) |
|---------|---------|-----------------------------------------------|
| Success, **no** new missions → OK → completed/debrief page | Success (no new missions) | [mission-detail-active.html?outcome=success](mission-detail-active.html?outcome=success) |
| Success, **one+** new missions listed (mock: **identify-the-traitor** after Alice completes remote-access) → OK → completed page | Success (+ new missions) | [mission-detail-active.html?outcome=success-unlocks](mission-detail-active.html?outcome=success-unlocks) |
| Wrong code | Wrong code | [mission-detail-active.html?outcome=invalid](mission-detail-active.html?outcome=invalid) |
| Stealth / not yet | Stealth block | [mission-detail-active.html?outcome=not_yet](mission-detail-active.html?outcome=not_yet) |

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
| [js/outcome-missions.js](js/outcome-missions.js) | Renders title / slug / clearance from mock JSON-shaped arrays |
| [js/unlock.js](js/unlock.js) | Hard-coded unlock outcomes; success adds global-hidden to roster |
| [js/transmission.js](js/transmission.js) | Hard-coded submit outcomes; `success` vs `success-unlocks` fork |
| [js/copy.js](js/copy.js) | Copy-to-clipboard on code blocks and recovered data |

---

## Suggested build order

1. `css/radspion.css` ✓  
2. `index.html` ✓  
3. `agent-dashboard-alice.html` ✓  
4. `mission-detail-active.html` → `mission-detail-completed.html` ✓  
5. Operator pages (TODO)

---

## Per-page checklist

### Agent dashboard
- Clearance sections; active before completed within a group.
- **Add Mission** → modal → preview or `?unlock=`.
- Unlock **success**: modal lists **Training: Confidential Briefing** / `global-hidden` / **Orientation**; **OK** inserts active card on orientation roster.

### Mission detail (active)
- Full Brief; Recovered Data submit → modal.
- **Success (no new missions)**: congratulate only → **OK** → `mission-detail-completed.html`.
- **Success (+ new missions)**: congratulate + mission list (mock: **identify-the-traitor** on DevOps roster after sync when completing **remote-access** in Alice’s seed path) → **OK** → completed page.

### Mission detail (completed)
- Recovered Data → Debrief → collapsed Brief.
