"""SQLite connection and storage for Radspion."""

import sqlite3
from pathlib import Path

from radspion.missions import (
    DashboardGroup,
    DashboardMission,
    ListedMissionContent,
    MissionListResult,
    MissionSummary,
)
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

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(
            id=row["id"],
            email=row["email"],
            google_subject_id=row["google_subject_id"],
            display_name=row["display_name"],
            codename=row["codename"],
            is_operator=bool(row["is_operator"]),
        )

    def find_user_by_google_subject_id(self, google_subject_id: str) -> User | None:
        try:
            row = self._conn.execute(
                "SELECT id, email, google_subject_id, display_name, codename, is_operator "
                "FROM users WHERE google_subject_id = ?",
                (google_subject_id,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading user: {exc}") from exc
        return self._row_to_user(row) if row else None

    def find_user_by_email(self, email: str) -> User | None:
        try:
            row = self._conn.execute(
                "SELECT id, email, google_subject_id, display_name, codename, is_operator "
                "FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading user: {exc}") from exc
        return self._row_to_user(row) if row else None

    def find_user_by_id(self, user_id: int) -> User | None:
        try:
            row = self._conn.execute(
                "SELECT id, email, google_subject_id, display_name, codename, is_operator "
                "FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading user: {exc}") from exc
        return self._row_to_user(row) if row else None

    def find_user_by_codename(self, codename: str) -> User | None:
        try:
            row = self._conn.execute(
                "SELECT id, email, google_subject_id, display_name, codename, is_operator "
                "FROM users WHERE codename = ?",
                (codename,),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading user: {exc}") from exc
        return self._row_to_user(row) if row else None

    def _create_codename(self) -> str:
        counter_row = self._conn.execute(
            "UPDATE codename_counter SET next_value = next_value + 1 RETURNING next_value"
        ).fetchone()
        if counter_row is None:
            raise DatabaseError("Database error creating user: codename counter missing")
        return f"AGENT{counter_row['next_value']:04d}"

    def create_user(
        self,
        *,
        email: str,
        google_subject_id: str,
        display_name: str,
        is_operator: bool = False,
    ) -> User:
        try:
            self._conn.execute("BEGIN")
            codename = self._create_codename()
            row = self._conn.execute(
                "INSERT INTO users (email, google_subject_id, display_name, codename, is_operator) "
                "VALUES (?, ?, ?, ?, ?) "
                "RETURNING id, email, google_subject_id, display_name, codename, is_operator",
                (email, google_subject_id, display_name, codename, 1 if is_operator else 0),
            ).fetchone()
            self._conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error creating user: {exc}") from exc
        return self._row_to_user(row)

    def sync_mission_status(self, user_id: int) -> None:
        """
        Keep agent_mission_status aligned with listable missions (UC-012).

        - open: ensure an active row exists (never downgrade completed).
        - requires_complete: active row when all list prerequisites are completed.
        - clearance_code: no row until clearance is granted (handled elsewhere).
        """
        try:
            self._conn.execute(
                """
                INSERT INTO agent_mission_status (user_id, mission_id, status)
                SELECT ?, m.id, 'active'
                FROM missions m
                WHERE m.access_rule = 'open'
                  AND NOT EXISTS (
                    SELECT 1 FROM agent_mission_status ams
                    WHERE ams.user_id = ? AND ams.mission_id = m.id
                  )
                """,
                (user_id, user_id),
            )
            self._conn.execute(
                """
                INSERT INTO agent_mission_status (user_id, mission_id, status)
                SELECT ?, m.id, 'active'
                FROM missions m
                WHERE m.access_rule = 'requires_complete'
                  AND NOT EXISTS (
                    SELECT 1 FROM agent_mission_status ams
                    WHERE ams.user_id = ? AND ams.mission_id = m.id
                  )
                  AND (
                    SELECT COUNT(*) FROM mission_list_requires mlr
                    WHERE mlr.mission_id = m.id
                  ) = (
                    SELECT COUNT(*) FROM mission_list_requires mlr
                    JOIN agent_mission_status ams
                      ON ams.mission_id = mlr.required_mission_id
                     AND ams.user_id = ?
                     AND ams.status = 'completed'
                    WHERE mlr.mission_id = m.id
                  )
                """,
                (user_id, user_id, user_id),
            )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error syncing mission status: {exc}") from exc

    def get_agent_dashboard(self, user_id: int) -> list[DashboardGroup]:
        """Mission list grouped by story arc, groups ordered by descending group id."""
        try:
            rows = self._conn.execute(
                """
                SELECT g.id AS group_id,
                       g.name AS group_name,
                       m.slug,
                       m.title,
                       ams.status
                FROM agent_mission_status ams
                JOIN missions m ON m.id = ams.mission_id
                JOIN groups g ON g.id = m.group_id
                WHERE ams.user_id = ?
                ORDER BY g.id DESC,
                         CASE ams.status WHEN 'active' THEN 0 ELSE 1 END,
                         m.slug ASC
                """,
                (user_id,),
            ).fetchall()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading agent dashboard: {exc}") from exc

        groups: list[DashboardGroup] = []
        by_id: dict[int, DashboardGroup] = {}
        for row in rows:
            group_id = row["group_id"]
            if group_id not in by_id:
                group = DashboardGroup(id=group_id, name=row["group_name"])
                by_id[group_id] = group
                groups.append(group)
            by_id[group_id].missions.append(
                DashboardMission(
                    slug=row["slug"],
                    title=row["title"],
                    status=row["status"],
                )
            )
        return groups

    def agent_has_listed_mission(self, user_id: int, slug: str) -> bool:
        """True when the agent has an active or completed row for this mission slug."""
        try:
            row = self._conn.execute(
                """
                SELECT 1
                FROM agent_mission_status ams
                JOIN missions m ON m.id = ams.mission_id
                WHERE ams.user_id = ? AND m.slug = ?
                """,
                (user_id, slug),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error checking mission list: {exc}") from exc
        return row is not None

    def find_listed_mission(self, user_id: int, slug: str) -> DashboardMission | None:
        """Load one listed mission for detail stub pages."""
        try:
            row = self._conn.execute(
                """
                SELECT m.slug, m.title, ams.status
                FROM agent_mission_status ams
                JOIN missions m ON m.id = ams.mission_id
                WHERE ams.user_id = ? AND m.slug = ?
                """,
                (user_id, slug),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading mission: {exc}") from exc
        if row is None:
            return None
        return DashboardMission(slug=row["slug"], title=row["title"], status=row["status"])

    def get_listed_mission_content(self, user_id: int, slug: str) -> ListedMissionContent | None:
        """Load mission brief/debrief for a listed mission (UC-016)."""
        try:
            row = self._conn.execute(
                """
                SELECT m.slug,
                       m.title,
                       ams.status,
                       m.brief_markdown,
                       m.debrief_markdown,
                       m.completion_data
                FROM agent_mission_status ams
                JOIN missions m ON m.id = ams.mission_id
                WHERE ams.user_id = ? AND m.slug = ?
                """,
                (user_id, slug),
            ).fetchone()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error loading mission detail: {exc}") from exc
        if row is None:
            return None
        recovered = row["completion_data"] if row["status"] == "completed" else None
        return ListedMissionContent(
            slug=row["slug"],
            title=row["title"],
            status=row["status"],
            brief_markdown=row["brief_markdown"],
            debrief_markdown=row["debrief_markdown"],
            completion_data=recovered,
        )

    def grant_clearance(self, user_id: int, clearance_code: str) -> MissionListResult:
        """
        Grant clearance for matching missions (UC-014, UC-019).

        ``clearance_code`` must be trimmed and non-empty. Comparison is case-sensitive.
        """
        try:
            known = self._conn.execute(
                "SELECT 1 FROM mission_clearance_codes WHERE clearance_code = ? LIMIT 1",
                (clearance_code,),
            ).fetchone()
            if known is None:
                return MissionListResult(outcome="invalid")

            rows = self._conn.execute(
                """
                SELECT m.id AS mission_id,
                       m.slug,
                       m.title,
                       g.name AS group_name
                FROM mission_clearance_codes mcc
                JOIN missions m ON m.id = mcc.mission_id
                JOIN groups g ON g.id = m.group_id
                WHERE mcc.clearance_code = ?
                  AND m.access_rule = 'clearance_code'
                  AND NOT EXISTS (
                    SELECT 1 FROM agent_mission_status ams
                    WHERE ams.user_id = ? AND ams.mission_id = m.id
                  )
                ORDER BY m.slug ASC
                """,
                (clearance_code, user_id),
            ).fetchall()

            if not rows:
                return MissionListResult(
                    outcome="already_done",
                    message="You have already been granted this clearance.",
                )

            new_missions: list[MissionSummary] = []
            for row in rows:
                self._conn.execute(
                    """
                    INSERT INTO agent_mission_status (user_id, mission_id, status)
                    VALUES (?, ?, 'active')
                    """,
                    (user_id, row["mission_id"]),
                )
                new_missions.append(
                    MissionSummary(
                        title=row["title"],
                        slug=row["slug"],
                        group_name=row["group_name"],
                    )
                )
            self._conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error granting clearance: {exc}") from exc

        return MissionListResult(
            outcome="success",
            new_missions=tuple(new_missions),
        )

    def _listed_mission_summaries(self, user_id: int) -> dict[str, MissionSummary]:
        """Map slug → summary for every mission on the agent's dashboard."""
        rows = self._conn.execute(
            """
            SELECT m.slug, m.title, g.name AS group_name
            FROM agent_mission_status ams
            JOIN missions m ON m.id = ams.mission_id
            JOIN groups g ON g.id = m.group_id
            WHERE ams.user_id = ?
            ORDER BY m.slug ASC
            """,
            (user_id,),
        ).fetchall()
        return {
            row["slug"]: MissionSummary(
                title=row["title"],
                slug=row["slug"],
                group_name=row["group_name"],
            )
            for row in rows
        }

    def submit_mission_data(
        self,
        user_id: int,
        slug: str,
        completion_data: str,
    ) -> MissionListResult | None:
        """
        Submit recovered mission data (UC-021).

        ``completion_data`` must be trimmed and non-empty. Comparison is case-sensitive.
        Returns None when the mission is not on the agent's list.
        """
        try:
            row = self._conn.execute(
                """
                SELECT ams.status, m.id AS mission_id, m.completion_data
                FROM agent_mission_status ams
                JOIN missions m ON m.id = ams.mission_id
                WHERE ams.user_id = ? AND m.slug = ?
                """,
                (user_id, slug),
            ).fetchone()
            if row is None:
                return None

            if row["status"] == "completed":
                return MissionListResult(
                    outcome="already_done",
                    message="This mission is already marked complete.",
                )

            if row["completion_data"] != completion_data:
                return MissionListResult(outcome="invalid")

            listed_before = self._listed_mission_summaries(user_id)
            self._conn.execute(
                """
                UPDATE agent_mission_status
                SET status = 'completed'
                WHERE user_id = ? AND mission_id = ?
                """,
                (user_id, row["mission_id"]),
            )
            self.sync_mission_status(user_id)
            listed_after = self._listed_mission_summaries(user_id)
            new_slugs = sorted(set(listed_after) - set(listed_before))
            new_missions = tuple(listed_after[s] for s in new_slugs)
            self._conn.commit()
        except sqlite3.Error as exc:
            raise DatabaseError(f"Database error submitting mission data: {exc}") from exc

        return MissionListResult(outcome="success", new_missions=new_missions)
