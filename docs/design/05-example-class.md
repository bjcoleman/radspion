# Example seed (220.2 DevOps)

> **Pending missions-pack rework.** Acceptance scenarios below reflect the **target** model. The seed in [`radspion-missions/example-class/seed_example_class.sql`](../../../radspion-missions/example-class/seed_example_class.sql) is outdated (rosters, `mission_complete_requires`).

**Orientation** missions use the Orientation story arc. **220.2 DevOps** missions use the DevOps arc. Always refer to missions by **slug** (not numeric ids).

Details: [04-example-data-walkthrough.md](04-example-data-walkthrough.md).

## Cast (target)

Four sample agents for acceptance tests once the seed is updated:

| Agent | Role in scenarios |
|-------|-------------------|
| Alice | Mid-progress DevOps; orientation complete |
| Bob | All missions complete |
| Charlie | Partial DevOps progress |
| Diana | Orientation only (has not entered DevOps arc) |

Diana does not see DevOps missions because she has not redeemed the arc entry code (or satisfied list prereqs) — not because of roster membership.

## Intended acceptance scenarios

| Agent | Expected behavior (target model) |
|-------|----------------------------------|
| Diana | Sees `basic-training` only; no DevOps missions until arc entry |
| Alice | DevOps progress per seed; `global-hidden` after unlock code |
| Bob | All missions `completed` |
| Charlie | Partial list; can complete any listed mission with correct code (no stealth submit gates) |

## Per-mission config (target)

| slug | arc | access_rule | List after completing… |
|------|-----|-------------|------------------------|
| basic-training | Orientation | open | — |
| global-hidden | Orientation | unlock_code | redeem code |
| read-the-manual | 220.2 DevOps | unlock_code * | redeem arc entry code * |
| learn-the-system | 220.2 DevOps | requires_complete * | TBD in pack rework |
| remote-access | 220.2 DevOps | requires_complete | TBD (`mission_list_requires`) |
| identify-the-traitor | 220.2 DevOps | requires_complete | read-the-manual **and** remote-access |

\* Exact access rules and list graph pending **radspion-missions** rework.

A mission never combines **`unlock_code`** with **`mission_list_requires`**.
