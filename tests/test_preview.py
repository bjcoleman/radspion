"""Tests for the mission preview dev server."""

from pathlib import Path

import pytest

from radspion.mission_files import MissionFilesError, load_mission, load_missions_root
from radspion.preview_app import create_preview_app, preview_port
from radspion.tools.preview import (
    PreviewCliError,
    main,
    parse_preview_args,
    preview_usage,
    validate_preview_target,
)


@pytest.fixture
def missions_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Minimal storyline pack tree under a temporary missions root."""
    missions_root = tmp_path / "radspion-missions"
    missions_root.mkdir()

    pack = missions_root / "test-pack"
    mission_dir = pack / "alpha"
    mission_dir.mkdir(parents=True)

    (pack / "storyline.yaml").write_text(
        """\
group: Test Pack

missions:
  - slug: alpha
    title: Alpha Mission
    access: open
    completion_data: "DONE alpha"
""",
        encoding="utf-8",
    )
    (mission_dir / "brief.md").write_text("# Brief\n\nPreview **brief** text.\n", encoding="utf-8")
    (mission_dir / "debrief.md").write_text("# Debrief\n\nPreview debrief.\n", encoding="utf-8")

    monkeypatch.setattr("radspion.mission_files.load_tool_env", lambda: None)
    monkeypatch.setenv("RADSPION_MISSIONS_ROOT", str(missions_root))

    return missions_root


def test_parse_preview_args_accepts_storyline_and_mission():
    assert parse_preview_args(["test-pack", "alpha"]) == ("test-pack", "alpha")


def test_parse_preview_args_rejects_wrong_count():
    with pytest.raises(PreviewCliError, match=preview_usage()):
        parse_preview_args(["only-one"])


def test_validate_preview_target_loads_mission(missions_env: Path):
    mission = validate_preview_target("test-pack", "alpha")

    assert mission.slug == "alpha"
    assert mission.title == "Alpha Mission"


def test_validate_preview_target_raises_for_unknown_slug(missions_env: Path):
    with pytest.raises(MissionFilesError, match="not found"):
        validate_preview_target("test-pack", "missing")


def test_main_exits_on_usage_error(capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 1
    assert preview_usage() in capsys.readouterr().err


def test_main_exits_when_mission_missing(missions_env: Path, capsys: pytest.CaptureFixture[str]):
    with pytest.raises(SystemExit) as exc_info:
        main(["test-pack", "missing"])

    assert exc_info.value.code == 1
    assert "not found" in capsys.readouterr().err


def test_preview_port_is_8001():
    assert preview_port() == 8001


def test_create_preview_app_stores_target():
    app = create_preview_app(storyline="orientation", mission_slug="basic-training")

    assert app.config["PREVIEW_STORYLINE"] == "orientation"
    assert app.config["PREVIEW_MISSION_SLUG"] == "basic-training"


def test_load_mission_reads_pack_files(missions_env: Path):
    mission = load_mission("test-pack", "alpha")

    assert mission.slug == "alpha"
    assert mission.title == "Alpha Mission"
    assert mission.completion_data == "DONE alpha"
    assert "Preview **brief** text." in mission.brief_markdown


def test_load_mission_unknown_slug_raises(missions_env: Path):
    with pytest.raises(MissionFilesError, match="not found"):
        load_mission("test-pack", "missing")


def test_load_missions_root_resolves_relative_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    radspion_root = tmp_path / "radspion"
    missions_root = tmp_path / "missions"
    missions_root.mkdir()
    radspion_root.mkdir()

    monkeypatch.setattr("radspion.mission_files.project_root", lambda: radspion_root)
    monkeypatch.setattr("radspion.mission_files.load_tool_env", lambda: None)
    monkeypatch.setenv("RADSPION_MISSIONS_ROOT", "../missions")

    assert load_missions_root() == missions_root.resolve()


def test_load_missions_root_rejects_non_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    radspion_root = tmp_path / "radspion"
    radspion_root.mkdir()
    not_a_dir = radspion_root / "nope.txt"
    not_a_dir.write_text("x", encoding="utf-8")

    monkeypatch.setattr("radspion.mission_files.project_root", lambda: radspion_root)
    monkeypatch.setattr("radspion.mission_files.load_tool_env", lambda: None)
    monkeypatch.setenv("RADSPION_MISSIONS_ROOT", "nope.txt")

    with pytest.raises(MissionFilesError, match="not a directory"):
        load_missions_root()


def test_load_missions_root_requires_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("radspion.mission_files.load_tool_env", lambda: None)
    monkeypatch.delenv("RADSPION_MISSIONS_ROOT", raising=False)

    with pytest.raises(MissionFilesError, match="RADSPION_MISSIONS_ROOT"):
        load_missions_root()


def test_load_mission_requires_pack_directory(
    missions_env: Path,
):
    with pytest.raises(MissionFilesError, match="Not a directory"):
        load_mission("missing-pack", "alpha")


def test_load_mission_requires_brief_markdown(missions_env: Path):
    (missions_env / "test-pack" / "alpha" / "brief.md").unlink()

    with pytest.raises(MissionFilesError, match="Missing"):
        load_mission("test-pack", "alpha")


def test_load_mission_rejects_invalid_storyline_yaml(
    missions_env: Path,
):
    bad_pack = missions_env / "bad-pack"
    bad_pack.mkdir()
    (bad_pack / "storyline.yaml").write_text("not a mapping\n", encoding="utf-8")

    with pytest.raises(MissionFilesError, match="must be a YAML mapping"):
        load_mission("bad-pack", "alpha")


def test_load_mission_requires_storyline_yaml(missions_env: Path):
    empty_pack = missions_env / "empty-pack"
    empty_pack.mkdir()

    with pytest.raises(MissionFilesError, match="Missing"):
        load_mission("empty-pack", "alpha")


def test_load_mission_rejects_invalid_yaml_syntax(missions_env: Path):
    bad_pack = missions_env / "syntax-pack"
    bad_pack.mkdir()
    (bad_pack / "storyline.yaml").write_text("missions: [\n", encoding="utf-8")

    with pytest.raises(MissionFilesError, match="Invalid YAML"):
        load_mission("syntax-pack", "alpha")


def test_load_mission_requires_missions_list(missions_env: Path):
    bad_pack = missions_env / "list-pack"
    bad_pack.mkdir()
    (bad_pack / "storyline.yaml").write_text(
        "group: Test\nmissions: open\n",
        encoding="utf-8",
    )

    with pytest.raises(MissionFilesError, match="missions must be a list"):
        load_mission("list-pack", "alpha")


def test_preview_route_renders_active_brief(missions_env: Path):
    app = create_preview_app(storyline="test-pack", mission_slug="alpha")
    client = app.test_client()

    response = client.get("/")
    body = response.data.decode()

    assert response.status_code == 200
    assert "Alpha Mission" in body
    assert "Mission Brief" in body
    assert "Preview <strong>brief</strong> text." in body
    assert "Author preview" in body
    assert "status=completed" in body
    assert "recovered-data-form--multiline" in body
    assert "mission-detail-copy-data.js" in body
    assert "preview.css" in body
    assert 'class="mission-markdown markdown-body"' in body


def test_preview_route_renders_completed_debrief(missions_env: Path):
    app = create_preview_app(storyline="test-pack", mission_slug="alpha")
    client = app.test_client()

    response = client.get("/?status=completed")
    body = response.data.decode()

    assert response.status_code == 200
    assert "Mission Debrief" in body
    assert "Preview debrief." in body
    assert "DONE alpha" in body
    assert "recovered-data__value" in body
    assert "mission-detail-copy-data.js" in body
    assert "preview.css" in body


def test_preview_route_accepts_complete_status_alias(missions_env: Path):
    app = create_preview_app(storyline="test-pack", mission_slug="alpha")
    client = app.test_client()

    response = client.get("/?status=complete")

    assert response.status_code == 200
    assert "Mission Debrief" in response.data.decode()


def test_preview_route_rejects_invalid_status(missions_env: Path):
    app = create_preview_app(storyline="test-pack", mission_slug="alpha")
    client = app.test_client()

    response = client.get("/?status=bogus")
    body = response.data.decode()

    assert response.status_code == 400
    assert "Preview error" in body
    assert "status must be active or completed" in body


def test_preview_route_returns_404_for_missing_pack(missions_env: Path):
    app = create_preview_app(storyline="missing-pack", mission_slug="alpha")
    client = app.test_client()

    response = client.get("/")
    body = response.data.decode()

    assert response.status_code == 404
    assert "Preview error" in body
    assert "Not a directory" in body
