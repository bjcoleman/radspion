# Field Activity: example data for mockups

Reference **fixture** for the public **Field Activity** page (`/activity`) and related UI mockups. Not loaded into the database — this document is the canonical story the mockup should tell.

Agents are identified by **codenames** (4–20 characters; agents choose on the Personnel File). Mission titles never appear on Field Activity; only storyline names and counts.

See [02-entities.md](02-entities.md) for vocabulary. Operator views (later) show codename, email, and Google `display_name`.

---

## The story this data tells

Radspion has been live with a small field cohort for a few weeks.

**Orientation** is nearly finished as a cohort — most agents cleared the arc, but a few are still working through training missions. New sign-ups land on the open mission and trickle through.

**Operation Glass Harbour** is the busiest storyline: many agents entered via the main clearance code, parallel branches are opening up, and one side clearance (`GLASS-ANCHOR`) has never been found. Nobody has finished the finale.

**The Meridian Protocol** is the deep endgame. Top agents are mid-arc; a hidden clearance (`MERIDIAN-VAULT`) remains undiscovered; the last two missions have no completions anywhere.

**Cold Relay** is newer and sparser. A handful of agents found the entry code; the secondary code (`COLD-SHIFT`) is still at zero grants. **Distant-Cipher** just unlocked two missions there — the freshest clearance event on the board.

**Veil of Cinders** is a side arc only two agents have entered. Progress is shallow; the back half of the arc is untouched globally.

**Quiet-Raven** completed their first field mission in Glass Harbour — visible on Recent Missions Completed but far from the leaderboard.

**Cobalt-Operative** signed in and has the Orientation open mission active, but has not completed anything yet. They do not appear on Field Activity feeds.

No agent has completed every mission in the system.

---

## Storylines

Five story arcs. Display order on Field Activity: **never-assigned count ascending**, ties by name; **Orientation always last**.

| Storyline | Missions | Never completed | Never assigned |
|-----------|----------|-----------------|----------------|
| Veil of Cinders | 5 | 3 | 0 |
| Operation Glass Harbour | 8 | 1 | 1 |
| The Meridian Protocol | 10 | 2 | 1 |
| Cold Relay | 7 | 3 | 1 |
| Orientation | 6 | 0 | 0 |

Fixture totals (not shown on the page): **36** missions · **3** never assigned · **9** never completed.

### Per-storyline notes

**Veil of Cinders** (5 missions)  
Entry clearance `VEIL-CINDERS` has been granted twice (**Silent-Fox**, **Sharp-Meridian**). Missions 3–5 have zero completions globally.

**Operation Glass Harbour** (8 missions)  
Main code `GLASS-HARBOUR` is widely known. Branch code `GLASS-ANCHOR` has **never** been submitted — one mission awaits first clearance. Finale mission 8 has zero completions; **Silent-Fox** is closest (7 completed, 1 active).

**The Meridian Protocol** (10 missions)  
Entry code `MERIDIAN-PROTOCOL` is common among active agents. Hidden code `MERIDIAN-VAULT` has **never** been submitted. Finale missions 9–10 have zero completions globally.

**Cold Relay** (7 missions)  
Entry code `COLD-RELAY` reached a few agents. Secondary code `COLD-SHIFT` has **never** been submitted. Missions 5–7 have zero completions globally.

**Orientation** (6 missions)  
One `open` mission plus clearance-gated training. Both clearance codes have been found by someone. Every mission has at least one completion — the tutorial arc is effectively “solved” as a set, though individual agents are still catching up.

### Mission graph (abbreviated)

```text
Orientation
  O1 (open) ──► O3 ──► O5 ──► O6 (finale)
  O2 (clearance) ──► O4 (clearance) ──┘

Operation Glass Harbour
  GH1 (clearance) ──► GH3 ──► GH5 ──┐
                 └──► GH4 ──► GH6 ──┼──► GH7 ──► GH8 (finale, unsolved)
  GH2 (clearance, NEVER GRANTED)     │

The Meridian Protocol
  MP1 (clearance) ──► MP3 ──► MP5 ──► MP7 ──┐
                 └──► MP4 ──► MP6 ──► MP8 ──┼──► MP9 ──► MP10 (unsolved)
  MP2 (clearance, NEVER GRANTED)

Cold Relay
  CR1 (clearance) ──► CR3 ──► CR5 ──┐
                 └──► CR4 ──► CR6 ──┼──► CR7 (unsolved)
  CR2 (clearance, NEVER GRANTED)

Veil of Cinders
  VC1 (clearance) ──► VC2 ──► VC4 ──► VC5 (unsolved)
                 └──► VC3 (unsolved)
```

---

## Agents (15)

Codenames only on Field Activity. Progress is **completed** / **active** counts per storyline. Omit storylines where the agent has no listed missions.

| # | Codename | Completed (all arcs) | On Field Activity |
|---|----------|----------------------|-------------------|
| 1 | Silent-Fox | 26 | Top Agents · Recent Missions Completed |
| 2 | Crimson-Vector | 20 | Top Agents · Recent Clearances Granted |
| 3 | Midnight-Broker | 16 | Top Agents |
| 4 | Iron-Sentinel | 15 | Top Agents · Recent Missions Completed |
| 5 | Velvet-Courier | 12 | Top Agents |
| 6 | Amber-Lantern | 12 | Top Agents · Recent Clearances Granted |
| 7 | Shadow-Archive | 9 | Top Agents |
| 8 | Pale-Handler | 7 | Top Agents |
| 9 | Burning-Asset | 7 | Top Agents |
| 10 | Hollow-Signal | 6 | Top Agents |
| 11 | Quiet-Raven | 1 | Recent Missions Completed only |
| 12 | Distant-Cipher | 2 | Recent Clearances Granted only |
| 13 | Cobalt-Operative | 0 | *(not on page)* |
| 14 | Ghostly-Ledger | 3 | — |
| 15 | Sharp-Meridian | 5 | — |

### Per-agent progress

**Silent-Fox** — 26 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 6 | 0 |
| Operation Glass Harbour | 7 | 1 |
| The Meridian Protocol | 8 | 2 |
| Cold Relay | 3 | 1 |
| Veil of Cinders | 2 | 1 |

**Crimson-Vector** — 20 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 6 | 0 |
| Operation Glass Harbour | 6 | 1 |
| The Meridian Protocol | 6 | 2 |
| Cold Relay | 2 | 2 |

**Midnight-Broker** — 16 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 6 | 0 |
| Operation Glass Harbour | 5 | 2 |
| The Meridian Protocol | 5 | 1 |

**Iron-Sentinel** — 15 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 6 | 0 |
| Operation Glass Harbour | 5 | 0 |
| The Meridian Protocol | 4 | 2 |

**Velvet-Courier** — 12 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 5 | 1 |
| Operation Glass Harbour | 4 | 1 |
| The Meridian Protocol | 3 | 1 |

**Amber-Lantern** — 12 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 6 | 0 |
| Operation Glass Harbour | 4 | 1 |
| The Meridian Protocol | 2 | 2 |

**Shadow-Archive** — 9 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 6 | 0 |
| Operation Glass Harbour | 3 | 2 |

**Pale-Handler** — 7 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 5 | 1 |
| The Meridian Protocol | 2 | 1 |

**Burning-Asset** — 7 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 6 | 0 |
| Cold Relay | 1 | 0 |

**Hollow-Signal** — 6 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 4 | 2 |
| Operation Glass Harbour | 2 | 1 |

**Quiet-Raven** — 1 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 0 | 1 |
| Operation Glass Harbour | 1 | 0 |

**Distant-Cipher** — 2 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 2 | 1 |
| Cold Relay | 0 | 2 |

**Cobalt-Operative** — 0 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 0 | 1 |

**Ghostly-Ledger** — 3 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 3 | 1 |

**Sharp-Meridian** — 5 completed  
| Storyline | Completed | Active |
|-----------|-----------|--------|
| Orientation | 4 | 1 |
| Veil of Cinders | 1 | 1 |

---

## Derived Field Activity displays

Values below are what the mockup should render. Copy uses codename and storyline name only.

### Page intro

```text
Field Activity

Agency-wide mission progress. Codenames only — mission titles are classified.
```

No summary or inventory line under the lede (totals live in the fixture table above only).

### Layout

Two columns on desktop; single column on narrow viewports.

| Column | Sections (top to bottom) |
|--------|--------------------------|
| Left | Top Agents · Storylines |
| Right | Recent Clearances Granted · Recent Missions Completed |

Section headings use title case in markup (`Top Agents`, `Recent Clearances Granted`, …) and render uppercase via CSS. Each heading sits **above** its list, not inside the panel.

List content (leaderboard, storylines, both feeds) sits in grey bordered panels. The right column adds extra vertical space before **Recent Missions Completed** so the two feed blocks read as separate sections.

Public header: brand + Sign in only (no nav). Agents reach Field Activity from the Mission Dashboard link (when signed in).

### Storylines

Section heading: **Storylines**. Display order: **never-assigned count ascending**, ties by name; **Orientation always last**. Omit a clause when its count is zero. Within each row, list **never completed** before **never assigned**.

```text
Veil of Cinders          5 missions · 3 never completed
Operation Glass Harbour  8 missions · 1 never completed · 1 never assigned
The Meridian Protocol   10 missions · 2 never completed · 1 never assigned
Cold Relay               7 missions · 3 never completed · 1 never assigned
Orientation              6 missions
```

### Top Agents (10)

Section heading: **Top Agents**. At least one completion required. Ordered by completed count descending; ties broken by most recent `completed_at`.

```text
 1. Silent-Fox       26 missions completed
 2. Crimson-Vector   20 missions completed
 3. Midnight-Broker  16 missions completed
 4. Iron-Sentinel    15 missions completed
 5. Velvet-Courier   12 missions completed
 6. Amber-Lantern    12 missions completed
 7. Shadow-Archive    9 missions completed
 8. Pale-Handler      7 missions completed
 9. Burning-Asset     7 missions completed
10. Hollow-Signal     6 missions completed
```

Fewer than ten agents qualify today — the mockup may show only these ten rows once the pool grows.

### Recent Missions Completed

Section heading: **Recent Missions Completed**. Most recent first. Count-based (`LIMIT 10`), not a time window. Each row includes a short relative timestamp (`18m`, `2h`, `1d`, …).

| Agent | Storyline | Scenario role |
|-------|-----------|---------------|
| Quiet-Raven | Operation Glass Harbour | Recent only — not in top 10 |
| Iron-Sentinel | The Meridian Protocol | Recent + top 10 |
| Silent-Fox | The Meridian Protocol | Recent + top 10 |
| Crimson-Vector | Operation Glass Harbour | — |
| Amber-Lantern | Orientation | — |
| Midnight-Broker | The Meridian Protocol | — |
| Velvet-Courier | Operation Glass Harbour | — |
| Sharp-Meridian | Veil of Cinders | — |
| Ghostly-Ledger | Orientation | — |
| Hollow-Signal | Orientation | — |

Display line (example):  
`Quiet-Raven in Operation Glass Harbour` — agent white, storyline gold, other text (`in`, timestamps) grey.

### Recent Clearances Granted

Section heading: **Recent Clearances Granted**. Grouped in the database by `(user_id, storyline, listed_at)`; `LIMIT 10` on groups. Only `listed_via = clearance` listings. Each row includes a short relative timestamp.

| Agent | Storyline | Missions unlocked | Scenario role |
|-------|-----------|-------------------|---------------|
| Distant-Cipher | Cold Relay | 2 | Recent only — not in top 10 |
| Amber-Lantern | The Meridian Protocol | 1 | Recent + top 10 |
| Crimson-Vector | Operation Glass Harbour | 3 | Recent + top 10 (one code, three missions) |
| Iron-Sentinel | The Meridian Protocol | 2 | — |
| Pale-Handler | The Meridian Protocol | 1 | — |
| Hollow-Signal | Operation Glass Harbour | 1 | — |
| Sharp-Meridian | Veil of Cinders | 1 | — |
| Velvet-Courier | Operation Glass Harbour | 1 | — |
| Ghostly-Ledger | Orientation | 1 | — |
| Shadow-Archive | Operation Glass Harbour | 1 | — |

Display lines (examples):  
`Distant-Cipher in Cold Relay`  
`Crimson-Vector in Operation Glass Harbour` — one row per grouped clearance event, even when multiple missions listed

---

## Scenario checklist

| Scenario | Agent | Where it shows |
|----------|-------|----------------|
| Never completed anything | Cobalt-Operative | Absent from Top Agents and both feed sections |
| One recent solve, not top 10 | Quiet-Raven | Recent Missions Completed (newest row) |
| Recent clearance, not top 10 | Distant-Cipher | Recent Clearances Granted (newest row) |
| Recent solve + top 10 | Iron-Sentinel, Silent-Fox | Top Agents and Recent Missions Completed |
| Recent clearance + top 10 | Amber-Lantern, Crimson-Vector | Top Agents and Recent Clearances Granted |
| Mission never completed globally | GH8, MP9, MP10, CR5–CR7, VC3–VC5 | Storylines never-completed counts |
| Mission never assigned | GH2, MP2, CR2 | Storylines never-assigned counts |
| No agent finished everything | *(all)* | Max completion is Silent-Fox at 26/36 |

---

## Consistency checks

Use these when extending the fixture or building the mockup.

1. **Completed counts** — Sum per-agent storyline `completed` values equal the leaderboard column.
2. **Active implies listed** — `active > 0` means the agent has a status row; `completed + active` never exceeds missions in that storyline.
3. **Never assigned** — Count clearance-gated missions with zero `agent_mission_status` rows across all agents (three in this fixture).
4. **Never completed** — Count missions with zero `completed` rows across all agents (nine in this fixture).
5. **Recent feeds** — Agents marked “recent only” must not appear in the top-10 table; agents marked “recent + top 10” must appear in both feed sections.
6. **Clearance grouping** — Crimson-Vector’s “3 missions” event is one `listed_at` from a single clearance request matching three missions; the feed shows one row (`Crimson-Vector in Operation Glass Harbour`), not a mission count.
7. **Feed copy** — Use `Agent in Storyline` (not parentheses). Mission titles never appear on Field Activity.
