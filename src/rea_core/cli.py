"""Command-line interface for REA Core."""

from __future__ import annotations

import argparse
import sys

from .validation import SCHEMA_VERSION, validate_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rea-core", description="Validate REA investigation records.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate", help="validate a JSON investigation record")
    validate_parser.add_argument("path", help="path to the JSON record")
    validate_parser.add_argument("--quiet", action="store_true", help="only set the exit status")
    subparsers.add_parser("schema-version", help="print the supported investigation schema version")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "schema-version":
        print(SCHEMA_VERSION)
        return 0
    issues = validate_file(args.path)
    if issues:
        print(f"INVALID: {args.path} ({len(issues)} issue(s))", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1
    if not args.quiet:
        print(f"VALID: {args.path} conforms to REA investigation schema {SCHEMA_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
