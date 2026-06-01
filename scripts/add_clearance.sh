#!/bin/bash
# Add a registration clearance code to database/radspion.db.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DB_PATH="database/radspion.db"

if [ $# -ne 1 ]; then
    echo "Usage: $0 \"clearance code\""
    exit 1
fi

CODE="$1"

if [ -z "$CODE" ]; then
    echo "Error: clearance code must not be empty."
    exit 1
fi

if [ ! -f "$DB_PATH" ]; then
    echo "Error: Database not found at $DB_PATH"
    exit 1
fi

CODE_SQL="${CODE//\'/\'\'}"

sqlite3 "$DB_PATH" "INSERT INTO registration_access_codes (code) VALUES ('$CODE_SQL');"

STORED="$(sqlite3 "$DB_PATH" "SELECT code FROM registration_access_codes WHERE code = '$CODE_SQL' LIMIT 1;")"
if [ "$STORED" != "$CODE" ]; then
    echo "Error: Could not verify clearance code in database."
    exit 1
fi

echo "Added clearance code."
