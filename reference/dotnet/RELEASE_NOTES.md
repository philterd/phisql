# Release Notes

All notable changes to the PhiSQL .NET reference implementation (the `Philterd.PhiSql` NuGet package) are recorded here. Versions follow [Semantic Versioning](https://semver.org/).

The implementation version is independent of the PhiSQL policy schema version it implements (exposed through the `PolicySchema` API). The .NET reference implementation was introduced alongside the PhiSQL 1.1.0 cycle, so its release history starts at 1.1.0 (there is no 1.0.0 .NET release). Specification-level changes (grammar, schema, catalog, examples) are recorded in the repository [release notes](../../RELEASE_NOTES.md). The current development version is `1.3.0-preview`.

## 1.2.0 - 2026-07-13

Targets policy schema 1.2.0.

### Added

- **Support for policy schema 1.2.0**, implementing the PhiSQL 1.2.0 language surface: `overlap` on `config.splitting`, filter and strategy `id` labels, `spanDisambiguation` on `config.analysis`, phone `region`, the `MAP_REPLACE` strategy with the top-level `generators` block and `DEFINE GENERATOR` statement, strategy `color`, and the `EIN` entity type. See the repository [release notes](../../RELEASE_NOTES.md) for the specification-level detail.

### Changed

- `PolicySchema.GetSupportedSchemaVersion()` now returns `1.2.0`, and the bundled schema advances accordingly (`redaction.policy.schema.version`).
- **`STATIC_REPLACE` now requires its `value` argument.** A `STATIC_REPLACE` strategy written without `value` fails with a semantic error instead of compiling an empty substitution.

### Fixed

- **A `WHERE` clause now compiles to `condition` (singular).** The compiler previously emitted `conditions` (plural), which the schema does not define and the Phileas runtimes ignore, so a `WHERE` clause was silently dropped.

## 1.1.1 - 2026-06-21

Published to NuGet. Implements the same policy schema 1.1.0 as 1.1.0.

### Added

- **`net8.0` target framework.** The package now multi-targets `net8.0` and `net10.0` (previously `net10.0` only), so it can be consumed from .NET 8 (LTS) as well as .NET 10. No public API or behavior change; the bundled policy schema is unchanged at 1.1.0.

## 1.1.0 - 2026-06-18

First published release of the `Philterd.PhiSql` NuGet package: the .NET reference parser and compiler for PhiSQL.

### Added

- **`Philterd.PhiSql` NuGet package.** The .NET reference implementation, packaged for NuGet with sources, a symbols package (`.snupkg`), and SourceLink for step-into debugging. Targets `net10.0`.
- **PhiSQL parser and compiler.** Parses PhiSQL (an ANTLR4 grammar generated from `spec/v1.0/grammar/PhiSQL.g4`) and compiles it to Phileas JSON, driven by the specification catalog YAML files, which are embedded in the assembly as resources.
- **`PolicySchema` API.** Exposes the canonical redaction policy schema bundled in the assembly: `GetSupportedSchemaVersion()` returns the schema version and `GetSchema()` returns the schema JSON, so dependents read the schema without checking out this repository.
- **Targets policy schema 1.1.0**, implementing the PhiSQL 1.1.0 language surface, including the `MODEL` clause for local GLiNER inference in `DETECT PHEYE`, identifier `validator` support through the `OPTIONS(...)` passthrough, and the widened `maskLength`. See the repository [release notes](../../RELEASE_NOTES.md) for the specification-level detail.
