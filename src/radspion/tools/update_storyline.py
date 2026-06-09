"""CLI entry point for syncing storyline pack content into an existing database."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from radspion.storyline_pack import StorylineError, StorylinePack, load_pack
from radspion.storyline_update import (
    DbPackState,
    PackUpdateDiff,
    StorylineUpdateAborted,
    StorylineUpdateError,
    apply_update_sql,
    confirm_sensitive_changes,
    diff_pack_against_db,
    format_diff_report,
    generate_update_sql,
    load_db_state,
    verify_pack_structure,
)
from radspion.tools._db_helpers import DbToolError, assert_schema_present, resolve_database_path
from radspion.tools.seed_storyline import resolve_pack_root


@dataclass(frozen=True)
class UpdateStorylineResult:
    """Outcome of validating or applying a storyline content update."""

    pack_root: Path
    group: str
    mission_count: int
    diff: PackUpdateDiff
    output_path: Path | None = None
    database_path: Path | None = None
    applied: bool = False


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a storyline pack and update content in an existing database.",
    )
    parser.add_argument(
        "pack",
        help="Storyline pack name (under RADSPION_MISSIONS_ROOT) or path to pack directory",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate and report differences only; do not write to the database",
    )
    parser.add_argument(
        "--write-sql",
        action="store_true",
        help="Write generated UPDATE SQL beside the pack ({pack}/{pack}-update.sql)",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Apply sensitive clearance/completion_data changes without prompting",
    )
    return parser.parse_args(argv)


def plan_update(
    pack_root: Path,
    *,
    pack_loader: Callable[[Path], StorylinePack] = load_pack,
    database_path_loader: Callable[[], Path] | None = None,
) -> tuple[StorylinePack, PackUpdateDiff, DbPackState, Path]:
    """Load pack and database state, verify structure, and compute the content diff."""
    pack = pack_loader(pack_root)
    db_path = (database_path_loader or resolve_database_path)()
    assert_schema_present(db_path)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        db_state = load_db_state(conn, pack.group)
        verify_pack_structure(pack, db_state)
        diff = diff_pack_against_db(pack, db_state)

    return pack, diff, db_state, db_path


def update_storyline(
    pack_root: Path,
    *,
    check_only: bool = False,
    write_sql: bool = False,
    auto_yes: bool = False,
    is_tty: bool | None = None,
    pack_loader: Callable[[Path], StorylinePack] = load_pack,
    database_path_loader: Callable[[], Path] | None = None,
) -> UpdateStorylineResult:
    """Validate a pack against the database and optionally write or apply content updates."""
    pack, diff, db_state, db_path = plan_update(
        pack_root,
        pack_loader=pack_loader,
        database_path_loader=database_path_loader,
    )

    output_path: Path | None = None
    applied = False

    if not diff.has_changes:
        return UpdateStorylineResult(
            pack_root=pack_root,
            group=pack.group,
            mission_count=len(pack.missions),
            diff=diff,
            database_path=db_path if not check_only and not write_sql else None,
            applied=False,
        )

    sql = generate_update_sql(pack, diff, db_state)

    if write_sql:
        output_path = pack_root / f"{pack_root.name}-update.sql"
        output_path.write_text(sql, encoding="utf-8")

    if check_only or write_sql:
        return UpdateStorylineResult(
            pack_root=pack_root,
            group=pack.group,
            mission_count=len(pack.missions),
            diff=diff,
            output_path=output_path,
            database_path=None,
            applied=False,
        )

    if diff.has_sensitive_changes:
        tty = sys.stdin.isatty() if is_tty is None else is_tty
        if not confirm_sensitive_changes(auto_yes=auto_yes, is_tty=tty):
            raise StorylineUpdateAborted(
                "Update aborted. Sensitive clearance/completion_data changes were not confirmed. "
                "Re-run with -y/--yes after review, or answer y at the prompt.",
            )

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        apply_update_sql(conn, sql)
        conn.commit()
        applied = True

    return UpdateStorylineResult(
        pack_root=pack_root,
        group=pack.group,
        mission_count=len(pack.missions),
        diff=diff,
        database_path=db_path,
        applied=applied,
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        if args.check and args.write_sql:
            raise StorylineUpdateError("Use either --check or --write-sql, not both.")
        pack_root = resolve_pack_root(args.pack)
        result = update_storyline(
            pack_root,
            check_only=args.check,
            write_sql=args.write_sql,
            auto_yes=args.yes,
        )
    except StorylineUpdateAborted as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except (StorylineError, StorylineUpdateError, DbToolError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(format_diff_report(result.diff))
    if result.diff.has_changes:
        print("")
    print(
        f"Pack {result.pack_root.name}: {result.mission_count} missions in group {result.group!r}",
    )

    if result.output_path is not None:
        print(f"Wrote {result.output_path}")

    if result.applied:
        print(f"Applied content updates to {result.database_path}")

    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
