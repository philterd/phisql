# PhiSQL Specification

PhiSQL is the declarative query language for PII privacy operations across the Philterd toolkit.

This repository is the **specification**. The reference parser and AST library live in [`philterd/phisql`](https://github.com/philterd/phisql).

## Status

> [!IMPORTANT]
> **PhiSQL v0.1 is a DRAFT.** The grammar and semantics are subject to change before v1.0. Implementations may track the draft but must not claim conformance until v1.0 is published.

The current draft covers the **redaction subset**: `REDACT`, `DEIDENTIFY`, `IGNORE`, and supporting clauses that compile to the Phileas JSON policy schema. Discovery, monitoring, benchmarking, and cross-tool join verbs are scoped for later drafts.

## Repository layout

The spec is a set of machine-readable artifacts. There is no prose specification document; the artifacts are the spec.

```
spec/v0.1/
├── grammar/
│   ├── PhiSQL.g4           ANTLR4 grammar (executable normative reference)
│   └── PhiSQL.ebnf         ISO 14977 EBNF (tool-independent presentation)
├── catalog/
│   ├── entity-types.yaml   Entity name -> Phileas field + strategies array
│   ├── strategies.yaml     Strategy name -> Phileas enum + allowed arguments
│   ├── keywords.yaml       Reserved keyword list
│   └── predicates.yaml     Predicate forms and how they compile to conditions
└── examples/               Worked examples (.phisql source + compiled .json)
```

The reference implementation and SDKs consume these files directly. The compiler's behavior is defined by the catalog files; the parser is generated from the grammar.

## Versions

| Version | Status | Tag |
|---|---|---|
| v0.1 | Draft | [`v0.1-draft`](https://github.com/philterd/phisql-spec/releases/tag/v0.1-draft) |

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

The Phileas JSON schema has no top-level `name` or `description` fields; policy identity comes from the JSON filename, and human-readable description lives in a sibling Markdown file. PhiSQL `POLICY <name>` compiles to the output filename, and `DESCRIPTION '<text>'` compiles to a sibling `<name>.md` file.

`PERSON` is deferred to a later spec version. The Phileas schema replaced `person` with a `pheyes` block whose configuration surface is not yet settled; PhiSQL v0.1 exposes `FIRST_NAME`, `SURNAME`, and `PHYSICIAN_NAME` instead.

## Validation

Every artifact is cross-checked by the CI workflow in [`.github/workflows/validate.yml`](.github/workflows/validate.yml) on every push and pull request. The validator runs three checks:

1. **Catalog YAML files are well-formed** and contain the expected top-level keys.
2. **Every Phileas field referenced by the catalogs exists in the canonical Phileas schema.** If the Phileas schema renames or removes a field, this check fails and the catalog must be updated (or the change rolled back) before the PR can merge.
3. **Every example JSON file validates against the canonical Phileas schema.**

Run the validator locally:

```sh
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/validate_spec.py
```

## Trademark

"PhiSQL" is a registered trademark of Philterd, LLC. The specification is freely readable and implementable, but the **name** is reserved for implementations that pass the conformance test suite (forthcoming at [`philterd/phisql-conformance`](https://github.com/philterd/phisql-conformance)).

## License

The specification is licensed under the [Apache License, Version 2.0](LICENSE).

## Contributing

The RFC process and contribution guidelines are forthcoming. For now, feedback on the v0.1 draft is welcome via GitHub issues.
