"""Load, validate, and generate SQL for a storyline mission pack."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from radspion.markdown_collapsible import validate_collapsible_markdown

STORYLINE_FILE = "storyline.yaml"
BRIEF_FILE = "brief.md"
DEBRIEF_FILE = "debrief.md"
GENERATOR = "generate_storyline"

IMG_MARKDOWN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
IMG_HTML = re.compile(r"""<img[^>]+src=["']([^"']+)["']""", re.IGNORECASE)
CLEARANCE_CODE_PATTERN = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*$")


@dataclass(frozen=True)
class MissionSpec:
    slug: str
    title: str
    access_rule: str
    clearance_code: str | None
    requires_complete: tuple[str, ...]
    completion_data: str
    brief_markdown: str
    debrief_markdown: str


@dataclass(frozen=True)
class StorylinePack:
    root: Path
    group: str
    missions: tuple[MissionSpec, ...]

    @property
    def name(self) -> str:
        return self.root.name


class StorylineError(Exception):
    """Raised when a pack fails validation."""


def load_storyline_yaml(pack_root: Path) -> object:
    path = pack_root / STORYLINE_FILE
    if not path.is_file():
        raise StorylineError(f"Missing {path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise StorylineError(f"Invalid YAML in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise StorylineError(f"{path} must be a YAML mapping")
    return data


def read_markdown(pack_root: Path, slug: str, filename: str) -> str:
    path = pack_root / slug / filename
    if not path.is_file():
        raise StorylineError(f"Missing {path}")
    return path.read_text(encoding="utf-8")


def validate_clearance_code(code: str, slug: str) -> None:
    if not CLEARANCE_CODE_PATTERN.fullmatch(code):
        raise StorylineError(
            f"Mission {slug!r}: clearance_code {code!r} must contain only "
            "letters, digits, and hyphens (e.g. LAST-TRANSMISSION)",
        )


def parse_access(raw: object, slug: str) -> tuple[str, str | None, tuple[str, ...]]:
    if raw == "open":
        return "open", None, ()

    if not isinstance(raw, dict):
        raise StorylineError(
            f"Mission {slug!r}: access must be open or a mapping with "
            "clearance_code / requires_complete",
        )

    keys = set(raw.keys())
    if keys == {"clearance_code"}:
        code = raw["clearance_code"]
        if not isinstance(code, str) or not code.strip():
            raise StorylineError(
                f"Mission {slug!r}: clearance_code must be a non-empty string",
            )
        stripped = code.strip()
        validate_clearance_code(stripped, slug)
        return "clearance_code", stripped, ()

    if keys == {"requires_complete"}:
        reqs = raw["requires_complete"]
        if not isinstance(reqs, list) or not reqs:
            raise StorylineError(
                f"Mission {slug!r}: requires_complete must be a non-empty list",
            )
        parsed: list[str] = []
        for item in reqs:
            if not isinstance(item, str) or not item.strip():
                raise StorylineError(
                    f"Mission {slug!r}: requires_complete entries must be non-empty strings",
                )
            parsed.append(item.strip())
        return "requires_complete", None, tuple(parsed)

    raise StorylineError(
        f"Mission {slug!r}: access must be exactly one of open, clearance_code, "
        "or requires_complete",
    )


def discover_mission_dirs(pack_root: Path) -> set[str]:
    found: set[str] = set()
    for child in pack_root.iterdir():
        if not child.is_dir():
            continue
        if (child / BRIEF_FILE).is_file() and (child / DEBRIEF_FILE).is_file():
            found.add(child.name)
    return found


def collect_image_errors(relative_path: str, text: str) -> list[str]:
    errors: list[str] = []
    for pattern in (IMG_MARKDOWN, IMG_HTML):
        for match in pattern.finditer(text):
            url = match.group(1).strip()
            if not url.startswith("https://"):
                errors.append(
                    f"{relative_path}: image URL must start with https:// (got {url!r})",
                )
    return errors


def detect_cycle(
    slug: str,
    graph: dict[str, list[str]],
    visiting: set[str],
    visited: set[str],
) -> None:
    if slug in visiting:
        raise StorylineError(f"Cycle detected in requires_complete graph at mission {slug!r}")
    if slug in visited:
        return
    visiting.add(slug)
    for required in graph.get(slug, []):
        detect_cycle(required, graph, visiting, visited)
    visiting.remove(slug)
    visited.add(slug)


def validate_graph(missions: tuple[MissionSpec, ...]) -> None:
    slugs = {mission.slug for mission in missions}
    graph = {mission.slug: list(mission.requires_complete) for mission in missions}

    for mission in missions:
        for required in mission.requires_complete:
            if required == mission.slug:
                raise StorylineError(
                    f"Mission {mission.slug!r} cannot require itself in requires_complete",
                )
            if required not in slugs:
                raise StorylineError(
                    f"Mission {mission.slug!r}: requires_complete references "
                    f"unknown slug {required!r}",
                )

    visiting: set[str] = set()
    visited: set[str] = set()
    for slug in slugs:
        detect_cycle(slug, graph, visiting, visited)


def load_pack(pack_root: Path) -> StorylinePack:
    pack_root = pack_root.resolve()
    if not pack_root.is_dir():
        raise StorylineError(f"Not a directory: {pack_root}")

    data = load_storyline_yaml(pack_root)
    group = data.get("group")
    if not isinstance(group, str) or not group.strip():
        raise StorylineError(f"{STORYLINE_FILE}: group must be a non-empty string")

    raw_missions = data.get("missions")
    if not isinstance(raw_missions, list) or not raw_missions:
        raise StorylineError(f"{STORYLINE_FILE}: missions must be a non-empty list")

    missions: list[MissionSpec] = []
    seen_slugs: set[str] = set()

    for index, raw in enumerate(raw_missions):
        if not isinstance(raw, dict):
            raise StorylineError(f"missions[{index}] must be a mapping")

        slug = raw.get("slug")
        if not isinstance(slug, str) or not slug.strip():
            raise StorylineError(f"missions[{index}]: slug must be a non-empty string")
        slug = slug.strip()
        if slug in seen_slugs:
            raise StorylineError(f"Duplicate mission slug {slug!r}")
        seen_slugs.add(slug)

        title = raw.get("title")
        if not isinstance(title, str) or not title.strip():
            raise StorylineError(f"Mission {slug!r}: title must be a non-empty string")

        completion_data = raw.get("completion_data")
        if not isinstance(completion_data, str) or not completion_data.strip():
            raise StorylineError(f"Mission {slug!r}: completion_data must be a non-empty string")

        if "access" not in raw:
            raise StorylineError(f"Mission {slug!r}: missing access")
        access_rule, clearance_code, requires_complete = parse_access(raw["access"], slug)

        brief = read_markdown(pack_root, slug, BRIEF_FILE)
        debrief = read_markdown(pack_root, slug, DEBRIEF_FILE)

        missions.append(
            MissionSpec(
                slug=slug,
                title=title.strip(),
                access_rule=access_rule,
                clearance_code=clearance_code,
                requires_complete=requires_complete,
                completion_data=completion_data.strip(),
                brief_markdown=brief,
                debrief_markdown=debrief,
            ),
        )

    pack = StorylinePack(root=pack_root, group=group.strip(), missions=tuple(missions))

    discovered = discover_mission_dirs(pack_root)
    configured = {mission.slug for mission in pack.missions}
    missing_dirs = configured - discovered
    extra_dirs = discovered - configured
    if missing_dirs:
        raise StorylineError(
            f"Missions missing brief/debrief folders: {', '.join(sorted(missing_dirs))}",
        )
    if extra_dirs:
        raise StorylineError(
            f"Folders with brief/debrief not listed in {STORYLINE_FILE}: "
            f"{', '.join(sorted(extra_dirs))}",
        )

    validate_graph(pack.missions)

    prose_errors: list[str] = []
    for mission in pack.missions:
        for filename, text in (
            (f"{mission.slug}/{BRIEF_FILE}", mission.brief_markdown),
            (f"{mission.slug}/{DEBRIEF_FILE}", mission.debrief_markdown),
        ):
            prose_errors.extend(collect_image_errors(filename, text))
            prose_errors.extend(validate_collapsible_markdown(text, path=filename))
    if prose_errors:
        raise StorylineError("\n".join(prose_errors))

    return pack


def sql_literal(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def generate_sql(pack: StorylinePack) -> str:
    group_expr = f"(SELECT id FROM groups WHERE name = {sql_literal(pack.group)})"
    mission_rows: list[str] = []
    for mission in pack.missions:
        mission_rows.append(
            "("
            f"{sql_literal(mission.slug)}, "
            f"{sql_literal(mission.title)}, "
            f"{sql_literal(mission.brief_markdown)}, "
            f"{sql_literal(mission.debrief_markdown)}, "
            f"{group_expr}, "
            f"{sql_literal(mission.access_rule)}, "
            f"{sql_literal(mission.completion_data)}"
            ")",
        )

    statements = [
        f"INSERT INTO groups (name) VALUES ({sql_literal(pack.group)});",
        "",
        "INSERT INTO missions (slug, title, brief_markdown, debrief_markdown, "
        "group_id, access_rule, completion_data) VALUES",
        "    " + ",\n    ".join(mission_rows) + ";",
    ]

    clearance_rows: list[str] = []
    for mission in pack.missions:
        if mission.access_rule == "clearance_code":
            clearance_rows.append(
                "SELECT id, "
                f"{sql_literal(mission.clearance_code)} "
                f"FROM missions WHERE slug = {sql_literal(mission.slug)}",
            )
    if clearance_rows:
        statements.extend(
            ["", "INSERT INTO mission_clearance_codes (mission_id, clearance_code)"],
        )
        statements.append("\nUNION ALL\n".join(clearance_rows) + ";")

    list_rows: list[str] = []
    for mission in pack.missions:
        for required in mission.requires_complete:
            list_rows.append(
                "SELECT child.id, parent.id\n"
                "FROM missions child\n"
                f"JOIN missions parent ON parent.slug = {sql_literal(required)}\n"
                f"WHERE child.slug = {sql_literal(mission.slug)}",
            )
    if list_rows:
        statements.extend(
            ["", "INSERT INTO mission_list_requires (mission_id, required_mission_id)"],
        )
        statements.append("\nUNION ALL\n".join(list_rows) + ";")

    body = "\n".join(statements)
    return f"""-- Generated by {GENERATOR} — do not edit by hand.
-- Storyline pack: {pack.name}

PRAGMA foreign_keys = ON;

BEGIN;

{body}

COMMIT;
"""
