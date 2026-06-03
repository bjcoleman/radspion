# Radspion

Secret-organization-themed mission platform for coursework. Agents complete **missions** in story **arcs** by submitting **field data**, meeting prerequisites, and reading Mission Briefs and Debriefs. Operators configure missions via SQL seed; agents sign in with Google OAuth (any account).

## Documentation

| Topic | Location |
|-------|----------|
| Design overview and reading order | [docs/README.md](docs/README.md) |
| Use cases (build backlog) | [docs/design/use-cases.md](docs/design/use-cases.md) |
| Agent UI rules + JSON endpoints | [docs/design/06-agent-experience.md](docs/design/06-agent-experience.md) |
| JSON API (`POST /api/submit`) | [docs/api.yaml](docs/api.yaml) |
| UI mockups (not production JS) | [docs/ui/README.md](docs/ui/README.md) |
| Dev setup, testing, Ruff, deploy | [docs/dev.md](docs/dev.md) |
| Operator SQL workflow | [docs/design/07-operator-setup.md](docs/design/07-operator-setup.md) |

## Repository layout

```
src/radspion/          Application package
src/radspion/sql/      Schema and seeds (mission markdown inlined in SQL)
deploy/                nginx vhost, systemd unit (production)
docs/                  Design docs, API outline, UI mockups
scripts/               DB bootstrap (create_empty_db.sh, create_test_db.sh, seed_storyline.sh)
database/              SQLite file (gitignored)
tests/                 Unit tests
```

## Quick start (development)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
./scripts/create_empty_db.sh
make
```

For an empty DB: `./scripts/create_empty_db.sh`, generate pack SQL in **radspion-missions**, set `RADSPION_MISSIONS_ROOT` in `.env`, then `./scripts/seed_storyline.sh PACK`. For dev/test with sample agents and `es-*` missions: `./scripts/create_test_db.sh`. See [05-testing-storyline.md](docs/design/05-testing-storyline.md).

See [docs/dev.md](docs/dev.md) for OAuth, CI, and deployment.

## Stack

- Python 3.12+, Flask + Jinja, SQLite 3
- Google OAuth, session-backed **`POST /api/submit`** for field data
- Ruff (lint/format), pytest + 90% coverage gate
