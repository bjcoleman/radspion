# SQL schema and seeds

| File | Purpose |
|------|---------|
| `schema.sql` | Tables and indexes |
| `seed_testing_storyline.sql` | Dev/test fixture: Orientation placeholder + Testing Storyline + sample agents |

## Production storyline packs

Mission packs are authored in **radspion-missions** (`storyline.yaml` + per-mission `brief.md` / `debrief.md`). Generate SQL in that repo, then load into a database that already has `schema.sql` applied:

```bash
# In radspion-missions (see that repo README)
.venv/bin/python scripts/generate_storyline_sql.py orientation

# In radspion (.env must set RADSPION_MISSIONS_ROOT)
./scripts/seed_storyline.sh orientation
```

`seed_storyline.sh` reads `{pack}/{pack}.sql` from the missions repo path in `.env`. Before loading, it runs `scripts/validate_pack_sql.py` to ensure listing and completion data in the pack are disjoint and do not overlap strings already in the database. Seeds are insert-only and not idempotent.

## Testing seed

`seed_testing_storyline.sql` includes **inlined** `brief_markdown` and `debrief_markdown` for the test fixture. Do not edit those bodies by hand.

Recreate local test database after schema or seed changes:

```bash
./scripts/create_test_db.sh
```

Pytest builds its own temporary databases from this seed; you do not need `create_test_db.sh` before running tests.
