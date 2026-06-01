#!/bin/bash
# Recreate the test database and point the Alice fixture at DEV_EMAIL in .env.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ALICE_EMAIL="alice@moravian.edu"
DB_PATH="database/radspion.db"

if [ ! -f .env ]; then
    echo "Error: .env not found."
    exit 1
fi

if ! grep -qE '^DEV_EMAIL=' .env; then
    echo "Error: DEV_EMAIL is not set in .env."
    exit 1
fi

DEV_EMAIL="$(grep -E '^DEV_EMAIL=' .env | head -1 | cut -d= -f2- | tr -d '[:space:]')"
if [ -z "$DEV_EMAIL" ]; then
    echo "Error: DEV_EMAIL is not set in .env."
    exit 1
fi

"$SCRIPT_DIR/create_test_db.sh"

DEV_EMAIL_SQL="${DEV_EMAIL//\'/\'\'}"
sqlite3 "$DB_PATH" "UPDATE users SET email = '$DEV_EMAIL_SQL', display_name = REPLACE(display_name, 'Alice', 'Developer') WHERE email = '$ALICE_EMAIL';"

if ! sqlite3 "$DB_PATH" "SELECT 1 FROM users WHERE email = '$DEV_EMAIL_SQL' LIMIT 1;" | grep -q 1; then
    echo "Error: Could not update Alice."
    exit 1
fi

echo "Updated Alice to $DEV_EMAIL (display name Developer)."
echo "Sign in with Google using that email to use Alice's mission progress."
