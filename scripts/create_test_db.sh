#!/bin/bash
# Create database/radspion.db with schema, orientation, registration codes,
# and Testing Storyline seed (dev/test only — not for production).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DB_PATH="database/radspion.db"
SCHEMA_FILE="src/radspion/sql/schema.sql"
ORIENTATION_SEED="src/radspion/sql/seed_orientation.sql"
REGISTRATION_CODES_SEED="src/radspion/sql/seed_registration_access_codes.sql"
TESTING_STORYLINE_SEED="src/radspion/sql/seed_testing_storyline.sql"

if [ -f "$DB_PATH" ]; then
    echo "Warning: Database file already exists at $DB_PATH"
    read -p "Overwrite? (y/n): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Aborted."
        exit 0
    fi
    rm "$DB_PATH"
fi

mkdir -p database

for f in "$SCHEMA_FILE" "$ORIENTATION_SEED" "$REGISTRATION_CODES_SEED" "$TESTING_STORYLINE_SEED"; do
    if [ ! -f "$f" ]; then
        echo "Error: Missing $f"
        exit 1
    fi
done

echo "Creating database with schema..."
sqlite3 "$DB_PATH" < "$SCHEMA_FILE"

echo "Loading orientation seed (basic-training)..."
sqlite3 "$DB_PATH" < "$ORIENTATION_SEED"

echo "Loading registration access codes..."
sqlite3 "$DB_PATH" < "$REGISTRATION_CODES_SEED"

echo "Loading Testing Storyline seed (dev/test)..."
sqlite3 "$DB_PATH" < "$TESTING_STORYLINE_SEED"

echo "Created test database at $DB_PATH"
echo "  Sample agents: Alice, Bob, Charlie, Diana (see docs/design/05-testing-storyline.md)"
echo "  Storyline unlock: EXAMPLE UNLOCK"
