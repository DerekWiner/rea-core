import json
from pathlib import Path

from rea_core.validation import SCHEMA_VERSION, validate_document, validate_file

ROOT = Path(__file__).resolve().parents[1]


def _example_document():
    return json.loads((ROOT / "examples" / "investigation.json").read_text(encoding="utf-8"))


def test_example_is_valid():
    assert validate_file(ROOT / "examples" / "investigation.json") == []


def test_missing_required_field_is_rejected():
    document = _example_document()
    del document["question"]
    issues = validate_document(document)
    assert issues
    assert any("question" in issue.message for issue in issues)


def test_unknown_top_level_field_is_rejected():
    document = _example_document()
    document["unexpected"] = "silently unsupported fields should not pass"
    issues = validate_document(document)
    assert any("Additional properties" in issue.message for issue in issues)


def test_bad_hash_is_rejected():
    document = _example_document()
    document["artifacts"][0]["sha256"] = "not-a-sha256"
    issues = validate_document(document)
    assert any("sha256" in issue.path for issue in issues)


def test_unsupported_schema_version_is_rejected():
    document = _example_document()
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


def test_duplicate_artifact_id_is_rejected():
    document = _example_document()
    duplicate = dict(document["artifacts"][0])
    document["artifacts"].append(duplicate)
    issues = validate_document(document)
    assert any(issue.path == "/artifacts/1/artifact_id" and "duplicate" in issue.message for issue in issues)


def test_unknown_artifact_reference_is_rejected():
    document = _example_document()
    document["evidence"][0]["artifact_ids"] = ["missing-artifact"]
    issues = validate_document(document)
    assert any(issue.path == "/evidence/0/artifact_ids/0" and "unknown" in issue.message for issue in issues)


def test_unknown_method_reference_is_rejected():
    document = _example_document()
    document["evidence"][0]["method_ids"] = ["missing-method"]
    issues = validate_document(document)
    assert any(issue.path == "/evidence/0/method_ids/0" and "unknown" in issue.message for issue in issues)


def test_unknown_evidence_reference_is_rejected():
    document = _example_document()
    document["findings"][0]["evidence_ids"] = ["missing-evidence"]
    issues = validate_document(document)
    assert any(issue.path == "/findings/0/evidence_ids/0" and "unknown" in issue.message for issue in issues)


def test_unknown_related_finding_reference_is_rejected():
    document = _example_document()
    document["findings"][0]["related_finding_ids"] = ["missing-finding"]
    issues = validate_document(document)
    assert any(issue.path == "/findings/0/related_finding_ids/0" and "unknown" in issue.message for issue in issues)
