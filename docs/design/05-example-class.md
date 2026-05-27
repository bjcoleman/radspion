# Example seed (220.2 DevOps)

**Orientation** missions use `group_id = 1`. **220.2 DevOps** missions use `group_id = 2`. Always refer to missions by **slug** (not numeric ids).

Details: [04-example-data-walkthrough.md](04-example-data-walkthrough.md). SQL: [`src/radspion/sql/seed_example_class.sql`](../../src/radspion/sql/seed_example_class.sql).

## Cast

| Agent | Orientation | 220.2 DevOps |
|-------|-------------|--------------|
| Alice, Bob, Charlie | member | member |
| Diana | member | — |

## Seed states

| Agent | 220.2 DevOps | Orientation |
|-------|--------------|-------------|
| Alice | read-the-manual, learn-the-system ✓; remote-access active | basic-training ✓ |
| Bob | all four class missions ✓ | basic-training, global-hidden ✓ |
| Charlie | learn-the-system ✓; read-the-manual + remote-access active | basic-training active |
| Diana | — | basic-training active |

## Per-mission config

| slug | group | access_rule | List after completing… | Complete only after… |
|------|-------|-------------|------------------------|-------------------------|
| basic-training | Orientation | open | — | — |
| global-hidden | Orientation | unlock_code | redeem code (only code-based mission in sample) | — |
| read-the-manual | 220.2 DevOps | open | — | — |
| learn-the-system | 220.2 DevOps | open | — | — |
| remote-access | 220.2 DevOps | requires_complete | learn-the-system | read-the-manual |
| identify-the-traitor | 220.2 DevOps | requires_complete | read-the-manual **and** remote-access | — (not listable until both are `completed`) |

A mission never combines **`unlock_code`** with **`mission_list_requires`** (code unlock vs. automatic listing are mutually exclusive).
