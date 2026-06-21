# Release Notes

All notable changes to the PhiSQL Python reference implementation (the `phisql` package) are recorded here. Versions follow [Semantic Versioning](https://semver.org/).

The implementation version is independent of the PhiSQL policy schema version it implements (exposed through `phisql/policy_schema.py`). Specification-level changes (grammar, schema, catalog, examples) are recorded in the repository [release notes](../../RELEASE_NOTES.md).

This package has not yet been published to PyPI; 1.1.0 is the initial release.

## 1.1.0 - Unreleased

Initial release of the Python reference parser and compiler, introduced alongside the PhiSQL 1.1.0 cycle and targeting policy schema 1.1.0.

### Added

- **Python reference parser and compiler.** Parses PhiSQL (an ANTLR4 grammar generated from `spec/v1.0/grammar/PhiSQL.g4`) and compiles it to Phileas JSON, driven by the specification catalog YAML files packaged with the distribution.
- **`policy_schema` module.** Exposes the canonical redaction policy schema packaged with the distribution (`SUPPORTED_SCHEMA_VERSION` and schema accessors), so dependents read the schema without checking out this repository.
- **Targets policy schema 1.1.0**, implementing the PhiSQL 1.1.0 language surface: the `MODEL` clause for local GLiNER inference in `DETECT PHEYE`, identifier `validator` support through the `OPTIONS(...)` passthrough, and the widened `maskLength`. See the repository [release notes](../../RELEASE_NOTES.md) for the specification-level detail.
- **Date-only strategy enforcement.** The compiler rejects `SHIFT`, `TRUNCATE_TO_YEAR`, and `RELATIVE` applied to any target other than the `DATE` entity, with a clear semantic error.
