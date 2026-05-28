# Changelog

All notable changes to the PhiSQL specification are documented here.

This project does not yet follow [Semantic Versioning](https://semver.org/) because it is pre-1.0. Major version semantics will be defined when v1.0 is published.

## [Unreleased]

### Changed

- Restructured the v0.1 spec into machine-readable artifacts: ANTLR4 grammar (`PhiSQL.g4`), EBNF grammar (`PhiSQL.ebnf`), and YAML catalog files for entity types, strategies, keywords, and predicates. The previous prose `SPEC.md` has been removed; the artifacts are now the spec.
- The validator (`scripts/validate_spec.py`) now runs three checks on every push and PR: catalog well-formedness, catalog references resolving against the canonical Phileas schema, and example JSON validating against the same schema.

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
