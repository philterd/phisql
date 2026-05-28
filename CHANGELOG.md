# Changelog

All notable changes to the PhiSQL specification are documented here.

This project does not yet follow [Semantic Versioning](https://semver.org/) because it is pre-1.0. Major version semantics will be defined when v1.0 is published.

## [Unreleased]

### Added

- Reference parser implementation under `reference/` (Java, ANTLR4). The parser is generated from `spec/v0.1/grammar/PhiSQL.g4` at build time. The `ExamplesParseTest` parses every `.phisql` example file as part of the test suite; any grammar/example drift fails the build.
- Reference compiler that translates parsed PhiSQL into Phileas JSON. The compiler is driven by the catalog YAML files (`spec/v0.1/catalog/*.yaml`), which are bundled inside the JAR as resources. `CompilerTest` compiles every example `.phisql` file and asserts byte-equivalent JSON output against the corresponding `.json` file. `CompileErrorTest` covers compile-time error cases (unknown entity, unknown strategy argument, invalid enum value).
- Five additional spec examples (06-10) exercising multi-strategy entities, format-preserving encryption, multiple confidence bands, policy-wide ignore patterns, and named strategy arguments. The compiler test suite now covers 10 representative policies, matching the round-trip-coverage criterion from issue #127.
- `.github/workflows/reference.yml` to build and test the reference implementation.

### Changed

- Repository renamed from `philterd/phisql-spec` to `philterd/phisql` to reflect that it now contains both the specification and the reference implementation.
- Restructured the v0.1 spec into machine-readable artifacts: ANTLR4 grammar (`PhiSQL.g4`), EBNF grammar (`PhiSQL.ebnf`), and YAML catalog files for entity types, strategies, keywords, and predicates. The previous prose `SPEC.md` has been removed; the artifacts are now the spec.
- The validator (`scripts/validate_spec.py`) now runs three checks on every push and PR: catalog well-formedness, catalog references resolving against the canonical Phileas schema, and example JSON validating against the same schema.
- Grammar: the `literal` production now accepts a bare identifier (`ID`) in addition to string, numeric, and boolean literals. This is required for enum-typed strategy arguments such as `scope=document`. The compiler is expected to validate that bare identifiers correspond to enum values declared in `strategies.yaml` for the relevant argument. Surfaced by `ExamplesParseTest` failing on the support-tickets example.

### Fixed

- `BITCOIN_ADDRESS` strategies field name corrected to `bitcoinFilterStrategies` (the catalog validator caught the discrepancy with the Phileas schema).

## [v0.1-draft] - 2026-05-28

### Added

- Initial draft of the PhiSQL specification.
- Redaction subset: `POLICY`, `REDACT`, `DEIDENTIFY`, `IGNORE` statements.
- Grammar in EBNF.
- Entity type mapping aligned 1:1 with the Phileas JSON policy schema (`$defs.identifiers.properties`).
- Filter strategy mapping aligned 1:1 with `baseFilterStrategy.strategy` enum.
- Predicate support for `CONFIDENCE` comparisons in `WHERE` clauses.
- Custom identifier references via `IDENTIFIER('name')`.
- Five worked examples with side-by-side PhiSQL source and compiled Phileas JSON.
- Relationship to Phileas policy schema documented: Phileas JSON is canonical; PhiSQL compiles to it; no proprietary extensions.

### Status

- Draft. Grammar and semantics may change before v1.0.
- Implementations may track the draft but must not claim conformance until v1.0 is published.
