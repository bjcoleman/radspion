#!/bin/bash
# Create database/radspion.db with schema + default orientation seed (basic-training only).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DB_PATH="database/radspion.db"
SCHEMA_FILE="src/radspion/sql/schema.sql"
ORIENTATION_SEED="src/radspion/sql/seed_orientation.sql"

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

for f in "$SCHEMA_FILE" "$ORIENTATION_SEED"; do
    if [ ! -f "$f" ]; then
        echo "Error: Missing $f"
        exit 1
    fi
done

echo "Creating database with schema..."
sqlite3 "$DB_PATH" < "$SCHEMA_FILE"

echo "Loading orientation seed (basic-training)..."
sqlite3 "$DB_PATH" < "$ORIENTATION_SEED"

echo "Created database at $DB_PATH (Orientation + basic-training only)."
echo "For the full example class, run: ./scripts/bootstrap_sample_class.sh"
