"""Load mission markdown from the radspion-missions filesystem."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from os import getenv
from pathlib import Path

from dotenv import load_dotenv


class MissionsFilesystemError(Exception):
    """Raised when mission pack files cannot be loaded."""


@dataclass(frozen=True)
class FilesystemMission:
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
        raise MissionsFilesystemError(
            "RADSPION_MISSIONS_ROOT is not set. Add it to .env "
            "(path to the radspion-missions repo)."
        )

    missions_root = Path(raw.strip())
    if not missions_root.is_absolute():
        missions_root = (root / missions_root).resolve()
    else:
        missions_root = missions_root.resolve()

    if not missions_root.is_dir():
        raise MissionsFilesystemError(f"RADSPION_MISSIONS_ROOT is not a directory: {missions_root}")

    return missions_root


def _import_storyline_pack(missions_root: Path):
    scripts_dir = missions_root / "scripts"
    if not scripts_dir.is_dir():
        raise MissionsFilesystemError(f"Missing missions scripts directory: {scripts_dir}")

    scripts_path = str(scripts_dir)
    if scripts_path not in sys.path:
        sys.path.insert(0, scripts_path)

    try:
        from storyline_pack import StorylineError, load_pack
    except ImportError as exc:  # pragma: no cover
        raise MissionsFilesystemError(
            "Could not import storyline_pack from radspion-missions. "
            "Ensure PyYAML is installed in this venv."
        ) from exc

    return StorylineError, load_pack


def load_mission(storyline: str, mission_slug: str) -> FilesystemMission:
    """Load one mission from a storyline pack by directory name and slug."""
    missions_root = load_missions_root()
    storyline_error, load_pack = _import_storyline_pack(missions_root)

    pack_root = missions_root / storyline
    try:
        pack = load_pack(pack_root)
    except storyline_error as exc:
        raise MissionsFilesystemError(str(exc)) from exc

    for mission in pack.missions:
        if mission.slug == mission_slug:
            return FilesystemMission(
                slug=mission.slug,
                title=mission.title,
                completion_data=mission.completion_data,
                brief_markdown=mission.brief_markdown,
                debrief_markdown=mission.debrief_markdown,
            )

    raise MissionsFilesystemError(
        f"Mission {mission_slug!r} not found in storyline pack {storyline!r}."
    )
