import json
from pathlib import Path

from rea_core.validation import SCHEMA_VERSION, validate_document, validate_file

ROOT = Path(__file__).resolve().parents[1]


def test_example_is_valid():
    issues = validate_file(ROOT / "examples" / "investigation.json")
    assert issues == []


def test_missing_required_field_is_rejected():
    document = json.loads((ROOT / "examples" / "investigation.json").read_text(encoding="utf-8"))
    del document["question"]
    issues = validate_document(document)
    assert issues
    assert any("question" in issue.message for issue in issues)


def test_unknown_top_level_field_is_rejected():
    document = json.loads((ROOT / "examples" / "investigation.json").read_text(encoding="utf-8"))
    document["unexpected"] = "silently unsupported fields should not pass"
    issues = validate_document(document)
    assert any("Additional properties" in issue.message for issue in issues)


def test_bad_hash_is_rejected():
    document = json.loads((ROOT / "examples" / "investigation.json").read_text(encoding="utf-8"))
    document["artifacts"][0]["sha256"] = "not-a-sha256"
    issues = validate_document(document)
    assert any("sha256" in issue.path for issue in issues)


def test_unsupported_schema_version_is_rejected():
    document = json.loads((ROOT / "examples" / "investigation.json").read_text(encoding="utf-8"))
    document["schema_version"] = "2.0.0"
    issues = validate_document(document)
    assert any("schema_version" in issue.path for issue in issues)


def test_version_is_declared():
    assert SCHEMA_VERSION == "1.0.0"


def test_invalid_json_returns_issue(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("{ invalid", encoding="utf-8")
    issues = validate_file(bad_file)
    assert len(issues) == 1
    assert "valid JSON" in issues[0].message
