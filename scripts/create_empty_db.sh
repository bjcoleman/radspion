#!/bin/bash
# Create database/radspion.db with schema only (no missions).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DB_PATH="database/radspion.db"
SCHEMA_FILE="src/radspion/sql/schema.sql"

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

if [ ! -f "$SCHEMA_FILE" ]; then
    echo "Error: Missing $SCHEMA_FILE"
    exit 1
fi

echo "Creating database with schema..."
sqlite3 "$DB_PATH" < "$SCHEMA_FILE"

echo "Created database at $DB_PATH (schema only, no missions)."
