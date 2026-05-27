#!/bin/bash
# Install example-class mission markdown into content/missions/, then create the sample database.
# Prompts to replace Alice (user id 1) with your Google account for local login.
#
# Production / empty dev DB: use create_empty_db.sh (schema + orientation seed only).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DB_PATH="database/radspion.db"
SCHEMA_FILE="src/radspion/sql/schema.sql"
ORIENTATION_SEED="src/radspion/sql/seed_orientation.sql"
EXAMPLE_SEED="src/radspion/sql/seed_example_class.sql"
SAMPLE_SRC="content/samples/example-class"

SAMPLE_SLUGS=(
    global-hidden
    read-the-manual
    learn-the-system
    remote-access
    identify-the-traitor
)

if [ -f "$DB_PATH" ]; then
    echo "Warning: Database file already exists at $DB_PATH"
    read -p "Overwrite? (y/n): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Aborted."
        exit 0
    fi
    rm "$DB_PATH"
fi

for f in "$SCHEMA_FILE" "$ORIENTATION_SEED" "$EXAMPLE_SEED"; do
    if [ ! -f "$f" ]; then
        echo "Error: Missing $f"
        exit 1
    fi
done

for slug in "${SAMPLE_SLUGS[@]}"; do
    if [ ! -d "$SAMPLE_SRC/$slug" ]; then
        echo "Error: Missing sample mission content at $SAMPLE_SRC/$slug"
        exit 1
    fi
done

echo "Installing example-class mission content into content/missions/..."
mkdir -p content/missions
for slug in "${SAMPLE_SLUGS[@]}"; do
    rm -rf "content/missions/$slug"
    cp -a "$SAMPLE_SRC/$slug" "content/missions/$slug"
done

mkdir -p database

echo "Creating database with schema..."
sqlite3 "$DB_PATH" < "$SCHEMA_FILE"

echo "Loading orientation seed (basic-training)..."
sqlite3 "$DB_PATH" < "$ORIENTATION_SEED"

echo "Loading example class seed..."
sqlite3 "$DB_PATH" < "$EXAMPLE_SEED"

ALICE_CHECK=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users WHERE id = 1;")
if [ "$ALICE_CHECK" -eq 0 ]; then
    echo "Error: Alice (user id 1) not found after seed."
    exit 1
fi

echo ""
echo "Example class loaded. Update Alice so you can sign in with your Google account."
echo ""
read -p "Email (@moravian.edu): " email
read -p "Display name: " name

if [ -z "$email" ] || [ -z "$name" ]; then
    echo "Error: Email and display name are required."
    exit 1
fi

EMAIL_ESC=$(echo "$email" | sed "s/'/''/g")
NAME_ESC=$(echo "$name" | sed "s/'/''/g")

sqlite3 "$DB_PATH" "UPDATE users SET email = '$EMAIL_ESC', display_name = '$NAME_ESC' WHERE id = 1;"

echo ""
echo "Sample environment ready at $DB_PATH"
echo "  Email: $email"
echo "  Display name: $name"
echo "  Live mission content: content/missions/ (basic-training + example-class copies)"
