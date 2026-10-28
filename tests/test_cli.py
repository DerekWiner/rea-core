from pathlib import Path

from rea_core.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_validate_command_returns_success(capsys):
    result = main(["validate", str(ROOT / "examples" / "investigation.json")])
    assert result == 0
    assert "VALID:" in capsys.readouterr().out


def test_schema_version_command(capsys):
    result = main(["schema-version"])
    assert result == 0
    assert capsys.readouterr().out.strip() == "1.0.0"
