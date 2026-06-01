# PhiSQL

PhiSQL is the declarative query language for PII privacy operations across the Philterd toolkit.

This repository is the home of two things that evolve together:

- **The redaction policy schema** ([`schema/`](schema/)) — the canonical, versioned JSON Schema that defines a valid Phileas redaction policy. It is published to `https://philterd.ai/schemas/redaction-policy/<version>/schema.json` and is the contract that PhiSQL compiles to and that Phileas executes against.
- **PhiSQL** — the authoring language that compiles to that schema: its **specification** (`spec/`) and the **reference parser/compiler** (`reference/`).

They live in one repository because they change together: adding an entity type or strategy means updating the schema and PhiSQL's grammar and catalog in the same pull request, and CI validates every PhiSQL example against the schema under `schema/`.

## Status

> [!IMPORTANT]
> **PhiSQL v1.0 is stable.** The grammar and semantics of the v1.0 surface are frozen, and conforming implementations may claim conformance to v1.0. Subsequent changes follow the [versioning policy](CONTRIBUTING.md#versioning-policy): additive features land in minor versions, breaking changes require a new major version.

PhiSQL today is the policy DSL; PhiSQL tomorrow is the unified query language for PII operations across the Philterd toolkit. PhiSQL v1.0 is a complete authoring surface for the redaction policy schema: `REDACT`, `DEIDENTIFY`, `IGNORE`, custom regex identifiers (`DEFINE IDENTIFIER ... MATCHING`), custom dictionaries (`DEFINE DICTIONARY ... TERMS`), section redaction (`DEFINE SECTION START ... END`), AI/NER detection (`DETECT PHEYE`), date shifting (`SHIFT`, `RELATIVE`, `TRUNCATE_TO_YEAR`), global configuration (`CONFIGURE SPLITTING | PDF | POSTFILTERS | ANALYSIS`), graphical bounding boxes (`CONFIGURE GRAPHICAL BOX`), per-filter knobs (`OPTIONS ( ... )`), and supporting clauses — all compiling to the Phileas JSON policy schema. Every property in the schema is expressible — down to individual strategy parameters, entity-specific validation flags, and nested structures (arrays of objects, map objects, nested config) via recursive `OPTIONS ( ... )` / `[ ... ]` settings. The only schema field PhiSQL does not surface is the **deprecated** `person` block (the schema itself says "use `pheyes` instead"), whose capability is already fully available through `DETECT PHEYE`. Discovery (`FIND PII`), monitoring (`SELECT FROM phield.trends`), benchmarking (`COMPARE POLICY`), and cross-tool join verbs are scoped for later versions and will earn the "SQL" suffix as they land.

## Repository layout

The spec is the set of machine-readable artifacts under `spec/`. There is no prose specification document; the artifacts are the spec.

The reference implementation generates a Java parser from `spec/v1.0/grammar/PhiSQL.g4` at build time. It is published as `ai.philterd:phisql` and consumed by other Philterd projects (Phileas, Phinder, the future PhiSQL CLI).

## Versions

| Version | Status | Tag |
|---|---|---|
| v1.0 | Stable | [`v1.0.0`](https://github.com/philterd/phisql/releases/tag/v1.0.0) |

## Reference implementation compatibility

The `ai.philterd:phisql` jar version and the schema version are independent. The jar may receive bug fixes and improvements without a schema change. Use this table to find the right jar version for your target schema.

| Schema version | Compatible jar versions |
|---|---|
| 1.0.0 | 1.0.0 |

## Relationship to the redaction policy schema

The [redaction JSON policy schema](https://philterd.ai/schemas/redaction-policy/1.0.0/schema.json) is the **canonical execution contract** for redaction. PhiSQL is a **convenience authoring layer** that compiles to it.

```
PhiSQL source  ->  Compiler  ->  Phileas JSON policy  ->  Phileas runtime
```

The governance posture:

- **The policy json schema leads; PhiSQL follows.** Anything PhiSQL can express must be representable as Phileas JSON.
- **The runtime does not change.** Phileas continues to execute against the JSON schema it already understands.
- **The policy library stays in JSON.** [`philterd/pii-redaction-policies`](https://github.com/philterd/pii-redaction-policies) remains the source of truth for distributable policies.
- **No proprietary extensions.** PhiSQL must not introduce constructs that have no Phileas JSON equivalent.
- **Backward compatible forever.** Existing JSON policies remain canonical. There is no migration; PhiSQL is additive.

The Phileas JSON schema has no top-level `name` or `description` fields; policy identity comes from the JSON filename, and human-readable description lives in a sibling Markdown file. PhiSQL `POLICY <name>` is optional; when present, its name must match the file basename after hyphen/underscore normalization (the filename can be `hipaa-safe-harbor.phisql` while the PhiSQL identifier is `hipaa_safe_harbor`). The full rule is documented in [`spec/v1.0/catalog/policy.yaml`](spec/v1.0/catalog/policy.yaml). `DESCRIPTION '<text>'` compiles to a sibling `<basename>.md` file.

`PERSON` is deferred to a later spec version. The Phileas schema replaced `person` with a `pheyes` block whose configuration surface is not yet settled; PhiSQL v1.0 exposes `FIRST_NAME`, `SURNAME`, and `PHYSICIAN_NAME` instead.

## Validation

Two CI workflows enforce that the spec and the reference implementation cannot drift:

- **`.github/workflows/validate.yml`** runs `scripts/validate_spec.py` to verify (a) the catalog YAML files are well-formed, (b) every Phileas field referenced by the catalogs exists in the canonical Phileas schema, (c) every example JSON file validates against the same Phileas schema, (d) discovery examples reference known findings columns, (e) PhiSQL covers the schema — every schema identifier, strategy, and top-level block is either exposed by PhiSQL or recorded as a deliberate deferral — and (f) PhiSQL covers every schema *leaf field*, descending into each policy object so no individual property can silently fall behind the schema.

- **`.github/workflows/reference.yml`** builds the Java reference implementation, which generates a parser from `spec/v1.0/grammar/PhiSQL.g4` and parses every `.phisql` example file as part of its test suite. Any grammar change that breaks an example, or any new example the grammar can't parse, fails this job.

Run them locally:

```sh
# Spec checks
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/validate_spec.py

# Reference implementation
cd reference && mvn verify
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the RFC process, lifecycle, review criteria, and versioning policy. The RFC template is at [`.github/RFC_TEMPLATE.md`](.github/RFC_TEMPLATE.md); accepted, rejected, and withdrawn RFCs live under [`rfcs/`](rfcs/).

Bug fixes, documentation tweaks, and new examples exercising already-specified grammar do not need an RFC — open a normal pull request. Feedback on PhiSQL v1.0 is welcome via GitHub issues.

## License

"PhiSQL" is a registered trademark of Philterd, LLC. The specification is freely readable and implementable, but the **name** is reserved for implementations that pass the conformance test suite (forthcoming at [`philterd/phisql-conformance`](https://github.com/philterd/phisql-conformance)).

The specification, reference implementation, and all artifacts in this repository are licensed under the [Apache License, Version 2.0](LICENSE).
