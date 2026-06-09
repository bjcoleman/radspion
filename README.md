# Radspion

Secret-organization-themed mission platform for coursework. Agents complete **missions** in story **arcs** using clearance codes, prerequisites, Mission Briefs, and Debriefs. Operators configure missions via SQL seed, and agents sign in with Google OAuth (any account).

## Documentation

| Topic | Location |
|-------|----------|
| Design overview and reading order | [docs/README.md](docs/README.md) |
| Use cases (build backlog) | [docs/design/use-cases.md](docs/design/use-cases.md) |
| Agent UI rules + JSON endpoints | [docs/design/06-agent-experience.md](docs/design/06-agent-experience.md) |
| JSON API (`/api/clearance`, mission submit) | [docs/api.yaml](docs/api.yaml) |
| UI mockups (not production JS) | [docs/ui/README.md](docs/ui/README.md) |
| Dev setup, testing, Ruff, deploy | [docs/dev.md](docs/dev.md) |
| Operator SQL workflow | [docs/design/07-operator-setup.md](docs/design/07-operator-setup.md) |
| Mission pack authoring | [docs/missions/README.md](docs/missions/README.md) |

## Repository layout

```
src/radspion/          Application package (includes tools/ CLIs)
src/radspion/sql/      Schema and seeds (mission markdown inlined in SQL)
deploy/                nginx vhost, systemd unit (production)
docs/                  Design docs, API outline, UI mockups, mission authoring
database/              SQLite file (gitignored)
tests/                 Unit tests
```

## Quick start (development)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
create_empty_db --force
make
```

For an empty DB: `create_empty_db --force`, set `RADSPION_MISSIONS_ROOT` in `.env`, then `seed_storyline PACK`. For dev/test with sample agents and `es-*` missions: `create_test_db --force`. See [05-testing-storyline.md](docs/design/05-testing-storyline.md).

See [docs/dev.md](docs/dev.md) for OAuth, CI, and deployment.

## Stack

- Python 3.12+, Flask + Jinja, SQLite 3
- Google OAuth, session-backed JSON for clearance and mission submit
- Ruff (lint/format), pytest + 90% coverage gate
