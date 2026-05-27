# Radspion

Secret-organization-themed mission platform for coursework. Agents in **groups** complete **missions** using unlock codes, prerequisites, Mission Briefs, and Debriefs. Operators configure classes via SQL seed; agents sign in with Google (`@moravian.edu`).

## Documentation

| Topic | Location |
|-------|----------|
| Design overview and reading order | [docs/README.md](docs/README.md) |
| Use cases (build backlog) | [docs/design/use-cases.md](docs/design/use-cases.md) |
| Agent UI rules + JSON endpoints | [docs/design/06-agent-experience.md](docs/design/06-agent-experience.md) |
| OpenAPI outline (unlock / submit) | [docs/api.yaml](docs/api.yaml) |
| UI mockups (not production JS) | [docs/ui/README.md](docs/ui/README.md) |
| Dev setup, testing, Ruff, deploy | [docs/dev.md](docs/dev.md) |
| Operator SQL workflow | [docs/design/07-operator-setup.md](docs/design/07-operator-setup.md) |

## Repository layout

```
src/radspion/          Application package
src/radspion/sql/      Schema and example seed
content/missions/      Live mission Brief / Debrief (basic-training default)
content/samples/       Sample mission packs (example class)
deploy/                nginx vhost, systemd unit (production)
docs/                  Design docs, API outline, UI mockups
scripts/               DB bootstrap, deploy group setup
database/              SQLite file (gitignored)
tests/                 Unit tests
```

## Quick start (development)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
./scripts/bootstrap_sample_class.sh
make
```

See [docs/dev.md](docs/dev.md) for OAuth, CI, and deployment.

## Stack

- Python 3.12+, Flask + Jinja, SQLite 3
- Google OAuth, session-backed JSON for unlock and mission submit
- Ruff (lint/format), pytest + 90% coverage gate
