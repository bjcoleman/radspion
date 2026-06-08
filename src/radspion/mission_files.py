"""Load mission markdown from the radspion-missions filesystem."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from pathlib import Path

import yaml
from dotenv import load_dotenv

STORYLINE_FILE = "storyline.yaml"
BRIEF_FILE = "brief.md"
DEBRIEF_FILE = "debrief.md"


class MissionFilesError(Exception):
    """Raised when mission pack files cannot be loaded."""


@dataclass(frozen=True)
class LoadedMission:
    """Mission prose and metadata read from a storyline pack on disk."""

    slug: str
    title: str
    completion_data: str
    brief_markdown: str
    debrief_markdown: str


def _radspion_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_missions_root() -> Path:
    """Resolve RADSPION_MISSIONS_ROOT from radspion .env."""
    root = _radspion_root()
    load_dotenv(root / ".env")

    raw = getenv("RADSPION_MISSIONS_ROOT")
    if not raw or not raw.strip():
        raise MissionFilesError(
            "RADSPION_MISSIONS_ROOT is not set. Add it to .env "
            "(path to the radspion-missions repo)."
        )

    missions_root = Path(raw.strip())
    if not missions_root.is_absolute():
        missions_root = (root / missions_root).resolve()
    else:
        missions_root = missions_root.resolve()

    if not missions_root.is_dir():
        raise MissionFilesError(f"RADSPION_MISSIONS_ROOT is not a directory: {missions_root}")

    return missions_root


def _read_markdown(path: Path) -> str:
    if not path.is_file():
        raise MissionFilesError(f"Missing {path}")
    return path.read_text(encoding="utf-8")


def _load_storyline_yaml(pack_root: Path) -> dict:
    path = pack_root / STORYLINE_FILE
    if not path.is_file():
        raise MissionFilesError(f"Missing {path}")

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise MissionFilesError(f"Invalid YAML in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise MissionFilesError(f"{path} must be a YAML mapping")

    return data


def _find_mission_entry(data: dict, pack_root: Path, mission_slug: str) -> dict:
    raw_missions = data.get("missions")
    if not isinstance(raw_missions, list):
        raise MissionFilesError(f"{pack_root / STORYLINE_FILE}: missions must be a list")

    for raw in raw_missions:
        if not isinstance(raw, dict):
            continue
        slug = raw.get("slug")
        if isinstance(slug, str) and slug.strip() == mission_slug:
            return raw

    raise MissionFilesError(
        f"Mission {mission_slug!r} not found in storyline pack {pack_root.name!r}."
    )


def _mission_fields(raw: dict, pack_root: Path, mission_slug: str) -> tuple[str, str]:
    title = raw.get("title")
    if not isinstance(title, str) or not title.strip():
        raise MissionFilesError(
            f"Mission {mission_slug!r} in {pack_root / STORYLINE_FILE}: "
            "title must be a non-empty string"
        )

    completion_data = raw.get("completion_data")
    if not isinstance(completion_data, str) or not completion_data.strip():
        raise MissionFilesError(
            f"Mission {mission_slug!r} in {pack_root / STORYLINE_FILE}: "
            "completion_data must be a non-empty string"
        )

    return title.strip(), completion_data.strip()


def load_mission(storyline: str, mission_slug: str) -> LoadedMission:
    """Load one mission from a storyline pack by directory name and slug."""
    missions_root = load_missions_root()
    pack_root = missions_root / storyline

    if not pack_root.is_dir():
        raise MissionFilesError(f"Not a directory: {pack_root}")

    data = _load_storyline_yaml(pack_root)
    raw = _find_mission_entry(data, pack_root, mission_slug)
    title, completion_data = _mission_fields(raw, pack_root, mission_slug)

    mission_dir = pack_root / mission_slug
    brief_markdown = _read_markdown(mission_dir / BRIEF_FILE)
    debrief_markdown = _read_markdown(mission_dir / DEBRIEF_FILE)

    return LoadedMission(
        slug=mission_slug,
        title=title,
        completion_data=completion_data,
        brief_markdown=brief_markdown,
        debrief_markdown=debrief_markdown,
    )
