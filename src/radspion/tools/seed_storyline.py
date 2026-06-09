"""CLI entry point for storyline pack validation and database seeding."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from radspion.mission_files import MissionFilesError, load_missions_root
from radspion.sql_utils import execute_sql_script
from radspion.storyline_pack import StorylineError, StorylinePack, generate_sql, load_pack
from radspion.tools._db_helpers import DbToolError, assert_schema_present, resolve_database_path


@dataclass(frozen=True)
class SeedStorylineResult:
    """Outcome of validating or seeding one pack."""

    pack_root: Path
    group: str
    mission_count: int
    output_path: Path | None = None
    database_path: Path | None = None


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a storyline pack and seed the database.",
    )
    parser.add_argument(
        "pack",
        help="Storyline pack name (under RADSPION_MISSIONS_ROOT) or path to pack directory",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate only; do not write to the database",
    )
    parser.add_argument(
        "--write-sql",
        action="store_true",
        help="Write generated SQL beside the pack ({pack}/{pack}.sql)",
    )
    return parser.parse_args(argv)


def resolve_pack_root(
    pack_arg: str,
    *,
    missions_root_loader: Callable[[], Path] = load_missions_root,
) -> Path:
    """Resolve a pack name or path using RADSPION_MISSIONS_ROOT from .env when needed."""
    candidate = Path(pack_arg)
    if candidate.is_dir():
        return candidate.resolve()

    if candidate.is_absolute():
        raise StorylineError(f"Not a directory: {candidate}")

    try:
        missions_root = missions_root_loader()
    except MissionFilesError as exc:
        raise StorylineError(str(exc)) from exc

    pack_root = (missions_root / pack_arg).resolve()
    if not pack_root.is_dir():
        raise StorylineError(f"Pack directory not found: {pack_root}")
    return pack_root


def seed_storyline(
    pack_root: Path,
    *,
    check_only: bool = False,
    write_sql: bool = False,
    pack_loader: Callable[[Path], StorylinePack] = load_pack,
    sql_generator: Callable[[StorylinePack], str] = generate_sql,
    database_path_loader: Callable[[], Path] = resolve_database_path,
) -> SeedStorylineResult:
    """Validate a pack and optionally write SQL or load it into the database."""
    pack = pack_loader(pack_root)
    output_path: Path | None = None
    db_path: Path | None = None

    if write_sql:
        sql = sql_generator(pack)
        output_path = pack_root / f"{pack_root.name}.sql"
        output_path.write_text(sql, encoding="utf-8")
    elif not check_only:
        sql = sql_generator(pack)
        db_path = database_path_loader()
        assert_schema_present(db_path)
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            execute_sql_script(conn, sql)
            conn.commit()

    return SeedStorylineResult(
        pack_root=pack_root,
        group=pack.group,
        mission_count=len(pack.missions),
        output_path=output_path,
        database_path=db_path,
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        if args.check and args.write_sql:
            raise StorylineError("Use either --check or --write-sql, not both.")
        pack_root = resolve_pack_root(args.pack)
        result = seed_storyline(
            pack_root,
            check_only=args.check,
            write_sql=args.write_sql,
        )
    except (StorylineError, DbToolError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"OK: {result.mission_count} missions in group {result.group!r}")

    if result.output_path is not None:
        print(f"Wrote {result.output_path}")

    if result.database_path is not None:
        print(f"Loaded storyline pack {result.pack_root.name} into {result.database_path}")

    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
