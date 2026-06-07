"""Tests for storyline pack validation and SQL generation."""

from pathlib import Path

import pytest

from radspion.storyline_pack import (
    MissionSpec,
    StorylineError,
    StorylinePack,
    collect_image_errors,
    generate_sql,
    load_pack,
    load_storyline_yaml,
    parse_access,
    sql_literal,
    validate_clearance_code,
    validate_graph,
)
from tests.helpers import write_minimal_pack


def test_sql_literal_escapes_single_quotes():
    assert sql_literal("it's") == "'it''s'"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("open", ("open", None, ())),
        ({"clearance_code": "RADSPION-TEST"}, ("clearance_code", "RADSPION-TEST", ())),
        (
            {"requires_complete": ["alpha", "beta"]},
            ("requires_complete", None, ("alpha", "beta")),
        ),
    ],
)
def test_parse_access_valid(raw: object, expected: tuple[str, str | None, tuple[str, ...]]):
    assert parse_access(raw, "mission-a") == expected


@pytest.mark.parametrize(
    ("raw", "match"),
    [
        ("invalid", "access must be open"),
        ({"clearance_code": ""}, "clearance_code must be a non-empty string"),
        ({"clearance_code": "bad code"}, "must contain only letters"),
        ({"requires_complete": []}, "requires_complete must be a non-empty list"),
        ({"requires_complete": [""]}, "requires_complete entries must be non-empty strings"),
        ({"clearance_code": "X", "requires_complete": ["a"]}, "exactly one of"),
    ],
)
def test_parse_access_invalid(raw: object, match: str):
    with pytest.raises(StorylineError, match=match):
        parse_access(raw, "mission-a")


def test_validate_clearance_code_rejects_invalid_slug():
    with pytest.raises(StorylineError, match="must contain only letters"):
        validate_clearance_code("-BAD", "mission-a")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("![x](https://example.com/x.png)", []),
        ("![x](http://example.com/x.png)", ["must start with https://"]),
        ('<img src="https://example.com/x.png">', []),
        ('<img src="/local/x.png">', ["must start with https://"]),
    ],
)
def test_collect_image_errors(text: str, expected: list[str]):
    errors = collect_image_errors("alpha/brief.md", text)
    if not expected:
        assert errors == []
    else:
        assert any(expected[0] in error for error in errors)


def _mission(
    slug: str,
    *,
    access_rule: str = "open",
    clearance_code: str | None = None,
    requires_complete: tuple[str, ...] = (),
) -> MissionSpec:
    return MissionSpec(
        slug=slug,
        title=slug.title(),
        access_rule=access_rule,
        clearance_code=clearance_code,
        requires_complete=requires_complete,
        completion_data=f"{slug}-data",
        brief_markdown="brief",
        debrief_markdown="debrief",
    )


def test_validate_graph_rejects_self_requirement():
    missions = (_mission("alpha", requires_complete=("alpha",)),)
    with pytest.raises(StorylineError, match="cannot require itself"):
        validate_graph(missions)


def test_validate_graph_rejects_unknown_slug():
    missions = (_mission("alpha", requires_complete=("missing",)),)
    with pytest.raises(StorylineError, match="unknown slug"):
        validate_graph(missions)


def test_validate_graph_rejects_cycle():
    missions = (
        _mission("alpha", requires_complete=("beta",)),
        _mission("beta", requires_complete=("alpha",)),
    )
    with pytest.raises(StorylineError, match="Cycle detected"):
        validate_graph(missions)


def test_generate_sql_includes_clearance_and_requires_complete(tmp_path: Path):
    pack_root = tmp_path / "story-pack"
    write_minimal_pack(
        pack_root,
        storyline="""group: Story Pack
missions:
  - slug: alpha
    title: Alpha
    access:
      clearance_code: RADSPION-TEST
    completion_data: ALPHA
  - slug: beta
    title: Beta
    access:
      requires_complete:
        - alpha
    completion_data: BETA
""",
    )
    (pack_root / "beta").mkdir()
    (pack_root / "beta" / "brief.md").write_text("## Beta\n", encoding="utf-8")
    (pack_root / "beta" / "debrief.md").write_text("## Beta debrief\n", encoding="utf-8")

    pack = load_pack(pack_root)
    sql = generate_sql(pack)
    assert "INSERT INTO mission_clearance_codes" in sql
    assert "RADSPION-TEST" in sql
    assert "INSERT INTO mission_list_requires" in sql
    assert "parent.slug = 'alpha'" in sql


@pytest.mark.parametrize(
    ("setup", "match"),
    [
        (
            lambda root: root.mkdir(parents=True),
            "Missing",
        ),
        (
            lambda root: root.write_text("not a directory", encoding="utf-8"),
            "Not a directory",
        ),
        (
            lambda root: (
                root.mkdir(parents=True),
                (root / "storyline.yaml").write_text("not a mapping\n", encoding="utf-8"),
            ),
            "must be a YAML mapping",
        ),
        (
            lambda root: (
                root.mkdir(parents=True),
                (root / "storyline.yaml").write_text("group: G\nmissions: []\n", encoding="utf-8"),
            ),
            "missions must be a non-empty list",
        ),
        (
            lambda root: (
                root.mkdir(parents=True),
                (root / "storyline.yaml").write_text(
                    "group: G\nmissions:\n  - slug: alpha\n    title: T\n    completion_data: X\n",
                    encoding="utf-8",
                ),
            ),
            "missing access",
        ),
        (
            lambda root: (
                write_minimal_pack(root),
                (root / "storyline.yaml").write_text(
                    "group: G\n"
                    "missions:\n"
                    "  - slug: alpha\n    title: T\n    access: open\n    completion_data: X\n"
                    "  - slug: alpha\n    title: T2\n    access: open\n    completion_data: Y\n",
                    encoding="utf-8",
                ),
            ),
            "Duplicate mission slug",
        ),
        (
            lambda root: (
                write_minimal_pack(root),
                (root / "extra").mkdir(),
                (root / "extra" / "brief.md").write_text("## x\n", encoding="utf-8"),
                (root / "extra" / "debrief.md").write_text("## x\n", encoding="utf-8"),
            ),
            "not listed in storyline.yaml",
        ),
        (
            lambda root: (
                root.mkdir(parents=True),
                (root / "storyline.yaml").write_text(
                    "group: G\n"
                    "missions:\n"
                    "  - slug: alpha\n    title: T\n    access: open\n    completion_data: X\n",
                    encoding="utf-8",
                ),
            ),
            "Missing",
        ),
        (
            lambda root: (
                write_minimal_pack(root),
                (root / "alpha" / "brief.md").write_text(
                    "![x](http://bad.test/x.png)\n",
                    encoding="utf-8",
                ),
            ),
            "image URL must start with https://",
        ),
    ],
)
def test_load_pack_errors(tmp_path: Path, setup, match: str):
    pack_root = tmp_path / "pack"
    setup(pack_root)
    with pytest.raises(StorylineError, match=match):
        load_pack(pack_root)


def test_load_storyline_yaml_rejects_invalid_yaml(tmp_path: Path):
    pack_root = tmp_path / "pack"
    pack_root.mkdir()
    (pack_root / "storyline.yaml").write_text("group: [\n", encoding="utf-8")
    with pytest.raises(StorylineError, match="Invalid YAML"):
        load_storyline_yaml(pack_root)


def test_load_pack_rejects_empty_group(tmp_path: Path):
    pack_root = tmp_path / "pack"
    pack_root.mkdir()
    (pack_root / "storyline.yaml").write_text("group: '   '\nmissions: []\n", encoding="utf-8")
    with pytest.raises(StorylineError, match="group must be a non-empty string"):
        load_pack(pack_root)


def test_storyline_pack_name_property(tmp_path: Path):
    pack_root = tmp_path / "my-pack"
    write_minimal_pack(pack_root)
    pack = load_pack(pack_root)
    assert pack.name == "my-pack"
    assert isinstance(pack, StorylinePack)
