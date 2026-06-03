#!/usr/bin/env python3
"""Validate a storyline pack SQL file before seeding."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from radspion.pack_sql_validation import PackValidationError, validate_pack_sql


def _default_schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "src" / "radspion" / "sql" / "schema.sql"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate that a storyline pack SQL file has disjoint listing and "
            "completion data strings and does not overlap strings already in the database."
        )
    )
    parser.add_argument("pack_sql", type=Path, help="Path to generated pack SQL")
    parser.add_argument("database", type=Path, help="Path to target SQLite database")
    parser.add_argument(
        "--schema",
        type=Path,
        default=_default_schema_path(),
        help="Path to schema.sql (default: src/radspion/sql/schema.sql)",
    )
    args = parser.parse_args(argv)

    try:
        validate_pack_sql(args.pack_sql, args.database, schema_path=args.schema)
    except PackValidationError as exc:
        print("Pack validation failed:", file=sys.stderr)
        for message in exc.messages:
            print(f"  - {message}", file=sys.stderr)
        return 1

    print(f"Pack validation passed: {args.pack_sql}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
