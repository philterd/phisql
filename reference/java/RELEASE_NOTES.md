# Release Notes

All notable changes to the PhiSQL Java reference implementation (the `ai.philterd:phisql` artifact on Maven Central) are recorded here. Versions follow [Semantic Versioning](https://semver.org/).

The implementation version is independent of the PhiSQL policy schema version it implements (exposed through `PolicySchema.getSupportedSchemaVersion()`). Specification-level changes (grammar, schema, catalog, examples) are recorded in the repository [release notes](../../RELEASE_NOTES.md).

## 1.3.0 - 2026-07-13

Targets policy schema 1.2.0.

### Added

- **Support for policy schema 1.2.0**, implementing the PhiSQL 1.2.0 language surface: `overlap` on `config.splitting`, filter and strategy `id` labels, `spanDisambiguation` on `config.analysis`, phone `region`, the `MAP_REPLACE` strategy with the top-level `generators` block and `DEFINE GENERATOR` statement, strategy `color`, and the `EIN` entity type. See the repository [release notes](../../RELEASE_NOTES.md) for the specification-level detail.

### Changed

- `PolicySchema.getSupportedSchemaVersion()` now returns `1.2.0`, and the bundled schema advances accordingly (`redaction.policy.schema.version`).
- **`STATIC_REPLACE` now requires its `value` argument.** A `STATIC_REPLACE` strategy written without `value` fails with a semantic error instead of compiling an empty substitution.

### Fixed

- **A `WHERE` clause now compiles to `condition` (singular).** The compiler previously emitted `conditions` (plural), which the schema does not define and the Phileas runtimes ignore, so a `WHERE` clause was silently dropped.

## 1.2.0 - 2026-06-22

Targets policy schema 1.1.0 (unchanged from 1.1.0).

### Changed

- Lowered the Java baseline from 25 to 17. The `ai.philterd:phisql` artifact now compiles to Java 17 bytecode, so it can be embedded in Java 17 and Java 21 runtimes (for example as a transitive dependency of Phileas inside OpenSearch and Elasticsearch plugins) that could not load the previous Java 25 build. There are no API or language changes; consumers on Java 21 or newer are unaffected.

## 1.1.0 - 2026-06-17

Targets policy schema 1.1.0. The Java sources moved from `reference/` to `reference/java/` in this release, alongside the new Python and .NET reference implementations.

### Added

- **Support for policy schema 1.1.0**, implementing the PhiSQL 1.1.0 language surface: the `MODEL` clause for local GLiNER inference in `DETECT PHEYE`, identifier `validator` support through the `OPTIONS(...)` passthrough, and the widened `maskLength`. See the repository [release notes](../../RELEASE_NOTES.md) for the specification-level detail.
- The `validators.yaml` catalog is bundled into the jar as a resource alongside the other catalogs.

### Changed

- `PolicySchema.getSupportedSchemaVersion()` now returns `1.1.0`, and the bundled schema advances accordingly (`redaction.policy.schema.version`).
- **Date-only strategies are now enforced.** The compiler rejects `SHIFT`, `TRUNCATE_TO_YEAR`, and `RELATIVE` applied to any target other than the `DATE` entity, with a clear semantic error. `REDACT SSN WITH SHIFT(days=30)` previously compiled and now fails.

## 1.0.0 - 2026-06-01

First stable release of the Java reference parser and compiler, targeting policy schema 1.0.0.

### Added

- **`ai.philterd:phisql` published to Maven Central**, with attached sources and javadoc jars and GPG signing via the `sign` profile.
- **PhiSQL parser and compiler.** Parses PhiSQL (an ANTLR4 grammar generated from `spec/v1.0/grammar/PhiSQL.g4` at build time) and compiles it to Phileas JSON, driven by the specification catalog YAML files, which are bundled inside the jar as resources.
- **`PolicySchema` API.** Exposes the canonical redaction policy schema bundled in the jar (`getSupportedSchemaVersion()`, `getSchema()`), so dependents read the schema without checking out this repository.
- **Targets policy schema 1.0.0**, implementing the frozen PhiSQL 1.0 language surface. See the repository [release notes](../../RELEASE_NOTES.md) for the specification-level detail.
