# PhiSQL

PhiSQL is the declarative query language for PII privacy operations across the Philterd toolkit.

This repository contains both the **specification** and the **reference parser implementation**. They live together because they evolve together: the parser is generated from the grammar in the spec, and every example file in the spec is parsed by the implementation as part of CI.

## Status

> [!IMPORTANT]
> **PhiSQL v0.1 is a DRAFT.** The grammar and semantics are subject to change before v1.0. Implementations may track the draft but must not claim conformance until v1.0 is published.

PhiSQL today is the policy DSL; PhiSQL tomorrow is the unified query language for PII operations across the Philterd toolkit. The v0.1 draft covers policy authoring: `REDACT`, `DEIDENTIFY`, `IGNORE`, custom regex identifiers (`DEFINE IDENTIFIER ... MATCHING`), AI/NER detection (`DETECT PHEYE`), date shifting (`SHIFT`, `TRUNCATE_TO_YEAR`), and supporting clauses, all compiling to the Phileas JSON policy schema. Discovery (`FIND PII`), monitoring (`SELECT FROM phield.trends`), benchmarking (`COMPARE POLICY`), and cross-tool join verbs are scoped for later drafts and will earn the "SQL" suffix as they land.

## Repository layout

```
philterd/phisql/
├── spec/v0.1/
│   ├── grammar/
│   │   ├── PhiSQL.g4           ANTLR4 grammar (executable normative reference)
│   │   └── PhiSQL.ebnf         ISO 14977 EBNF (tool-independent presentation)
│   ├── catalog/
│   │   ├── entity-types.yaml   Entity name -> Phileas field + strategies array
│   │   ├── strategies.yaml     Strategy name -> Phileas enum + allowed arguments
│   │   ├── keywords.yaml       Reserved keyword list
│   │   ├── predicates.yaml     Predicate forms and how they compile to conditions
│   │   └── policy.yaml         POLICY declaration / filename relationship
│   └── examples/               Worked examples (.phisql source + compiled .json)
├── reference/                  Java reference implementation
│   ├── pom.xml
│   └── src/                    Wrapper around the ANTLR-generated parser
├── rfcs/                       Accepted/rejected RFCs (historical record)
└── scripts/                    Spec validators (Python)
```

The spec is the set of machine-readable artifacts under `spec/`. There is no prose specification document; the artifacts are the spec.

The reference implementation generates a Java parser from `spec/v0.1/grammar/PhiSQL.g4` at build time. It is published as `ai.philterd:phisql` and consumed by other Philterd projects (Phileas, Phinder, the future PhiSQL CLI).

## Versions

| Version | Status | Tag |
|---|---|---|
| v0.1 | Draft | [`v0.1-draft`](https://github.com/philterd/phisql/releases/tag/v0.1-draft) |

## Relationship to the Phileas policy schema

The [Phileas JSON policy schema](https://github.com/philterd/phileas/blob/main/policy-schema/redaction-policy-schema.json) is the **canonical execution contract** for redaction. PhiSQL is a **convenience authoring layer** that compiles to it.

```
PhiSQL source  ->  Compiler  ->  Phileas JSON policy  ->  Phileas runtime
```

The v0.1 governance posture:

- **Phileas JSON leads; PhiSQL follows.** Anything PhiSQL can express must be representable as Phileas JSON.
- **The runtime does not change.** Phileas continues to execute against the JSON schema it already understands.
- **The policy library stays in JSON.** [`philterd/pii-redaction-policies`](https://github.com/philterd/pii-redaction-policies) remains the source of truth for distributable policies.
- **No proprietary extensions.** PhiSQL must not introduce constructs that have no Phileas JSON equivalent.
- **Backward compatible forever.** Existing JSON policies remain canonical. There is no migration; PhiSQL is additive.

The Phileas JSON schema has no top-level `name` or `description` fields; policy identity comes from the JSON filename, and human-readable description lives in a sibling Markdown file. PhiSQL `POLICY <name>` is optional; when present, its name must match the file basename after hyphen/underscore normalization (the filename can be `hipaa-safe-harbor.phisql` while the PhiSQL identifier is `hipaa_safe_harbor`). The full rule is documented in [`spec/v0.1/catalog/policy.yaml`](spec/v0.1/catalog/policy.yaml). `DESCRIPTION '<text>'` compiles to a sibling `<basename>.md` file.

`PERSON` is deferred to a later spec version. The Phileas schema replaced `person` with a `pheyes` block whose configuration surface is not yet settled; PhiSQL v0.1 exposes `FIRST_NAME`, `SURNAME`, and `PHYSICIAN_NAME` instead.

## Validation

Two CI workflows enforce that the spec and the reference implementation cannot drift:

- **`.github/workflows/validate.yml`** runs `scripts/validate_spec.py` to verify (a) the catalog YAML files are well-formed, (b) every Phileas field referenced by the catalogs exists in the canonical Phileas schema, and (c) every example JSON file validates against the same Phileas schema.

- **`.github/workflows/reference.yml`** builds the Java reference implementation, which generates a parser from `spec/v0.1/grammar/PhiSQL.g4` and parses every `.phisql` example file as part of its test suite. Any grammar change that breaks an example, or any new example the grammar can't parse, fails this job.

Run them locally:

```sh
# Spec checks
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/validate_spec.py

# Reference implementation
cd reference && mvn verify
```

## When this repo will split

This single-repo arrangement is the right shape while PhiSQL is pre-1.0 with one implementation. It will split into separate repos when at least one of these is true:

- A second implementation ships (third-party or first-party in another language).
- The conformance program goes public and starts certifying external implementations.
- The spec governance moves to a foundation.

The Phase 5 SDKs (Go, Python, etc.) and the conformance test suite already plan to be separate repos.

## Trademark

"PhiSQL" is a registered trademark of Philterd, LLC. The specification is freely readable and implementable, but the **name** is reserved for implementations that pass the conformance test suite (forthcoming at [`philterd/phisql-conformance`](https://github.com/philterd/phisql-conformance)).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the RFC process, lifecycle, review criteria, and versioning policy. The RFC template is at [`.github/RFC_TEMPLATE.md`](.github/RFC_TEMPLATE.md); accepted, rejected, and withdrawn RFCs live under [`rfcs/`](rfcs/).

Bug fixes, documentation tweaks, and new examples exercising already-specified grammar do not need an RFC — open a normal pull request. Feedback on the v0.1 draft is welcome via GitHub issues.

## License

The specification, reference implementation, and all artifacts in this repository are licensed under the [Apache License, Version 2.0](LICENSE).
