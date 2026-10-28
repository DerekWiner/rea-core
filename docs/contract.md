# REA Core contract guide

## Investigation records

The version 1 schema is the portable envelope for one bounded research effort. It records the question, artifacts, methods, evidence, findings and limitations. Domain-specific details belong under `extensions` or in artifact/method metadata.

## Evidence taxonomy

| Type | Meaning |
| --- | --- |
| `observation` | Directly observed output or behavior, with the method and context recorded where possible |
| `reported_claim` | A statement made by a person, tool, paper or upstream system that has not been independently established here |
| `interpretation` | An explanation inferred from one or more observations or claims |
| `hypothesis` | A proposed explanation or prediction that still needs a discriminating test |
| `independent_verification` | A result checked through a separate method, source or replication. The record should explain what made the check independent |

Do not upgrade a reported claim to an observation merely because it appears in machine-readable output. An independent verification record should document the method and its relationship to the original result.

## Findings

A finding links to one or more evidence IDs and includes a confidence estimate and status. Confidence is a recorded judgment, not a calibrated probability unless a project defines and validates such calibration. A `supported` finding is not automatically proven true.

## Artifacts and hashes

Artifact URIs are descriptive references. Consumers must not automatically fetch or execute them. SHA-256 records content identity when computed over the exact bytes, but a hash does not establish origin, integrity before hashing, authorship or truth. If a hash is recorded, the method of obtaining the bytes should be documented when relevant.

## Methods and execution

Record tool names and versions, relevant parameters and execution mode where known. State whether network access occurred. Use `unknown` or omit a field rather than guessing. REA Core itself does not execute methods or manage sandboxes.

## Schema evolution

Version 1 requires `schema` and `schema_version`. Patch releases should not change validation semantics. Backward-compatible additions require care because version 1 records reject unknown top-level and nested fields in core objects. Use `extensions` or metadata for domain-specific data; a breaking contract change requires a new schema version and migration guidance.

## Validation boundaries

Schema validation establishes only that a document has the expected shape and field constraints. It does not establish referential integrity between IDs, resolve URIs, verify artifact hashes, reproduce an experiment or certify a scientific conclusion. Those should be implemented as separate checks with explicit names and results.
