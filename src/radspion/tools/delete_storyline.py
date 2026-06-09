"""CLI entry point for deleting a storyline from the database."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from radspion.storyline_delete import (
    StorylineDeleteAborted,
    StorylineDeleteError,
    StorylineDeleteImpact,
    confirm_delete_group_name,
    delete_sql_path,
    delete_storyline_group,
    format_delete_report,
    generate_delete_sql,
    load_delete_impact,
    normalize_group_name,
)
from radspion.tools._db_helpers import DbToolError, assert_schema_present, resolve_database_path


@dataclass(frozen=True)
class DeleteStorylineResult:
    """Outcome of checking or deleting a storyline."""

    group_name: str
    impact: StorylineDeleteImpact
    output_path: Path | None = None
    database_path: Path | None = None
    applied: bool = False


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete a storyline (story arc) and all agent progress on its missions.",
    )
    parser.add_argument(
        "group",
        help="Storyline name exactly as stored in the database (groups.name)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report deletion impact only; do not write to the database",
    )
    parser.add_argument(
        "--write-sql",
        action="store_true",
        help="Write generated DELETE SQL to ./{storyline-name}-delete.sql in the current directory",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help=(
            "Delete without typing the storyline name to confirm. "
            "Hardcore — only use after reviewing --check output."
        ),
    )
    return parser.parse_args(argv)


def plan_delete(
    group_name: str,
    *,
    database_path_loader: Callable[[], Path] | None = None,
) -> tuple[StorylineDeleteImpact, Path]:
    """Load deletion impact for a storyline group."""
    normalized = normalize_group_name(group_name)
    db_path = (database_path_loader or resolve_database_path)()
    assert_schema_present(db_path)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        impact = load_delete_impact(conn, normalized)

    return impact, db_path


def delete_storyline(
    group_name: str,
    *,
    check_only: bool = False,
    write_sql: bool = False,
    auto_yes: bool = False,
    is_tty: bool | None = None,
    database_path_loader: Callable[[], Path] | None = None,
    sql_output_dir: Path | None = None,
) -> DeleteStorylineResult:
    """Report on or delete one storyline group from the database."""
    impact, db_path = plan_delete(
        group_name,
        database_path_loader=database_path_loader,
    )

    output_path: Path | None = None
    applied = False

    if write_sql:
        sql = generate_delete_sql(impact)
        output_path = delete_sql_path(impact.group_name, output_dir=sql_output_dir)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(sql, encoding="utf-8")

    if check_only or write_sql:
        return DeleteStorylineResult(
            group_name=impact.group_name,
            impact=impact,
            output_path=output_path,
            database_path=None,
            applied=False,
        )

    print(format_delete_report(impact))
    print("")

    tty = sys.stdin.isatty() if is_tty is None else is_tty
    if not confirm_delete_group_name(impact.group_name, auto_yes=auto_yes, is_tty=tty):
        raise StorylineDeleteAborted(
            "Deletion aborted. Type the exact storyline name to confirm, "
            "or re-run with -y/--yes only if you mean it.",
        )

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        delete_storyline_group(conn, impact)
        conn.commit()
        applied = True

    return DeleteStorylineResult(
        group_name=impact.group_name,
        impact=impact,
        database_path=db_path,
        applied=applied,
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        if args.check and args.write_sql:
            raise StorylineDeleteError("Use either --check or --write-sql, not both.")
        result = delete_storyline(
            args.group,
            check_only=args.check,
            write_sql=args.write_sql,
            auto_yes=args.yes,
        )
    except StorylineDeleteAborted as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except (StorylineDeleteError, DbToolError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if args.check or args.write_sql:
        print(format_delete_report(result.impact))

    if result.output_path is not None:
        print("")
        print(f"Wrote {result.output_path}")

    if result.applied:
        print("")
        print(f"Deleted storyline {result.group_name!r} from {result.database_path}")

    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
