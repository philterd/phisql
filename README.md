# PhiSQL Specification

PhiSQL is the declarative query language for PII privacy operations across the Philterd toolkit.

This repository contains the language specification. The reference parser and AST library live in [`philterd/phisql`](https://github.com/philterd/phisql).

## Status

> [!IMPORTANT]
> **PhiSQL v0.1 is a DRAFT.** The grammar and semantics are subject to change before v1.0. Implementations may track the draft but must not claim conformance until v1.0 is published.

The current draft covers the **redaction subset**: `REDACT`, `DEIDENTIFY`, and supporting clauses that compile to the Phileas JSON policy schema. Discovery, monitoring, benchmarking, and cross-tool join verbs are scoped for later drafts.

## Versions

| Version | Status | Scope | Document |
|---|---|---|---|
| v0.1 | Draft | Redaction subset | [`spec/v0.1/SPEC.md`](spec/v0.1/SPEC.md) |

## Relationship to the Phileas policy schema

The [Phileas JSON policy schema](https://github.com/philterd/phileas/blob/main/policy-schema/redaction-policy-schema.json) is the **canonical execution contract** for redaction. PhiSQL is a **convenience authoring layer** that compiles to it.

```
PhiSQL source  →  Compiler  →  Phileas JSON policy  →  Phileas runtime
```

The compiler is deterministic and lossless. Anything PhiSQL can express must be representable as Phileas JSON. The runtime does not change. The policy library at [`philterd/pii-redaction-policies`](https://github.com/philterd/pii-redaction-policies) remains the source of truth for distributable policies.

See [Relationship to Phileas](spec/v0.1/SPEC.md#relationship-to-the-phileas-policy-schema) in the spec for the full governance posture.

## Trademark

"PhiSQL" is a registered trademark of Philterd, LLC. The specification is freely readable and implementable, but the **name** is reserved for implementations that pass the conformance test suite (forthcoming at [`philterd/phisql-conformance`](https://github.com/philterd/phisql-conformance)). See the trademark policy on [philterd.ai](https://www.philterd.ai) once published.

## License

The specification is licensed under the [Apache License, Version 2.0](LICENSE).

## Validating examples

Every JSON example under `spec/<version>/examples/` is validated against the canonical Phileas policy schema on every push and pull request. Run it locally:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/validate_examples.py
```

The validator fetches the schema from `philterd/phileas` at runtime, so updates to the canonical schema show up here without a manual sync step. If the Phileas schema changes in a way that breaks an example, the example must be updated (or the change rolled back) before the PR can merge.

## Contributing

The RFC process and contribution guidelines are forthcoming. For now, feedback on the v0.1 draft is welcome via GitHub issues.
