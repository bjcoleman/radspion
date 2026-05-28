# Radspion UI mockups (V1)

Static HTML/CSS prototypes for **Flask + Jinja SSR**. Each file is a fixed snapshot—no backend. Modal animations use **inline scripts** on dedicated outcome pages; production will use server-rendered pages plus `fetch` to the JSON API ([06-agent-experience.md](../design/06-agent-experience.md), [api.yaml](../api.yaml)). Use the [example class seed](../../src/radspion/sql/seed_example_class.sql) personas and states from [design docs](../design/).

**Design reference:** [06-agent-experience.md](../design/06-agent-experience.md) (includes hybrid JSON endpoints) · [use-cases.md](../design/use-cases.md) · [05-example-class.md](../design/05-example-class.md) · [COLOR_USAGE.md](COLOR_USAGE.md)

**Assets:** shared styles in [`css/radspion.css`](css/radspion.css); logos in [`logos/`](../../logos/). Mission brief and debrief copy is **inlined in HTML** on mission detail mockups (production loads markdown from `content/missions/`).

**Sample data alignment:** Six missions — **Orientation** (`basic-training`, `global-hidden` code-only), **DevOps** (`read-the-manual`, `learn-the-system` open starters; **`remote-access`** lists after LMS; **`identify-the-traitor`** finale). Adding a mission to the roster uses either a redeemable **`unlock_code`** or automatic **`requires_complete`** listing — never both (see seed + use cases).

**Mock vs production:** Modal outcome pages hard-code copy and animation; no `fetch`. Production will call `POST /agent/api/unlock` and `POST /agent/api/missions/<slug>/submit` and render the same UI from JSON. API `outcome` values: unlock — `success`, `invalid`, `not_cleared`; submit — `success`, `invalid`, `not_yet`. Submit **success-unlocks** simulates `success` with a non-empty `new_missions` array.

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
| [agent-dashboard.html](agent-dashboard.html) | done | Alice; completed missions visible; DevOps expanded | UC-013, UC-019, UC-026 |
| [agent-dashboard-hidden.html](agent-dashboard-hidden.html) | done | Same roster; **Show completed missions** off | UC-013 |
| [agent-dashboard-unlock-success.html](agent-dashboard-unlock-success.html) | done | Unlock success modal | UC-020, UC-027 |
| [agent-dashboard-unlock-bad-code.html](agent-dashboard-unlock-bad-code.html) | done | Unlock invalid modal | UC-020 |
| [agent-dashboard-unlock-wrong-clearance.html](agent-dashboard-unlock-wrong-clearance.html) | done | Unlock not-cleared modal | UC-020 |

### Mission detail

| File | Status | Persona / state | Use cases |
|------|--------|-----------------|-----------|
| [mission-detail-active.html](mission-detail-active.html) | done | **Alice / remote-access** active: Brief, Recovered Data | UC-009, UC-016, UC-017 |
| [mission-detail-completed.html](mission-detail-completed.html) | done | **Alice / learn-the-system** completed; collapsible Mission Debrief + Mission Brief | UC-010, UC-018, UC-021 |
| [mission-detail-submit-success.html](mission-detail-submit-success.html) | done | Submit success (no new missions) | UC-021, UC-022 |
| [mission-detail-submit-success-unlocks.html](mission-detail-submit-success-unlocks.html) | done | Submit success + **identify-the-traitor** listed | UC-021, UC-022, UC-029 |
| [mission-detail-submit-invalid.html](mission-detail-submit-invalid.html) | done | Submit invalid code | UC-022 |
| [mission-detail-submit-not-yet.html](mission-detail-submit-not-yet.html) | done | Submit blocked (stealth / not yet) | UC-023 |

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
- Clearance sections with collapsible groups; toggle for completed missions.
- Unlock code field → open `agent-dashboard-unlock-*.html` for each outcome.

### Mission detail (active)
- Mission Brief; Recovered Data submit → open `mission-detail-submit-*.html` for each outcome.

### Mission detail (completed)
- Recovered Data → collapsible Mission Debrief (open) → collapsible Mission Brief (closed).
