#!/bin/bash
# One-time setup on webapps: let nginx (www-data) connect to the gunicorn Unix socket.
# The radspion system user should already exist (primary group radspion).
# Run with sudo: sudo ./scripts/setup_deploy_group.sh
set -euo pipefail

GROUP=radspion

if ! getent group "$GROUP" >/dev/null; then
  echo "error: group $GROUP not found; create the radspion user first (adduser radspion)" >&2
  exit 1
fi

usermod -aG "$GROUP" www-data

echo "www-data added to group $GROUP. Members:"
getent group "$GROUP"
