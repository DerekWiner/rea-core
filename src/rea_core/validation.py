"""Structural and cross-reference validation for REA investigation records.

Validation is deliberately offline and does not execute or fetch referenced artifacts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_VERSION = "1.0.0"


@dataclass(frozen=True)
class ValidationIssue:
    """One validation problem, with a JSON Pointer-like location."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path or '/'}: {self.message}"


def load_schema() -> dict[str, Any]:
    """Load the bundled investigation schema without network access."""
    schema_path = files("rea_core").joinpath("schemas/investigation.schema.json")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _pointer(*parts: object) -> str:
    """Build a JSON Pointer-like path from path segments."""
    return "/" + "/".join(
        str(part).replace("~", "~0").replace("/", "~1") for part in parts
    )


def _unique_id_issues(document: dict[str, Any]) -> list[ValidationIssue]:
    """Report repeated identifiers within each record collection."""
    issues: list[ValidationIssue] = []
    collections = (
        ("artifacts", "artifact_id"),
        ("methods", "method_id"),
        ("evidence", "evidence_id"),
        ("findings", "finding_id"),
    )

    for collection_name, id_key in collections:
        seen: set[str] = set()
        for index, item in enumerate(document.get(collection_name, [])):
            identifier = item.get(id_key)
            if identifier in seen:
                issues.append(
                    ValidationIssue(
                        path=_pointer(collection_name, index, id_key),
                        message=f"duplicate {id_key} {identifier!r}",
                    )
                )
            else:
                seen.add(identifier)
    return issues


def _reference_issues(document: dict[str, Any]) -> list[ValidationIssue]:
    """Report references to identifiers that are absent from the record."""
    issues: list[ValidationIssue] = []
    artifact_ids = {item["artifact_id"] for item in document.get("artifacts", [])}
    method_ids = {item["method_id"] for item in document.get("methods", [])}
    evidence_ids = {item["evidence_id"] for item in document.get("evidence", [])}
    finding_ids = {item["finding_id"] for item in document.get("findings", [])}

    for index, evidence in enumerate(document.get("evidence", [])):
        for field, known_ids in (
            ("artifact_ids", artifact_ids),
            ("method_ids", method_ids),
        ):
            for ref_index, identifier in enumerate(evidence.get(field, [])):
                if identifier not in known_ids:
                    issues.append(
                        ValidationIssue(
                            path=_pointer("evidence", index, field, ref_index),
                            message=f"references unknown identifier {identifier!r}",
                        )
                    )

    for index, finding in enumerate(document.get("findings", [])):
        for ref_index, identifier in enumerate(finding.get("evidence_ids", [])):
            if identifier not in evidence_ids:
                issues.append(
                    ValidationIssue(
                        path=_pointer("findings", index, "evidence_ids", ref_index),
                        message=f"references unknown evidence_id {identifier!r}",
                    )
                )
        for ref_index, identifier in enumerate(finding.get("related_finding_ids", [])):
            if identifier not in finding_ids:
                issues.append(
                    ValidationIssue(
                        path=_pointer("findings", index, "related_finding_ids", ref_index),
                        message=f"references unknown finding_id {identifier!r}",
                    )
                )
    return issues


def validate_document(document: Any) -> list[ValidationIssue]:
    """Return structural and cross-reference issues; empty means valid by these checks."""
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    issues: list[ValidationIssue] = []
    for error in sorted(
        validator.iter_errors(document),
        key=lambda item: list(map(str, item.absolute_path)),
    ):
        issues.append(
            ValidationIssue(
                path=_pointer(*error.absolute_path) if error.absolute_path else "/",
                message=error.message,
            )
        )

    # Semantic checks rely on schema-guaranteed fields and types, so only run
    # them after structural validation succeeds.
    if issues or not isinstance(document, dict):
        return issues
    issues.extend(_unique_id_issues(document))
    issues.extend(_reference_issues(document))
    return issues


def validate_file(path: str | Path) -> list[ValidationIssue]:
    """Load a JSON file and validate it, reporting parse errors as a validation issue."""
    file_path = Path(path)
    try:
        document = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [ValidationIssue(path="/", message=f"could not read valid JSON: {exc}")]
    return validate_document(document)
