"""Compare a storyline pack against the database and plan content updates."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from radspion.storyline_pack import (
    MissionSpec,
    StorylineError,
    StorylinePack,
    sql_literal,
)

GENERATOR_UPDATE = "update_storyline"

SENSITIVE_PROMPT = (
    "This update changes clearance code(s) and/or completion data. "
    "These changes can impact agents. Be sure that the mission brief, QR codes, "
    "public display of clearance codes, and other external story elements are "
    "consistent. Do you want to continue? (y/N) "
)


@dataclass(frozen=True)
class DbMissionState:
    slug: str
    title: str
    brief_markdown: str
    debrief_markdown: str
    access_rule: str
    completion_data: str
    clearance_code: str | None
    requires_complete: frozenset[str]


@dataclass(frozen=True)
class DbPackState:
    group_id: int
    group_name: str
    missions: dict[str, DbMissionState]


@dataclass(frozen=True)
class MissionFieldDiff:
    slug: str
    title_changed: bool
    brief_changed: bool
    debrief_changed: bool
    clearance_code_changed: bool
    old_clearance_code: str | None
    new_clearance_code: str | None
    completion_data_changed: bool

    @property
    def has_changes(self) -> bool:
        return (
            self.title_changed
            or self.brief_changed
            or self.debrief_changed
            or self.clearance_code_changed
            or self.completion_data_changed
        )


@dataclass(frozen=True)
class PackUpdateDiff:
    group_name: str
    mission_count: int
    missions: tuple[MissionFieldDiff, ...]

    @property
    def has_changes(self) -> bool:
        return any(mission.has_changes for mission in self.missions)

    @property
    def has_sensitive_changes(self) -> bool:
        return any(
            mission.clearance_code_changed or mission.completion_data_changed
            for mission in self.missions
        )

    def changed_mission_slugs(self) -> list[str]:
        return [mission.slug for mission in self.missions if mission.has_changes]

    def sensitive_mission_slugs(self) -> list[str]:
        return [
            mission.slug
            for mission in self.missions
            if mission.clearance_code_changed or mission.completion_data_changed
        ]


class StorylineUpdateError(Exception):
    """Raised when a pack cannot be compared or applied to the database."""


class StorylineUpdateAborted(StorylineUpdateError):
    """Raised when the operator declines a sensitive update."""


def load_db_state(connection: sqlite3.Connection, group_name: str) -> DbPackState:
    """Load mission content and access structure for one story-arc group."""
    group_row = connection.execute(
        "SELECT id, name FROM groups WHERE name = ?",
        (group_name,),
    ).fetchone()
    if group_row is None:
        raise StorylineUpdateError(
            f"Group {group_name!r} is not in the database. "
            "Seed the pack first with seed_storyline.",
        )

    group_id = group_row["id"]
    mission_rows = connection.execute(
        """
        SELECT slug,
               title,
               brief_markdown,
               debrief_markdown,
               access_rule,
               completion_data
        FROM missions
        WHERE group_id = ?
        ORDER BY slug ASC
        """,
        (group_id,),
    ).fetchall()

    clearance_rows = connection.execute(
        """
        SELECT m.slug, mcc.clearance_code
        FROM mission_clearance_codes mcc
        JOIN missions m ON m.id = mcc.mission_id
        WHERE m.group_id = ?
        """,
        (group_id,),
    ).fetchall()
    clearance_by_slug = {row["slug"]: row["clearance_code"] for row in clearance_rows}

    requires_rows = connection.execute(
        """
        SELECT child.slug AS child_slug, parent.slug AS parent_slug
        FROM mission_list_requires mlr
        JOIN missions child ON child.id = mlr.mission_id
        JOIN missions parent ON parent.id = mlr.required_mission_id
        WHERE child.group_id = ?
        """,
        (group_id,),
    ).fetchall()
    requires_by_slug: dict[str, set[str]] = {}
    for row in requires_rows:
        requires_by_slug.setdefault(row["child_slug"], set()).add(row["parent_slug"])

    missions: dict[str, DbMissionState] = {}
    for row in mission_rows:
        slug = row["slug"]
        access_rule = row["access_rule"]
        clearance_code = clearance_by_slug.get(slug)
        if access_rule == "clearance_code" and clearance_code is None:
            raise StorylineUpdateError(
                f"Mission {slug!r}: database has access_rule clearance_code but no clearance row",
            )
        if access_rule != "clearance_code" and clearance_code is not None:
            raise StorylineUpdateError(
                f"Mission {slug!r}: database has a clearance row "
                "but access_rule is not clearance_code",
            )
        missions[slug] = DbMissionState(
            slug=slug,
            title=row["title"],
            brief_markdown=row["brief_markdown"],
            debrief_markdown=row["debrief_markdown"],
            access_rule=access_rule,
            completion_data=row["completion_data"],
            clearance_code=clearance_code,
            requires_complete=frozenset(requires_by_slug.get(slug, ())),
        )

    return DbPackState(group_id=group_id, group_name=group_row["name"], missions=missions)


def verify_pack_structure(pack: StorylinePack, db_state: DbPackState) -> None:
    """Ensure immutable pack fields match the database."""
    if pack.group != db_state.group_name:
        raise StorylineUpdateError(
            f"Group name mismatch: pack has {pack.group!r}, database has {db_state.group_name!r}. "
            "Group names cannot be changed with update_storyline.",
        )

    pack_slugs = {mission.slug for mission in pack.missions}
    db_slugs = set(db_state.missions)
    missing = sorted(pack_slugs - db_slugs)
    extra = sorted(db_slugs - pack_slugs)
    if missing or extra:
        parts: list[str] = []
        if missing:
            parts.append(f"pack missions missing from database: {', '.join(missing)}")
        if extra:
            parts.append(f"database missions missing from pack: {', '.join(extra)}")
        raise StorylineUpdateError(
            "Mission set mismatch. update_storyline cannot add or remove missions. "
            + "; ".join(parts),
        )

    for mission in pack.missions:
        db_mission = db_state.missions[mission.slug]
        if mission.access_rule != db_mission.access_rule:
            raise StorylineUpdateError(
                f"Mission {mission.slug!r}: access_rule mismatch "
                f"(pack {mission.access_rule!r}, database {db_mission.access_rule!r}). "
                "Access structure cannot be changed with update_storyline.",
            )

        pack_requires = frozenset(mission.requires_complete)
        if pack_requires != db_mission.requires_complete:
            pack_list = ", ".join(sorted(pack_requires)) or "(none)"
            db_list = ", ".join(sorted(db_mission.requires_complete)) or "(none)"
            raise StorylineUpdateError(
                f"Mission {mission.slug!r}: requires_complete mismatch "
                f"(pack: {pack_list}; database: {db_list}). "
                "Access structure cannot be changed with update_storyline.",
            )

        if mission.access_rule == "clearance_code":
            if mission.clearance_code is None:
                raise StorylineError(f"Mission {mission.slug!r}: missing clearance_code in pack")
        elif mission.clearance_code is not None:
            raise StorylineError(f"Mission {mission.slug!r}: unexpected clearance_code in pack")


def diff_pack_against_db(pack: StorylinePack, db_state: DbPackState) -> PackUpdateDiff:
    """Compare mutable fields between a validated pack and database state."""
    mission_diffs: list[MissionFieldDiff] = []
    for mission in pack.missions:
        db_mission = db_state.missions[mission.slug]
        clearance_changed = False
        if mission.access_rule == "clearance_code":
            clearance_changed = mission.clearance_code != db_mission.clearance_code
        mission_diffs.append(
            MissionFieldDiff(
                slug=mission.slug,
                title_changed=mission.title != db_mission.title,
                brief_changed=mission.brief_markdown != db_mission.brief_markdown,
                debrief_changed=mission.debrief_markdown != db_mission.debrief_markdown,
                clearance_code_changed=clearance_changed,
                old_clearance_code=db_mission.clearance_code,
                new_clearance_code=mission.clearance_code,
                completion_data_changed=mission.completion_data != db_mission.completion_data,
            ),
        )

    return PackUpdateDiff(
        group_name=pack.group,
        mission_count=len(pack.missions),
        missions=tuple(mission_diffs),
    )


def _mission_spec_by_slug(pack: StorylinePack) -> dict[str, MissionSpec]:
    return {mission.slug: mission for mission in pack.missions}


def generate_update_sql(pack: StorylinePack, diff: PackUpdateDiff, db_state: DbPackState) -> str:
    """Generate UPDATE statements for the changed mutable fields."""
    specs = _mission_spec_by_slug(pack)
    statements: list[str] = []

    for mission_diff in diff.missions:
        if not mission_diff.has_changes:
            continue
        spec = specs[mission_diff.slug]
        mission_updates: list[str] = []
        if mission_diff.title_changed:
            mission_updates.append(f"title = {sql_literal(spec.title)}")
        if mission_diff.brief_changed:
            mission_updates.append(f"brief_markdown = {sql_literal(spec.brief_markdown)}")
        if mission_diff.debrief_changed:
            mission_updates.append(f"debrief_markdown = {sql_literal(spec.debrief_markdown)}")
        if mission_diff.completion_data_changed:
            mission_updates.append(f"completion_data = {sql_literal(spec.completion_data)}")
        if mission_updates:
            statements.append(
                "UPDATE missions\n"
                f"SET {', '.join(mission_updates)}\n"
                f"WHERE slug = {sql_literal(spec.slug)}\n"
                f"  AND group_id = {db_state.group_id};",
            )
        if mission_diff.clearance_code_changed:
            statements.append(
                "UPDATE mission_clearance_codes\n"
                f"SET clearance_code = {sql_literal(spec.clearance_code)}\n"
                "WHERE mission_id = (\n"
                "    SELECT id FROM missions\n"
                f"    WHERE slug = {sql_literal(spec.slug)}\n"
                f"      AND group_id = {db_state.group_id}\n"
                ");",
            )

    if not statements:
        return ""

    body = "\n\n".join(statements)
    return f"""-- Generated by {GENERATOR_UPDATE} — do not edit by hand.
-- Storyline pack: {pack.name}

PRAGMA foreign_keys = ON;

BEGIN;

{body}

COMMIT;
"""


def apply_update_sql(connection: sqlite3.Connection, sql: str) -> None:
    """Apply generated update SQL inside the caller's transaction expectations."""
    if not sql.strip():
        return
    connection.executescript(sql)


def _format_mission_diff(mission_diff: MissionFieldDiff) -> list[str]:
    if not mission_diff.has_changes:
        return [f"{mission_diff.slug}: unchanged"]

    lines = [f"{mission_diff.slug}:"]
    if mission_diff.title_changed:
        lines.append("  title: changed")
    if mission_diff.brief_changed:
        lines.append("  brief: changed")
    if mission_diff.debrief_changed:
        lines.append("  debrief: changed")
    if mission_diff.clearance_code_changed:
        lines.append(
            "  clearance_code: "
            f"{mission_diff.old_clearance_code!r} → {mission_diff.new_clearance_code!r}",
        )
    if mission_diff.completion_data_changed:
        lines.append("  completion_data: changed")
    return lines


def format_diff_report(diff: PackUpdateDiff) -> str:
    """Return a human-readable report of pending content changes."""
    lines = [
        f"OK: pack matches group {diff.group_name!r} ({diff.mission_count} missions)",
        "",
    ]

    change_counts = {
        "title": 0,
        "brief": 0,
        "debrief": 0,
        "clearance_code": 0,
        "completion_data": 0,
    }

    for mission_diff in diff.missions:
        lines.extend(_format_mission_diff(mission_diff))
        if mission_diff.title_changed:
            change_counts["title"] += 1
        if mission_diff.brief_changed:
            change_counts["brief"] += 1
        if mission_diff.debrief_changed:
            change_counts["debrief"] += 1
        if mission_diff.clearance_code_changed:
            change_counts["clearance_code"] += 1
        if mission_diff.completion_data_changed:
            change_counts["completion_data"] += 1
        lines.append("")

    if not diff.has_changes:
        lines.append("Summary: no content changes")
        return "\n".join(lines)

    summary_parts = [f"{count} {name}" for name, count in change_counts.items() if count]
    lines.append(f"Summary: {', '.join(summary_parts)} would change")
    if diff.has_sensitive_changes:
        lines.append(
            "Sensitive changes: "
            + ", ".join(
                name
                for name, count in (
                    ("clearance_code", change_counts["clearance_code"]),
                    ("completion_data", change_counts["completion_data"]),
                )
                if count
            ),
        )
    return "\n".join(lines)


def confirm_sensitive_changes(
    *,
    auto_yes: bool,
    is_tty: bool,
    prompt: str = SENSITIVE_PROMPT,
) -> bool:
    """Return True when sensitive updates should proceed."""
    if auto_yes:
        return True
    if not is_tty:
        return False
    answer = input(prompt).strip().lower()
    return answer == "y"
