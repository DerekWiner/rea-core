# REA Core

**Shared evidence contracts and validation tools for the REA ecosystem.**

REA Core provides a small, domain-neutral format for describing investigations, artifacts, evidence and findings. Specialist REAs should be able to exchange structured records without inventing a new data format for every integration.

This repository starts with a versioned JSON Schema and a small command-line validator. It is a contract and validation library, not an agent framework or reverse-engineering engine.

## What is included

- `src/rea_core/schemas/investigation.schema.json` — version 1 investigation record schema.
- `src/rea_core/cli.py` — validate a JSON investigation record.
- `src/rea_core/validation.py` — reusable validation function.
- `examples/investigation.json` — synthetic, valid example.
- `tests/` — contract and CLI tests.

## Quick start

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[test]"
rea-core validate examples/investigation.json
```

On Windows PowerShell, activate the environment with `.venv\\Scripts\\Activate.ps1`.

Exit code `0` means the document conforms to the schema. A validation failure prints actionable errors and exits non-zero.

## Contract principles

- **Versioned records.** Every record declares a schema identifier and version.
- **Evidence types stay distinct.** Observations, reported claims, interpretations, hypotheses and independent verification are not interchangeable.
- **Provenance is explicit.** Record artifact hashes and tool information when available, without treating metadata as proof of truth.
- **Portable references.** Artifact locations can be local paths or external URIs, but consumers must not fetch or execute them automatically.
- **Domain extensions.** Specialist projects may add namespaced metadata without weakening the shared fields.
- **Safe by default.** Validation parses JSON only. It does not execute artifacts, access the network or upload data.

## Record shape

An investigation includes an ID, schema version, question, creation time, status, artifact records, evidence records and findings. Evidence points back to the artifact and method that produced it. Findings cite evidence IDs and state their confidence and validation status.

See [the schema](src/rea_core/schemas/investigation.schema.json), [the example](examples/investigation.json) and [the contract guide](docs/contract.md).

## Compatibility

Version 1 is intentionally small. Schema changes that break existing valid records require a new schema version or an explicit migration. Consumers should preserve unknown extension metadata when practical and reject unsupported major versions rather than silently misreading them.

## Current limitations

The validator checks schema conformance, unique record IDs and internal references between evidence, artifacts, methods and findings. These checks are still structural. They do not verify whether an experiment actually ran, whether a source is trustworthy, whether a hash matches an artifact on disk, or whether a conclusion is scientifically correct. Those require separate verification workflows.

## License

MIT. See [LICENSE](LICENSE). Third-party artifacts and tools retain their own licenses and restrictions.
