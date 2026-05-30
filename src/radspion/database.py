"""SQLite connection and storage for Radspion."""

import sqlite3
from pathlib import Path

from radspion.user import User


class DatabaseError(Exception):
    """Raised when the SQLite database cannot be opened or used."""


class DatabaseRadspionStorage:
    """Persist and load data using a SQLite database file."""

    def __init__(self, database_path: Path) -> None:
        try:
            self._conn = sqlite3.connect(database_path, check_same_thread=False)
        except sqlite3.Error as exc:
            raise DatabaseError(f"Could not open database at {database_path}: {exc}") from exc
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def registration_code_exists(self, code: str) -> bool:
        """Return True when the code exists in registration_access_codes."""
        try:
            row = self._conn.execute(
                "SELECT 1 FROM registration_access_codes WHERE code = ?",
                (code,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error checking registration code: {exc}") from exc
        return row is not None

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            email=row["email"],
            google_subject_id=row["google_subject_id"],
            display_name=row["display_name"],
            is_operator=bool(row["is_operator"]),
        )

    def find_user_by_google_subject_id(self, google_subject_id: str) -> User | None:
        try:
            row = self._conn.execute(
                "SELECT id, email, google_subject_id, display_name, is_operator "
                "FROM users WHERE google_subject_id = ?",
                (google_subject_id,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading user: {exc}") from exc
        return self._row_to_user(row) if row else None

    def find_user_by_email(self, email: str) -> User | None:
        try:
            row = self._conn.execute(
                "SELECT id, email, google_subject_id, display_name, is_operator "
                "FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading user: {exc}") from exc
        return self._row_to_user(row) if row else None

    def find_user_by_id(self, user_id: int) -> User | None:
        try:
            row = self._conn.execute(
                "SELECT id, email, google_subject_id, display_name, is_operator "
                "FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading user: {exc}") from exc
        return self._row_to_user(row) if row else None

    def create_user(
        self,
        *,
        email: str,
        google_subject_id: str,
        display_name: str,
        is_operator: bool = False,
    ) -> User:
        try:
            row = self._conn.execute(
                "INSERT INTO users (email, google_subject_id, display_name, is_operator) "
                "VALUES (?, ?, ?, ?) "
                "RETURNING id, email, google_subject_id, display_name, is_operator",
                (email, google_subject_id, display_name, 1 if is_operator else 0),
            ).fetchone()
            self._conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error creating user: {exc}") from exc
        return self._row_to_user(row)

    def get_orientation_group_id(self) -> int | None:
        try:
            row = self._conn.execute(
                "SELECT id FROM groups WHERE name = ?",
                ("Orientation",),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading Orientation group: {exc}") from exc
        return row["id"] if row else None

    def add_group_member(self, user_id: int, group_id: int) -> None:
        try:
            self._conn.execute(
                "INSERT OR IGNORE INTO group_members (user_id, group_id) VALUES (?, ?)",
                (user_id, group_id),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error adding group member: {exc}") from exc
