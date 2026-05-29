# Development and deployment

## Overview

Radspion is a Flask + SQLite application for coursework. This document covers local development and production deployment on the **department web server**.

### Prerequisites

- Python 3.12 or later
- `git`
- `sqlite3` CLI
- Moravian Google account (`@moravian.edu`) for OAuth setup

## Google OAuth setup

1. Create a project in [Google Cloud Console](https://console.cloud.google.com/) with your `@moravian.edu` account.
2. Configure the **OAuth consent screen** (Internal audience for Moravian).
3. Create a **Web application** OAuth client with authorized origins and redirect URIs for:
   - Local dev: `http://localhost:8000/` (trailing slash required)
   - Production: `https://www.radspion.com` only (apex and `.org` redirect in nginx)
4. Save **Client ID** and **Client secret** (secret is shown only once).

## Configuration (`.env`)

Create `.env` in the project root. **Never commit** this file.

| Variable | Purpose |
|----------|---------|
| `BASE_URL` | App base URL (`http://localhost:8000` in dev; `https://www.radspion.com` in prod) |
| `GOOGLE_CLIENT_ID` | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret |
| `SECRET_KEY` | Flask session signing (**required**; app exits at startup if unset). Generate with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `DATABASE_PATH` | Optional; default `database/radspion.db` |

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Database

**Production-style database** (schema + Orientation + `basic-training` only):

```bash
./scripts/create_empty_db.sh
```

**Full example class** (copies five sample missions into `content/missions/`, loads example seed, prompts to replace Alice with your account):

```bash
./scripts/bootstrap_sample_class.sh
```

SQL: `schema.sql`, `seed_orientation.sql`, `seed_registration_access_codes.sql`, `seed_example_class.sql`. Sample Brief/Debrief sources: `content/samples/example-class/`.

### Application layout

Flat modules under `src/radspion/` (similar to [cost_sharing](https://github.com/MoravianUniversity/cost_sharing)):

| Module | Role |
|--------|------|
| `config.py` | Load `SECRET_KEY`, `DATABASE_PATH`; fail fast if required values missing |
| `database.py` | `DatabaseError`, `DatabaseRadspionStorage` |
| `radspion.py` | Business logic (`Radspion` class) |
| `app.py` | `launch()` loads `.env`, then config → DB → storage → `Radspion` → `create_app()` |
| `web/main.py` | Flask blueprint for public pages |

`launch()` prints configuration/database errors to stderr and exits with code 1. Tests call `load_config(testing=True)` and `create_app(config, Radspion(InMemoryRadspionStorage(...)))` so no real database is required.

### Running the app

Once application code exists:

```bash
python -m radspion.app
```

## Makefile

Run from the project root (not from `src/`).

| Target | Action |
|--------|--------|
| `make` (default) | Unit tests, then Ruff lint and format check |
| `make test` | `pytest` only |
| `make style` | Ruff only |

Before you push or open a PR, run **`make`** and fix anything that fails. CI runs the same checks.

**Tests** must pass with **at least 90% line coverage** on the `radspion` package. Threshold and pytest options are in [`pytest.ini`](../pytest.ini). Use `# pragma: no cover` only sparingly and by team agreement.

**Static analysis** (Ruff lint and format) must pass with no violations. Rule selection and formatting options are in [`pyproject.toml`](../pyproject.toml) under `[tool.ruff]`. Use `# noqa: CODE` on a line only sparingly and by team agreement, after discussing why the rule should not apply there.

## CI/CD (GitHub Actions)

- **Unit Tests** — `pytest` on every push/PR
- **Static Analysis** — Ruff lint and format check (separate workflow for clearer failure reports)
- **Redeploy** — manual `workflow_dispatch`; SSH to the department server and run `redeploy.sh`

Configure repository secrets for redeploy (ProxyJump via jump box):

| Secret | Example (Moravian) |
|--------|----------------------|
| `DEPLOY_SSH_KEY` | Full private key file
| `DEPLOY_JUMP_USER` | user on jumpbox |
| `DEPLOY_JUMP_HOST` | hostname of jumpbox |
| `DEPLOY_USER` | user on server |
| `DEPLOY_HOST` | hostname of server |


The workflow uses [appleboy/ssh-action](https://github.com/appleboy/ssh-action) with `proxy_*` for the jump box (same key for jump and webapps).


## Production (webapps)

Canonical URL: **`https://www.radspion.com`**. Gunicorn binds **`unix:/run/radspion/gunicorn.sock`** (see `deploy/radspion.service`). Repo on server: **`/home/radspion/radspion`**.

### Deploy user and permissions

Create the `radspion` account, SSH access, nginx socket access, and passwordless `systemctl` for `redeploy.sh`. Run as an admin with `sudo`, except step 2 (log in as `radspion`).

**1. Create the user**

```bash
sudo adduser radspion
```

**2. SSH keys (as `radspion`)** — `su - radspion` or `sudo -u radspion -i`:

```bash
ssh-keygen
```

**3. Socket permissions (admin)**

```bash
sudo usermod -aG radspion www-data
```

**4. Sudoers for redeploy (admin)** — install `deploy/sudoers-radspion` from this repo:

```bash
sudo cp /home/radspion/radspion/deploy/sudoers-radspion /etc/sudoers.d/radspion
sudo chmod 440 /etc/sudoers.d/radspion
sudo visudo -cf /etc/sudoers.d/radspion
```

### TLS certificates (one-time, admin)

Issue one certificate for all four hostnames (canonical name first). DNS must already point at webapps.

```bash
sudo certbot certonly --nginx \
  -d www.radspion.com -d radspion.com -d radspion.org -d www.radspion.org
```

### Application setup (as radspion)

* Clone the repo:


* Create venv and install libraries

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

* Create `~/radspion/.env` (see Configuration above). 


* Initialize the database:


```bash
./scripts/create_empty_db.sh
```

  Use `./scripts/bootstrap_sample_class.sh` instead for the full example class locally.


### systemd (admin, after clone)

Install the unit and start gunicorn before nginx serves traffic to this app

```bash
sudo cp /home/radspion/radspion/deploy/radspion.service /etc/systemd/system/radspion.service
sudo systemctl daemon-reload
sudo systemctl enable --now radspion
```

Confirm the app responds on the Unix socket

```bash
curl --unix-socket /run/radspion/gunicorn.sock http://localhost/
```


### nginx (admin)

Install the vhost and reload nginx.

```bash
sudo cp /home/radspion/radspion/deploy/nginx/radspion.conf /etc/nginx/conf.d/radspion.conf
sudo nginx -t && sudo systemctl reload nginx
```

Check HTTPS through nginx (from your laptop, or on webapps with loopback so SNI matches):

```bash
curl -sS https://www.radspion.com/
# on webapps only:
curl -sS --resolve www.radspion.com:443:127.0.0.1 https://www.radspion.com/
```

If `curl https://www.radspion.com` **hangs on webapps** but works from your laptop, that is usually a **firewall / hairpin** issue (traffic to the public IP from inside the box), not a broken app.


### Redeploy

As `radspion` (or GitHub Actions with `DEPLOY_USER=radspion`):

```bash
cd /home/radspion/radspion
./redeploy.sh
```

App-only deploys do not require an nginx reload.

## UI mockups

Static prototypes live in `docs/ui/`. They inform Jinja templates and CSS; **mock-only JavaScript** (hard-coded modal outcomes) is not production code. Implement server-rendered pages plus `fetch` to the JSON API per `docs/api.yaml` and `docs/design/06-agent-experience.md`.

### Transmission modal (`static/js/transmission-modal.js`)

Shared progress animation for access-code validation, mission unlock, and field submission. Include `templates/_transmission_modal.html` in the page and load the script from `extra_body`.

**Presets** (`RadspionTransmission.PRESET`):

| Preset | Modal title | Step 3 label |
|--------|-------------|--------------|
| `ACCESS_CODE` | Secure channel | access code |
| `UNLOCK_CODE` | Secure channel | unlock code |
| `COMPLETION_DATA` | Secure transmission | completion data |

All presets use the same four steps: initiating secure connection → establishing agent identity → transferring *&lt;data&gt;* → checking agency records. Total duration targets **~3 seconds** with per-step jitter.

**`transmit({ preset, request, renderOutcome })`** runs `request()` (typically `fetch`) **in parallel** with the progress animation. The outcome panel is shown only after **both** complete; a fast server response still waits for the animation (unless the user has **Reduce motion** enabled, in which case the outcome appears as soon as the request finishes).

Manual check: open `docs/ui/transmission-modal-demo.html` in a browser (includes slow POST on unlock demo to verify animation wins the race).
