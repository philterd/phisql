# Changelog

All notable changes to the PhiSQL specification are documented here.

This project does not yet follow [Semantic Versioning](https://semver.org/) because it is pre-1.0.
Major version semantics will be defined when v1.0 is published.

## [v0.1] - 2026-05-28 (Draft)

### Added

- Initial draft of the PhiSQL specification.
- Redaction subset: `POLICY`, `REDACT`, `DEIDENTIFY`, `IGNORE` statements.
- Grammar in EBNF.
- Entity type mapping aligned 1:1 with the Phileas JSON policy schema (`$defs.identifiers.properties`).
- Filter strategy mapping aligned 1:1 with `baseFilterStrategy.strategy` enum.
- Predicate support for `CONFIDENCE` comparisons in `WHERE` clauses.
- Custom identifier references via `IDENTIFIER('name')`.
- Dictionary references via `DICTIONARY('name')`.
- Five worked examples with side-by-side PhiSQL source and compiled Phileas JSON:
  1. Minimal SSN redaction.
  2. HIPAA Safe Harbor de-identification.
  3. PCI DSS scope reduction.
  4. FRBP 9037 bankruptcy filings.
  5. Support tickets with allowlist.
- Appendix A: complete PhiSQL → Phileas JSON mapping reference.
- Appendix B: reserved keyword list.
- Relationship to Phileas policy schema documented: Phileas JSON is canonical; PhiSQL compiles to it; no proprietary extensions.

### Status

- Draft. Grammar and semantics may change before v1.0.
- Implementations may track the draft but must not claim conformance until v1.0 is published.
