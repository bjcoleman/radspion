"""Tests for make_radspion_clearance_logo CLI."""

from pathlib import Path

import pytest

from radspion.tools.make_radspion_clearance_logo import (
    main,
    make_clearance_logo_image,
)


def test_make_clearance_logo_image(tmp_path: Path):
    image = make_clearance_logo_image("RADSPION-QR-TRAINING")
    output = tmp_path / "logo.png"
    image.save(output)
    assert output.is_file()
    assert output.stat().st_size > 0


def test_make_clearance_logo_rejects_wide_text():
    with pytest.raises(ValueError, match="wider than the logo"):
        make_clearance_logo_image("X" * 80)


def test_main_rejects_empty_text(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    output = tmp_path / "out.png"
    with pytest.raises(SystemExit) as exc:
        main([str(output), "   "])
    assert exc.value.code == 1
    assert "must not be empty" in capsys.readouterr().err


def test_main_writes_png(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    output = tmp_path / "out.png"
    with pytest.raises(SystemExit) as exc:
        main([str(output), "RADSPION-QR-TRAINING"])
    assert exc.value.code == 0
    assert output.is_file()
    assert str(output) in capsys.readouterr().out
