# SQL schema and seeds

| File | Purpose |
|------|---------|
| `schema.sql` | Tables and indexes |
| `seed_testing_storyline.sql` | Dev/test fixture: Orientation placeholder + Testing Storyline + sample agents |

## Production storyline packs

Mission packs are authored in **radspion-missions** (`storyline.yaml` + per-mission `brief.md` / `debrief.md`). Load into a database that already has `schema.sql` applied:

```bash
# In radspion (.env must set RADSPION_MISSIONS_ROOT)
seed_storyline orientation --check
create_empty_db --force
seed_storyline orientation
```

`seed_storyline` validates the pack, generates SQL in memory, and inserts rows. Seeds are insert-only and not idempotent. Use `--write-sql` to write `{pack}/{pack}.sql` beside the pack for debugging.

## Testing seed

`seed_testing_storyline.sql` includes **inlined** `brief_markdown` and `debrief_markdown` for the test fixture. Do not edit those bodies by hand.

Recreate local test database after schema or seed changes:

```bash
create_test_db --force
```

Pytest builds its own temporary databases from this seed; you do not need `create_test_db` before running tests.
