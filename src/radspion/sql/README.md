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

After the first seed, sync content changes (title, brief, debrief, clearance code, completion data) with:

```bash
update_storyline orientation --check
update_storyline orientation              # prompts if clearance/completion_data change
update_storyline orientation -y           # apply after review
update_storyline orientation --write-sql  # write {pack}/{pack}-update.sql only
```

`update_storyline` does not add or remove missions and cannot change group names, slugs, or access structure.

To remove a storyline entirely (all missions and agent progress on that arc), then re-seed after editing the pack:

```bash
delete_storyline "Orientation" --check
delete_storyline "Orientation"              # type the storyline name to confirm
delete_storyline "Orientation" -y           # hardcore — skips typed confirm; use only after --check
delete_storyline "Orientation" --write-sql  # write ./{name}-delete.sql only
```

User accounts and other storylines are not deleted. To change immutable fields (group name, slugs, access structure), edit the pack, delete the old storyline, then run `seed_storyline`.

## Testing seed

`seed_testing_storyline.sql` includes **inlined** `brief_markdown` and `debrief_markdown` for the test fixture. Do not edit those bodies by hand.

Recreate local test database after schema or seed changes:

```bash
create_test_db --force
```

Pytest builds its own temporary databases from this seed; you do not need `create_test_db` before running tests.
