# Mission pack authoring

How to author storylines in **radspion-missions**. Platform behavior: [design/06-agent-experience.md](../design/06-agent-experience.md).

## Clearance and data

| | Clearance | Data |
|---|-----------|------|
| **YAML / DB** | `access: { clearance_code: "..." }` | `completion_data: ...` |
| **Format** | Letters, digits, hyphen only; human-readable encouraged (validated at pack load) | Any text — JSON, hex, prose, **newlines** |
| **Effect** | Lists mission(s) on dashboard | Completes the active mission |

Do not shape mission **data** like clearance codes (especially in **Orientation**, which teaches the distinction).

## `storyline.yaml`

Each pack has `group` and `missions`. Each mission: `slug`, `title`, `access`, `completion_data`.

### Access (exactly one)

```yaml
access: open
```

```yaml
access:
  clearance_code: "RADSPION-QR-TRAINING"
```

```yaml
access:
  requires_complete:
    - other-mission-slug
```

- **`open`** — rare; walk-up content with minimal prerequisites.
- **`clearance_code`** — clearance code (YAML key matches DB column `clearance_code`). The same string may appear on **multiple** missions so one grant lists several.
- **`requires_complete`** — lists after listed prerequisites are **completed**.

A mission never combines `clearance_code` with `requires_complete` on the same row.

### `completion_data` (completion data)

Set in YAML only — not parsed from markdown. Must match what the brief tells agents to submit **exactly** (case, spaces, newlines).

Single line:

```yaml
completion_data: "0x690x6E"
```

Multi-line (literal block):

```yaml
completion_data: |
  [
    {
      "_id": "6a22140a1da67bab6d17716f",
      "isActive": true,
      "name": "Ayala King"
    }
  ]
```

The pack loader strips leading/trailing whitespace on the whole value; internal newlines are preserved.

## Brief and debrief (`{slug}/brief.md`, `{slug}/debrief.md`)

- Point agents at **clearance codes** when a string lists new missions (including QR codes).
- Point agents at **data** when they should complete the current mission.
- Show copy-paste **data** in fenced code blocks (see [mission-markdown.md](mission-markdown.md)).
- The **first mission** in a pack should have a clear title and brief that onboard the arc: premise, prerequisites, effort, links. Course grading and due dates belong in the LMS, not in Radspion prose.

## QR codes and field assets

```bash
make_radspion_qr ./qr.png "https://www.radspion.com/clearance/RADSPION-QR-TRAINING"
make_radspion_clearance_logo ./logo-code.png "RADSPION-CLEARANCE-TRAINING"
```

QR URLs encode a clearance code.

## Campus and field sources

Briefs may send agents to real people (e.g. campus contacts) for **data**, clearance codes, or both. Distribute sensitive clearance outside public briefs when appropriate (LMS, in-person).

## Validate and seed

From **radspion** (with `RADSPION_MISSIONS_ROOT` in `.env`):

```bash
seed_storyline PACK --check
create_empty_db --force
seed_storyline PACK
```

Seeds are insert-only and not idempotent. See [dev.md](../dev.md).

## Preview brief layout

From **radspion** (with `RADSPION_MISSIONS_ROOT` in `.env`): `preview_mission PACK SLUG` — see [dev.md](../dev.md). Reads `{slug}/brief.md` and `debrief.md` from **radspion-missions** without seeding the database.

## Reference pack

**Orientation** teaches clearance and data step by step.
