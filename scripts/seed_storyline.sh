#!/bin/bash
# Load a generated storyline pack SQL file into an existing database (INSERT only).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

usage() {
    echo "Usage: $0 PACK"
    echo "  PACK  Storyline pack name (e.g. orientation) or path to pack directory"
    exit 1
}

if [ $# -ne 1 ]; then
    usage
fi

if [ ! -f .env ]; then
    echo "Error: .env not found."
    exit 1
fi

if ! grep -qE '^RADSPION_MISSIONS_ROOT=' .env; then
    echo "Error: RADSPION_MISSIONS_ROOT is not set in .env."
    exit 1
fi

RADSPION_MISSIONS_ROOT="$(grep -E '^RADSPION_MISSIONS_ROOT=' .env | head -1 | cut -d= -f2- | tr -d '[:space:]')"
if [ -z "$RADSPION_MISSIONS_ROOT" ]; then
    echo "Error: RADSPION_MISSIONS_ROOT is empty in .env."
    exit 1
fi

DB_PATH="database/radspion.db"
if grep -qE '^DATABASE_PATH=' .env; then
    DB_PATH="$(grep -E '^DATABASE_PATH=' .env | head -1 | cut -d= -f2- | tr -d '[:space:]')"
fi
if [ -z "$DB_PATH" ]; then
    echo "Error: DATABASE_PATH is empty in .env."
    exit 1
fi

PACK_ARG="$1"
if [ -d "$PACK_ARG" ]; then
    PACK_DIR="$(cd "$PACK_ARG" && pwd)"
else
    PACK_DIR="$(cd "$RADSPION_MISSIONS_ROOT/$PACK_ARG" && pwd)"
fi

PACK_NAME="$(basename "$PACK_DIR")"
PACK_SQL="$PACK_DIR/$PACK_NAME.sql"

if [ ! -d "$PACK_DIR" ]; then
    echo "Error: Pack directory not found: $PACK_DIR"
    exit 1
fi

if [ ! -f "$PACK_SQL" ]; then
    echo "Error: Missing $PACK_SQL"
    echo "Generate it from radspion with:"
    echo "  .venv/bin/generate_storyline $PACK_NAME"
    exit 1
fi

if [ ! -f "$DB_PATH" ]; then
    echo "Error: Database not found at $DB_PATH"
    echo "Create it first with ./scripts/create_empty_db.sh"
    exit 1
fi

if ! sqlite3 "$DB_PATH" "SELECT 1 FROM sqlite_master WHERE type='table' AND name='groups' LIMIT 1;" | grep -q 1; then
    echo "Error: Database at $DB_PATH has no schema (groups table missing)."
    echo "Run ./scripts/create_empty_db.sh first."
    exit 1
fi

echo "Loading storyline pack $PACK_NAME from $PACK_SQL..."
sqlite3 "$DB_PATH" < "$PACK_SQL"
echo "Loaded storyline pack $PACK_NAME into $DB_PATH"
