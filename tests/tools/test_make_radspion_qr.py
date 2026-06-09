"""Tests for make_radspion_qr CLI."""

from pathlib import Path

import pytest

from radspion.tools.make_radspion_qr import main, make_qr_image


def test_make_qr_image_writes(tmp_path: Path):
    img = make_qr_image("https://www.radspion.com/clearance/TEST-CODE")
    output = tmp_path / "qr.png"
    img.save(output)
    assert output.is_file()
    assert output.stat().st_size > 0


def test_main_rejects_non_png(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    output = tmp_path / "qr.txt"
    with pytest.raises(SystemExit) as exc:
        main([str(output), "payload"])
    assert exc.value.code == 1
    assert "must be a .png" in capsys.readouterr().err


def test_main_writes_png(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    output = tmp_path / "qr.png"
    with pytest.raises(SystemExit) as exc:
        main([str(output), "payload"])
    assert exc.value.code == 0
    assert output.is_file()
    assert str(output) in capsys.readouterr().out
