"""Validate storyline pack SQL before loading into an existing database."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class PackValidationError(Exception):
    """Raised when pack SQL would introduce overlapping agency codes."""

    def __init__(self, messages: list[str]) -> None:
        self.messages = messages
        super().__init__("\n".join(messages))


def _format_codes(codes: set[str]) -> str:
    return ", ".join(repr(code) for code in sorted(codes))


def _load_codes(conn: sqlite3.Connection) -> tuple[set[str], set[str], set[str]]:
    unlock = {
        row[0] for row in conn.execute("SELECT unlock_code FROM mission_unlock_codes").fetchall()
    }
    completion = {row[0] for row in conn.execute("SELECT completion_code FROM missions").fetchall()}
    duplicate_completion = {
        row[0]
        for row in conn.execute(
            """
            SELECT completion_code
            FROM missions
            GROUP BY completion_code
            HAVING COUNT(*) > 1
            """
        ).fetchall()
    }
    return unlock, completion, duplicate_completion


def _load_pack_codes(pack_sql_path: Path, schema_path: Path) -> tuple[set[str], set[str], set[str]]:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        conn.executescript(pack_sql_path.read_text(encoding="utf-8"))
        return _load_codes(conn)
    except sqlite3.Error as exc:
        raise PackValidationError([f"Pack SQL failed in validation sandbox: {exc}"]) from exc
    finally:
        conn.close()


def _load_existing_codes(db_path: Path) -> tuple[set[str], set[str]]:
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        return _load_codes(conn)[:2]
    except sqlite3.Error as exc:
        raise PackValidationError([f"Could not read codes from database: {exc}"]) from exc
    finally:
        conn.close()


def validate_pack_sql(
    pack_sql_path: Path,
    db_path: Path,
    *,
    schema_path: Path,
) -> None:
    """
    Ensure pack SQL does not introduce overlapping listing/completion codes.

    Checks:
    - no string appears as both unlock and completion within the pack
    - no duplicate completion_code within the pack
    - no pack code already exists in the target database (unlock or completion)
    """
    pack_sql_path = pack_sql_path.resolve()
    db_path = db_path.resolve()
    schema_path = schema_path.resolve()

    if not pack_sql_path.is_file():
        raise PackValidationError([f"Pack SQL not found: {pack_sql_path}"])
    if not db_path.is_file():
        raise PackValidationError([f"Database not found: {db_path}"])
    if not schema_path.is_file():
        raise PackValidationError([f"Schema SQL not found: {schema_path}"])

    pack_unlock, pack_completion, duplicate_completion = _load_pack_codes(
        pack_sql_path,
        schema_path,
    )
    existing_unlock, existing_completion = _load_existing_codes(db_path)
    existing_all = existing_unlock | existing_completion
    pack_all = pack_unlock | pack_completion

    errors: list[str] = []

    internal_overlap = pack_unlock & pack_completion
    if internal_overlap:
        errors.append(
            "Pack lists the same string as both listing and completion data: "
            f"{_format_codes(internal_overlap)}"
        )

    if duplicate_completion:
        errors.append(
            f"Pack defines duplicate completion data strings: {_format_codes(duplicate_completion)}"
        )

    db_overlap = pack_all & existing_all
    if db_overlap:
        details: list[str] = []
        for code in sorted(db_overlap):
            locations: list[str] = []
            if code in existing_unlock:
                locations.append("existing mission_unlock_codes")
            if code in existing_completion:
                locations.append("existing missions.completion_code")
            if code in pack_unlock:
                locations.append("pack listing")
            if code in pack_completion:
                locations.append("pack completion")
            details.append(f"{code!r} ({', '.join(locations)})")
        errors.append("Pack codes conflict with the database: " + "; ".join(details))

    if errors:
        raise PackValidationError(errors)
