# Radspion

Secret-organization-themed mission platform for coursework. Agents complete **missions** in story **arcs** using unlock codes, prerequisites, Mission Briefs, and Debriefs. Operators configure missions via SQL seed; new agents need a registration access code, then Google OAuth (any account); returning agents use Google only.

## Documentation

| Topic | Location |
|-------|----------|
| Design overview and reading order | [docs/README.md](docs/README.md) |
| Use cases (build backlog) | [docs/design/use-cases.md](docs/design/use-cases.md) |
| Agent UI rules + JSON endpoints | [docs/design/06-agent-experience.md](docs/design/06-agent-experience.md) |
| JSON API (`/api/access`, `/api/unlock`, mission submit) | [docs/api.yaml](docs/api.yaml) |
| UI mockups (not production JS) | [docs/ui/README.md](docs/ui/README.md) |
| Dev setup, testing, Ruff, deploy | [docs/dev.md](docs/dev.md) |
| Operator SQL workflow | [docs/design/07-operator-setup.md](docs/design/07-operator-setup.md) |

## Repository layout

```
src/radspion/          Application package
src/radspion/sql/      Schema and seeds (mission markdown inlined in SQL)
deploy/                nginx vhost, systemd unit (production)
docs/                  Design docs, API outline, UI mockups
scripts/               DB bootstrap (create_empty_db.sh, create_test_db.sh, add_clearance.sh)
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

For production-like DB: `./scripts/create_empty_db.sh`. For dev/test with sample agents and `es-*` missions: `./scripts/create_test_db.sh`. See [05-testing-storyline.md](docs/design/05-testing-storyline.md) and [04-example-data-walkthrough.md](docs/design/04-example-data-walkthrough.md).

See [docs/dev.md](docs/dev.md) for OAuth, CI, and deployment.

## Stack

- Python 3.12+, Flask + Jinja, SQLite 3
- Google OAuth, session-backed JSON for unlock and mission submit
- Ruff (lint/format), pytest + 90% coverage gate
