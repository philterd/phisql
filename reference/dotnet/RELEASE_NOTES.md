# Release Notes

All notable changes to the PhiSQL .NET reference implementation (the `Philterd.PhiSql` NuGet package) are recorded here. Versions follow [Semantic Versioning](https://semver.org/).

The package version tracks the PhiSQL specification and policy schema it implements. The .NET reference implementation was introduced alongside PhiSQL 1.1.0, so its release history starts at 1.1.0 (there is no 1.0.0 .NET release). Specification-level changes (grammar, schema, catalog, examples) are recorded in the repository [CHANGELOG](../../CHANGELOG.md).

## 1.1.1 - 2026-06-21

A packaging-only patch: it implements the same PhiSQL 1.1.0 specification and policy schema as 1.1.0, so the version stays on the 1.1.x line.

### Added

- **`net8.0` target framework.** The package now multi-targets `net8.0` and `net10.0` (previously `net10.0` only), so it can be consumed from .NET 8 (LTS) as well as .NET 10. No public API, behavior, or schema change; the bundled policy schema is unchanged at 1.1.0.

## 1.1.0 - 2026-06-18

First published release of the `Philterd.PhiSql` NuGet package: the .NET reference parser and compiler for PhiSQL.

### Added

- **`Philterd.PhiSql` NuGet package.** The .NET reference implementation, packaged for NuGet with sources, a symbols package (`.snupkg`), and SourceLink for step-into debugging. Targets `net10.0`.
- **PhiSQL parser and compiler.** Parses PhiSQL (an ANTLR4 grammar generated from `spec/v1.0/grammar/PhiSQL.g4`) and compiles it to Phileas JSON, driven by the specification catalog YAML files, which are embedded in the assembly as resources.
- **`PolicySchema` API.** Exposes the canonical redaction policy schema bundled in the assembly: `GetSupportedSchemaVersion()` returns the schema version and `GetSchema()` returns the schema JSON, so dependents read the schema without checking out this repository.
- **Targets policy schema 1.1.0**, implementing the PhiSQL 1.1.0 language surface, including the `MODEL` clause for local GLiNER inference in `DETECT PHEYE`, identifier `validator` support through the `OPTIONS(...)` passthrough, and the widened `maskLength`. See the repository [CHANGELOG](../../CHANGELOG.md) for the specification-level detail.
