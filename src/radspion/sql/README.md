# SQL schema and seeds

| File | Purpose |
|------|---------|
| `schema.sql` | Tables and indexes |
| `seed_orientation.sql` | Orientation group + `basic-training` (production) |
| `seed_testing_storyline.sql` | Testing Storyline + sample agents (dev/test only) |

## Mission markdown in seeds

`seed_orientation.sql` and `seed_testing_storyline.sql` include **inlined** `brief_markdown` and `debrief_markdown`. Do not edit those bodies by hand.

Author mission copy in the **radspion-missions** repo, then regenerate:

```bash
cd /path/to/radspion-missions
python3 scripts/generate_radspion_sql.py
```

Recreate local databases after schema or seed changes:

```bash
./scripts/create_empty_db.sh
# or
./scripts/create_test_db.sh
```
