# Example Storyline (test seed)

Generic mission chain for **local testing** and use-case acceptance. Not used in production.

**Orientation** includes `basic-training` (`open`). **Example Storyline** exercises shared unlock codes, list prerequisites, a hidden side mission, and a two-prereq finale.

Details: [04-example-data-walkthrough.md](04-example-data-walkthrough.md). Always refer to missions by **slug**.

## Cast

Four sample agents; each illustrates a distinct progress state:

| Agent | Role in scenarios |
|-------|-------------------|
| Diana | Orientation only — no storyline unlocks redeemed |
| Alice | `es-alpha` done; `es-gamma` listed; `es-beta` still active; `es-delta` hidden |
| Charlie | `es-beta` done; `es-alpha` still active; `es-gamma` not listed |
| Bob | All storyline missions `completed` |

## Acceptance scenarios

| Agent | Expected behavior |
|-------|-------------------|
| Diana | Sees `basic-training` only; no Example Storyline missions until unlock |
| Alice | `es-gamma` active after `es-alpha` complete; `es-delta` not listed until `es-beta` and `es-gamma` are both complete |
| Charlie | `es-beta` complete but `es-gamma` not listed (`es-alpha` not complete) |
| Bob | All `es-*` missions `completed`; can view all captured completion codes |
| Any | Redeem **EXAMPLE UNLOCK** → `es-alpha` and `es-beta` appear; **HIDDEN UNLOCK** → `es-hidden` only |

## Per-mission config

| slug | access_rule | Listed when |
|------|-------------|-------------|
| es-alpha | unlock_code | Redeem **EXAMPLE UNLOCK** |
| es-beta | unlock_code | Redeem **EXAMPLE UNLOCK** |
| es-hidden | unlock_code | Redeem **HIDDEN UNLOCK** (hint on ES: Beta brief) |
| es-gamma | requires_complete | **es-alpha** completed |
| es-delta | requires_complete | **es-beta** and **es-gamma** completed |

A mission never combines **`unlock_code`** with **`mission_list_requires`**.

**es-hidden** and **es-delta** do not unlock further missions after completion.
