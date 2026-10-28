"""Shared evidence contracts and validation utilities for REA."""

from .validation import SCHEMA_VERSION, ValidationIssue, validate_document

__all__ = ["SCHEMA_VERSION", "ValidationIssue", "validate_document"]
__version__ = "0.1.0"
