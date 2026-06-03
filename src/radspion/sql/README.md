# SQL schema and seeds

| File | Purpose |
|------|---------|
| `schema.sql` | Tables and indexes |
| `seed_testing_storyline.sql` | Dev/test fixture: Orientation placeholder + Testing Storyline + sample agents |

## Production storyline packs

Mission packs are authored in **radspion-missions**. Each pack generates `{pack}/{pack}.sql` (e.g. `orientation/orientation.sql`). Load into an empty database with `./scripts/seed_storyline.sh` (requires `RADSPION_MISSIONS_ROOT` in `.env`).

## Testing seed

`seed_testing_storyline.sql` includes **inlined** `brief_markdown` and `debrief_markdown` for the test fixture. Do not edit those bodies by hand.

Recreate local test database after schema or seed changes:

```bash
./scripts/create_test_db.sh
```

Pytest builds its own temporary databases from this seed; you do not need `create_test_db.sh` before running tests.
