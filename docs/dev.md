# Development and deployment

## Overview

Radspion is a Flask + SQLite application for coursework. This document covers local development, testing, static analysis, and production deployment on the **department web server** (not AWS Learner Lab / `register_ip` flow).

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
| `JWT_SECRET` | Session/token signing (`python3 -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `DATABASE_PATH` | Optional; default `database/radspion.db` when implemented |

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

SQL: `schema.sql`, `seed_orientation.sql`, `seed_example_class.sql`. Sample Brief/Debrief sources: `content/samples/example-class/`.

### Running the app

Once application code exists:

```bash
python -m radspion.app
```

## Mission markdown (Brief / Debrief)

The app uses **[Python-Markdown](https://python-markdown.github.io/)** (`markdown` on PyPI), not Mistune. For coursework write-ups with **fenced code blocks** (triple backticks), including blocks inside numbered or bulleted lists, enable:

- `markdown.extensions.fenced_code` — ``` blocks between paragraphs
- `markdown.extensions.sane_lists` — stable list numbering when items have multiple blocks
- `markdown.extensions.tables` — optional pipe tables

**List + code:** In CommonMark, a fenced block inside a list item must be indented to the **content column** of that item (typically four spaces past the list marker). Example:

```markdown
1. Run diagnostics:

   ```bash
   git status
   ```

2. Continue with the next step.
```

Mistune and minimal converters often break nested fences or list numbering; Python-Markdown with `sane_lists` is the recommended default for this project.

## Testing

Run from the project root (not from `src/`):

```bash
pytest
```

`pytest.ini` enforces **90%** coverage on the `radspion` package (`--cov-fail-under=90`). CI will fail until application code and tests exist. Use `# pragma: no cover` only sparingly and by team agreement.

## Static analysis (Ruff)

Ruff replaces Pylint for this project. Configuration is in `pyproject.toml` under `[tool.ruff]`.

**Defaults vs our config:** Ruff’s default rule set is only `E` (pycodestyle errors) and `F` (pyflakes). That is a minimal bar. We also enable `W`, `I` (import sort), `B` (bugbear), `UP` (modern Python), and `SIM` (simplifications)—a practical set for teaching without Pylint’s per-function complexity caps.

```bash
ruff check src tests
ruff format --check src tests   # or: ruff format src tests
```

Disable a rule locally only when necessary: `# noqa: CODE` on the line, after discussion.

## Makefile

| Target | Action |
|--------|--------|
| `make` | Tests, then Ruff lint + format check |
| `make test` | `pytest` |
| `make style` | `ruff check` + `ruff format --check` |

## CI/CD (GitHub Actions)

- **Unit Tests** — `pytest` on every push/PR
- **Static Analysis** — Ruff lint and format check (separate workflow for clearer failure reports)
- **Redeploy** — manual `workflow_dispatch`; SSH to the department server and run `redeploy.sh`

Configure repository secrets for redeploy: `DEPLOY_SSH_KEY`, `DEPLOY_HOST`, `DEPLOY_USER` (`radspion`). The workflow SSHs to `/home/radspion/radspion` and runs `redeploy.sh`.

## Production (webapps)

Production serves **only** `https://www.radspion.com`. Other hostnames redirect in nginx. The app runs as Unix user **`radspion`** with gunicorn on **`unix:/run/radspion/gunicorn.sock`** (no TCP port).

Repo path on the server: **`/home/radspion/radspion`**.

### A. One-time setup (admin with sudo)

Run from any account that can `sudo`. Replace the example SSH public key with yours.

```bash
# 1. Deploy user (set password when prompted; you can disable password login later)
sudo adduser radspion

# 2. SSH key login for radspion
sudo install -d -m 700 -o radspion -g radspion /home/radspion/.ssh
sudo tee /home/radspion/.ssh/authorized_keys >/dev/null <<'EOF'
ssh-ed25519 AAAA...paste-your-public-key-here...
EOF
sudo chown radspion:radspion /home/radspion/.ssh/authorized_keys
sudo chmod 600 /home/radspion/.ssh/authorized_keys

# 3. Clone as radspion (GitHub deploy key or HTTPS — configure auth first)
sudo -u radspion -i
git clone https://github.com/YOUR_ORG/radspion.git /home/radspion/radspion
exit

# 4. Socket permissions — nginx (www-data) must be in group radspion
cd /home/radspion/radspion
sudo ./scripts/setup_deploy_group.sh

# 5. Passwordless systemctl for redeploy.sh (optional but recommended)
sudo cp deploy/sudoers-radspion /etc/sudoers.d/radspion
sudo chmod 440 /etc/sudoers.d/radspion
sudo visudo -cf /etc/sudoers.d/radspion

# 6. TLS (four names, one cert; canonical first)
sudo certbot certonly --nginx \
  -d www.radspion.com -d radspion.com -d radspion.org -d www.radspion.org

# Restore 01-block-bad-hostnames.conf to ONLY the self-signed default_server (return 444)
# if certbot added a second server block for Radspion names.

# 7. nginx vhost
sudo cp /home/radspion/radspion/deploy/nginx/radspion.conf /etc/nginx/conf.d/radspion.conf
sudo nginx -t && sudo systemctl reload nginx

# 8. systemd unit
sudo cp /home/radspion/radspion/deploy/radspion.service /etc/systemd/system/radspion.service
sudo systemctl daemon-reload
sudo systemctl enable radspion
```

### B. App setup (as radspion)

```bash
sudo -u radspion -i
cd ~/radspion

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Create .env (never commit); see Configuration table above
$EDITOR .env

./scripts/create_empty_db.sh   # production default, or bootstrap_sample_class.sh for demo

sudo systemctl start radspion
exit
```

Example production `.env` entries: `BASE_URL=https://www.radspion.com`, OAuth client values, `JWT_SECRET`.

### C. Verify

```bash
curl -sI https://radspion.com/ | grep -i location
curl -s https://www.radspion.com/
sudo systemctl status radspion
ls -l /run/radspion/gunicorn.sock    # group radspion, mode srw-rw----
sudo certbot renew --dry-run
```

### Socket permissions (how it fits together)

| Piece | Detail |
|-------|--------|
| gunicorn | Runs as `User=radspion`, `Group=radspion`; creates `/run/radspion/gunicorn.sock` |
| `UMask=0007` | Socket is group-readable/writable, not world-accessible |
| nginx | Runs as `www-data`; `setup_deploy_group.sh` adds `www-data` to group `radspion` |
| nginx config | `proxy_pass http://unix:/run/radspion/gunicorn.sock:/;` |

If you get **502 Bad Gateway**, check: `systemctl status radspion`, socket exists, and `groups www-data` includes `radspion`.

### Redeploy

As `radspion` (or GitHub Actions with `DEPLOY_USER=radspion`):

```bash
cd /home/radspion/radspion
./redeploy.sh
```

App-only deploys do not require an nginx reload.

### Layout reference

| Piece | Location |
|-------|----------|
| Deploy user / home | `radspion` → `/home/radspion/radspion` |
| nginx vhost (template) | `deploy/nginx/radspion.conf` |
| systemd unit (template) | `deploy/radspion.service` |
| sudoers fragment (template) | `deploy/sudoers-radspion` |
| gunicorn socket | `unix:/run/radspion/gunicorn.sock` |
| TLS files | `/etc/letsencrypt/live/www.radspion.com/` |

## UI mockups

Static prototypes live in `docs/ui/`. They inform Jinja templates and CSS; **mock-only JavaScript** (hard-coded modal outcomes) is not production code. Implement server-rendered pages plus `fetch` to the JSON API per `docs/api.yaml` and `docs/design/06-agent-experience.md`.
