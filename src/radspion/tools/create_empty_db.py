"""CLI entry point to create a schema-only radspion database."""

from __future__ import annotations

import argparse
import sys

from radspion.project_paths import database_path
from radspion.tools._db_helpers import DbToolError, create_schema_database


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create database/radspion.db with schema only (no missions).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing database without prompting",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    db_path = database_path()
    try:
        create_schema_database(db_path, force=args.force)
    except DbToolError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"Created database at {db_path} (schema only, no missions).")
    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
