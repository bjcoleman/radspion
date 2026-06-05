# Testing Storyline (dev/test seed)

Generic mission chain for **local testing** and use-case acceptance. **Not used in production.**

**Orientation** includes `basic-training` (`open`). **Testing Storyline** exercises shared clearance codes (`EXAMPLE-CLEARANCE`, `HIDDEN-CLEARANCE`), list prerequisites, a hidden side mission, and a two-prereq finale. Agent UI vocabulary: [06-agent-experience.md](06-agent-experience.md).

Seed: [`src/radspion/sql/seed_testing_storyline.sql`](../../src/radspion/sql/seed_testing_storyline.sql).  
Details: [04-example-data-walkthrough.md](04-example-data-walkthrough.md). Always refer to missions by **slug**.

## Cast

Four sample agents; each illustrates a distinct progress state:

| Agent | Role in scenarios |
|-------|-------------------|
| Diana | Orientation only — no storyline clearance granted |
| Alice | `es-alpha` done; `es-gamma` listed; `es-beta` still active; `es-delta` hidden |
| Charlie | `es-beta` done; `es-alpha` still active; `es-gamma` not listed |
| Bob | All storyline missions `completed` |

## Acceptance scenarios

| Agent | Expected behavior |
|-------|-------------------|
| Diana | Sees `basic-training` only; no Testing Storyline missions until clearance |
| Alice | `es-gamma` active after `es-alpha` complete; `es-delta` not listed until `es-beta` and `es-gamma` are both complete |
| Charlie | `es-beta` complete but `es-gamma` not listed (`es-alpha` not complete) |
| Bob | All `es-*` missions `completed`; can view all captured data |
| Any | Clearance **EXAMPLE-CLEARANCE** → `es-alpha` and `es-beta` appear; **HIDDEN-CLEARANCE** → `es-hidden` only |

## Per-mission config

| slug | access_rule | Listed when |
|------|-------------|-------------|
| es-alpha | clearance_code | Clearance **EXAMPLE-CLEARANCE** |
| es-beta | clearance_code | Clearance **EXAMPLE-CLEARANCE** |
| es-hidden | clearance_code | Clearance **HIDDEN-CLEARANCE** (hint on ES: Beta brief) |
| es-gamma | requires_complete | **es-alpha** completed |
| es-delta | requires_complete | **es-beta** and **es-gamma** completed |

A mission never combines **`clearance_code`** with **`mission_list_requires`**.

**es-hidden** and **es-delta** do not list further missions after completion.
