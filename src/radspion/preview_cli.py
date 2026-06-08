"""CLI entry point for the mission preview dev server."""

from __future__ import annotations

import sys

from radspion.mission_files import LoadedMission, MissionFilesError, load_mission
from radspion.preview_app import create_preview_app, preview_port


class PreviewCliError(Exception):
    """Invalid preview CLI usage."""


def preview_usage() -> str:
    return "Usage: preview_mission <storyline> <mission>"


def parse_preview_args(argv: list[str]) -> tuple[str, str]:
    """Return storyline and mission slug from CLI arguments."""
    if len(argv) != 2:
        raise PreviewCliError(preview_usage())
    return argv[0], argv[1]


def validate_preview_target(storyline: str, mission_slug: str) -> LoadedMission:
    """Ensure the pack and mission exist on disk."""
    return load_mission(storyline, mission_slug)


def start_preview_server(storyline: str, mission_slug: str) -> None:
    """Run the preview Flask dev server (blocks until interrupted)."""
    app = create_preview_app(storyline=storyline, mission_slug=mission_slug)
    app.run(host="127.0.0.1", port=preview_port(), debug=True)  # pragma: no cover


def main(argv: list[str] | None = None) -> None:
    """Start the preview server for one storyline mission."""
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        storyline, mission_slug = parse_preview_args(args)
        validate_preview_target(storyline, mission_slug)
    except PreviewCliError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from exc
    except MissionFilesError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    start_preview_server(storyline, mission_slug)


if __name__ == "__main__":  # pragma: no cover
    main()
