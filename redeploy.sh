#!/bin/bash
# Production redeploy on webapps as user radspion (see docs/dev.md).
# Requires passwordless sudo for systemctl — install deploy/sudoers-radspion.
sudo systemctl stop radspion
git pull origin main
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
sudo systemctl start radspion
