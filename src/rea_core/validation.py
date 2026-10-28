"""Structural validation for REA investigation records.

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
    """One schema validation problem, with a JSON Pointer-like location."""

    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path or '/'}: {self.message}"


def load_schema() -> dict[str, Any]:
    """Load the bundled investigation schema without network access."""
    schema_path = files("rea_core").joinpath("schemas/investigation.schema.json")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_document(document: Any) -> list[ValidationIssue]:
    """Return structural validation issues. An empty list means the document is valid."""
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    issues = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(map(str, item.absolute_path))):
        path = "/" + "/".join(str(part).replace("~", "~0").replace("/", "~1") for part in error.absolute_path)
        issues.append(ValidationIssue(path=path, message=error.message))
    return issues


def validate_file(path: str | Path) -> list[ValidationIssue]:
    """Load a JSON file and validate it, reporting parse errors as a validation issue."""
    file_path = Path(path)
    try:
        document = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [ValidationIssue(path="/", message=f"could not read valid JSON: {exc}")]
    return validate_document(document)
