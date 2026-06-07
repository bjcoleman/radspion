"""CLI entry point for storyline pack validation and SQL generation."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from radspion.mission_files import MissionFilesError, load_missions_root
from radspion.storyline_pack import StorylineError, StorylinePack, generate_sql, load_pack


@dataclass(frozen=True)
class StorylineRunResult:
    """Outcome of validating or generating SQL for one pack."""

    pack_root: Path
    group: str
    mission_count: int
    output_path: Path | None = None


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify a storyline pack and generate seed SQL with inlined mission markdown.",
    )
    parser.add_argument(
        "pack",
        help="Storyline pack name (under RADSPION_MISSIONS_ROOT) or path to pack directory",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate only; do not write SQL",
    )
    return parser.parse_args(argv)


def resolve_pack_root(
    pack_arg: str,
    *,
    missions_root_loader: Callable[[], Path] = load_missions_root,
) -> Path:
    """Resolve a pack name or path using RADSPION_MISSIONS_ROOT from .env when needed."""
    candidate = Path(pack_arg)
    if candidate.is_dir():
        return candidate.resolve()

    if candidate.is_absolute():
        raise StorylineError(f"Not a directory: {candidate}")

    try:
        missions_root = missions_root_loader()
    except MissionFilesError as exc:
        raise StorylineError(str(exc)) from exc

    pack_root = (missions_root / pack_arg).resolve()
    if not pack_root.is_dir():
        raise StorylineError(f"Pack directory not found: {pack_root}")
    return pack_root


def run_storyline(
    pack_root: Path,
    *,
    check_only: bool = False,
    pack_loader: Callable[[Path], StorylinePack] = load_pack,
    sql_generator: Callable[[StorylinePack], str] = generate_sql,
) -> StorylineRunResult:
    """Validate a pack and optionally write generated SQL beside the pack."""
    pack = pack_loader(pack_root)
    output_path: Path | None = None
    if not check_only:
        output_path = pack_root / f"{pack_root.name}.sql"
        output_path.write_text(sql_generator(pack), encoding="utf-8")
    return StorylineRunResult(
        pack_root=pack_root,
        group=pack.group,
        mission_count=len(pack.missions),
        output_path=output_path,
    )


def main(argv: list[str] | None = None) -> None:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        pack_root = resolve_pack_root(args.pack)
        result = run_storyline(pack_root, check_only=args.check)
    except StorylineError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    print(f"OK: {result.mission_count} missions in group {result.group!r}")

    if result.output_path is not None:
        print(f"Wrote {result.output_path}")

    raise SystemExit(0)


if __name__ == "__main__":  # pragma: no cover
    main()
