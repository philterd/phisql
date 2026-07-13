# Release Notes

All notable changes to the PhiSQL Python reference implementation (the `phisql` package) are recorded here. Versions follow [Semantic Versioning](https://semver.org/).

The implementation version is independent of the PhiSQL policy schema version it implements (exposed through `phisql/policy_schema.py`). Specification-level changes (grammar, schema, catalog, examples) are recorded in the repository [release notes](../../RELEASE_NOTES.md).

1.2.0 is the initial release.

## 1.2.0 - 2026-07-13

Initial release of the Python reference parser and compiler, targeting policy schema 1.2.0.

### Added

- **Python reference parser and compiler.** Parses PhiSQL (an ANTLR4 grammar generated from `spec/v1.0/grammar/PhiSQL.g4`) and compiles it to Phileas JSON, driven by the specification catalog YAML files packaged with the distribution.
- **`policy_schema` module.** Exposes the canonical redaction policy schema packaged with the distribution (`SUPPORTED_SCHEMA_VERSION` and schema accessors), so dependents read the schema without checking out this repository.
- **Targets policy schema 1.2.0**, implementing the full PhiSQL 1.2.0 language surface. This includes the 1.1.0 features (the `MODEL` clause for local GLiNER inference in `DETECT PHEYE`, identifier `validator` support through the `OPTIONS(...)` passthrough, and the widened `maskLength`) and the 1.2.0 additions (`overlap` on `config.splitting`, filter and strategy `id` labels, `spanDisambiguation` on `config.analysis`, phone `region`, the `MAP_REPLACE` strategy with the top-level `generators` block and `DEFINE GENERATOR` statement, strategy `color`, and the `EIN` entity type). See the repository [release notes](../../RELEASE_NOTES.md) for the specification-level detail.
- **Date-only strategy enforcement.** The compiler rejects `SHIFT`, `TRUNCATE_TO_YEAR`, and `RELATIVE` applied to any target other than the `DATE` entity, with a clear semantic error.
- **`STATIC_REPLACE` requires its `value` argument.** A `STATIC_REPLACE` strategy written without `value` fails with a semantic error instead of compiling an empty substitution.
- **A `WHERE` clause compiles to `condition` (singular)**, matching the schema and the Phileas runtimes, so a `WHERE` clause is no longer silently dropped.
