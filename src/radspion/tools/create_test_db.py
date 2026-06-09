"""CLI entry point to create the Testing Storyline dev/test database."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from os import getenv
from pathlib import Path

from radspion.project_paths import database_path, load_tool_env, testing_seed_path
from radspion.sql_utils import execute_sql_file
from radspion.tools._db_helpers import DbToolError, create_schema_database

_ALICE_EMAIL = "alice@moravian.edu"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create database with schema and Testing Storyline seed (dev/test only).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing database without prompting",
    )
    parser.add_argument(
        "--bind-dev-email",
        action="store_true",
        help="After recreate, point the Alice fixture at DEV_EMAIL in .env",
    )
    return parser.parse_args(argv)


def _load_testing_seed(connection: sqlite3.Connection) -> None:
    seed_path = testing_seed_path()
    if not seed_path.is_file():
        raise DbToolError(f"Missing {seed_path}")
    execute_sql_file(connection, seed_path)


def _dev_email() -> str:
    load_tool_env()
    raw = getenv("DEV_EMAIL")
    if not raw or not raw.strip():
        raise DbToolError("DEV_EMAIL is not set in .env.")
    return raw.strip()


def _bind_dev_email(db_path: Path) -> None:
    dev_email = _dev_email()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            UPDATE users
            SET email = ?, display_name = REPLACE(display_name, 'Alice', 'Developer')
            WHERE email = ?
            """,
            (dev_email, _ALICE_EMAIL),
        )
        row = conn.execute(
            "SELECT 1 FROM users WHERE email = ? LIMIT 1",
            (dev_email,),
        ).fetchone()
        conn.commit()
    if row is None:
        raise DbToolError("Could not update Alice.")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    db_path = database_path()
    try:
        create_schema_database(db_path, force=args.force, after_schema=_load_testing_seed)
        if args.bind_dev_email:
            _bind_dev_email(db_path)
    except DbToolError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Created test database at {db_path}")
    print("  Sample agents: Alice, Bob, Charlie, Diana (see docs/design/05-testing-storyline.md)")
    if args.bind_dev_email:
        print(f"Updated Alice to {_dev_email()} (display name Developer).")
        print("Sign in with Google using that email to use Alice's mission progress.")
    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
