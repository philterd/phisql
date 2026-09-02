# Release Notes

All notable changes to the PhiSQL Python reference implementation (the `phisql` package) are recorded here. Versions follow [Semantic Versioning](https://semver.org/).

The implementation version is independent of the PhiSQL policy schema version it implements (exposed through `phisql/policy_schema.py`). Specification-level changes (grammar, schema, catalog, examples) are recorded in the repository [release notes](../../RELEASE_NOTES.md).

1.2.0 is the initial release.

## 1.3.0 - 2026-09-02

Targets policy schema 1.3.0. **This release breaks existing input**: a document using `REDACT PHYSICIAN_NAME ...` no longer compiles. Read the migration note below before upgrading.

### Added

- **Support for policy schema 1.3.0**, implementing the PhiSQL 1.3.0 language surface: the removal of `PHYSICIAN_NAME`, the renamed `zipCodeFilterStrategies`, and the optional top-level `metadata` object. See the repository [release notes](../../RELEASE_NOTES.md) for the specification-level detail.
- **`DESCRIPTION` now compiles to `metadata.description`** (#23). The clause on a `POLICY` declaration previously had nowhere to go in the policy JSON, so a caller who wanted to keep the text wrote it somewhere else. It is now written into the compiled policy, so a description survives export, import, and sharing. `CompileResult.description` still carries it as well, so callers that keep a description elsewhere are unaffected, and a policy without a `DESCRIPTION` clause compiles to the same JSON as before (no empty `metadata` object).
- **`EntityType.phileas_strategies_field_aliases`**, holding earlier names for the strategies array that an engine must still read. It defaults to an empty tuple, so existing construction of `EntityType` keeps working.

### Changed

- `SUPPORTED_SCHEMA_VERSION` is now `1.3.0`, and the schema packaged with the distribution advances accordingly.
- **The zip-code filter now emits `zipCodeFilterStrategies` (plural)** (philterd/phileas#337), matching every other filter and the `1.3.0` schema. The compiler reads the name from the catalog, which also records `zipCodeFilterStrategy` as a deprecated alias an engine must still accept.

### Removed

- **`PHYSICIAN_NAME` entity type** (RFC #35). `REDACT PHYSICIAN_NAME WITH ...` now fails with a semantic error instead of compiling to a `physicianName` filter, and the compiled JSON no longer carries `identifiers.physicianName` (which schema `1.3.0` rejects). It was the one rules-based entity no conforming implementation could be held to, so it had no portable behavior to preserve.

### Migration

Physician-name detection moves to PhEye (AI/NER), the same path `PERSON` was deferred to in v1.0. Replace

```sql
REDACT PHYSICIAN_NAME WITH REDACT;
```

with

```sql
DETECT PHEYE LABELS ('physician name') WITH REDACT;
```

## 1.2.0 - 2026-07-13

Initial release of the Python reference parser and compiler, targeting policy schema 1.2.0.

### Added

- **Python reference parser and compiler.** Parses PhiSQL (an ANTLR4 grammar generated from `spec/v1.0/grammar/PhiSQL.g4`) and compiles it to Phileas JSON, driven by the specification catalog YAML files packaged with the distribution.
- **`policy_schema` module.** Exposes the canonical redaction policy schema packaged with the distribution (`SUPPORTED_SCHEMA_VERSION` and schema accessors), so dependents read the schema without checking out this repository.
- **Targets policy schema 1.2.0**, implementing the full PhiSQL 1.2.0 language surface. This includes the 1.1.0 features (the `MODEL` clause for local GLiNER inference in `DETECT PHEYE`, identifier `validator` support through the `OPTIONS(...)` passthrough, and the widened `maskLength`) and the 1.2.0 additions (`overlap` on `config.splitting`, filter and strategy `id` labels, `spanDisambiguation` on `config.analysis`, phone `region`, the `MAP_REPLACE` strategy with the top-level `generators` block and `DEFINE GENERATOR` statement, strategy `color`, and the `EIN` entity type). See the repository [release notes](../../RELEASE_NOTES.md) for the specification-level detail.
- **Date-only strategy enforcement.** The compiler rejects `SHIFT`, `TRUNCATE_TO_YEAR`, and `RELATIVE` applied to any target other than the `DATE` entity, with a clear semantic error.
- **`STATIC_REPLACE` requires its `value` argument.** A `STATIC_REPLACE` strategy written without `value` fails with a semantic error instead of compiling an empty substitution.
- **A `WHERE` clause compiles to `condition` (singular)**, matching the schema and the Phileas runtimes, so a `WHERE` clause is no longer silently dropped.
