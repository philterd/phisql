# Changelog

All notable changes to the PhiSQL specification are documented here.

This project does not yet follow [Semantic Versioning](https://semver.org/) because it is pre-1.0. Major version semantics will be defined when v1.0 is published.

## [Unreleased]

### Added

- **Discovery query verbs.** Three scan verbs and one query verb were added to the grammar:
  - `FIND PII IN '<uri>' [WHERE <predicate>]`
  - `DISCOVER ENTITIES IN '<uri>' [WHERE <predicate>]`
  - `SCAN IN '<uri>' [WHERE <predicate>]`
  - `SELECT <projection> FROM <findings-ref> [WHERE ...] [GROUP BY ...] [LIMIT n]`
  These compile to a separate discovery-query JSON shape (not Phileas JSON). Conforming discovery engines such as Phinder consume the discovery-query JSON.
- **`IN '<uri>'` clause** in discovery statements, accepting URIs from the schemes declared in `spec/v0.1/catalog/sources.yaml` (S3, GCS, Azure Blob, local filesystem, PostgreSQL, MySQL, Snowflake, BigQuery).
- **Discovery WHERE predicates** over finding-row columns. Supported forms: `<column> IN ('a', 'b')`, `<column> <op> <literal>`, and `AND`/`OR`/parenthesization.
- **SELECT projection surface**: column references, `*`, and aggregates (`COUNT`, `AVG`, `SUM`, `MIN`, `MAX`).
- **`spec/v0.1/catalog/findings.yaml`** documenting the canonical findings table schema (columns, types, filterable subset, groupable subset). Sets `phinder` as the default namespace for the unqualified `findings` reference.
- **`spec/v0.1/catalog/sources.yaml`** listing the URI schemes recognized in the `IN` clause. Engines that do not support a scheme must reject statements with a clear error rather than silently no-op.
- **Reserved keywords** added: `FIND`, `PII`, `DISCOVER`, `ENTITIES`, `SCAN`, `IN`, `SELECT`, `FROM`, `BY`, `LIMIT`, `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`. Pre-1.0, breaking changes may land within a minor version (per `CONTRIBUTING.md`'s versioning policy), so these reservations were folded into v0.1 rather than triggering a v0.2 cut.
- **Five discovery examples** under `spec/v0.1/examples/` covering S3, GCS, Azure Blob, local filesystem, and a `SELECT ... GROUP BY` over the findings store (`15-find-pii-s3`, `16-discover-entities-gcs`, `17-scan-azure-blob`, `18-find-pii-local-filesystem`, `19-select-findings-groupby`).
- **`columnRef` accepts `CONFIDENCE`** in addition to `ID`, because `CONFIDENCE` is reserved by the redaction predicate but is a valid findings-table column.
- **Validator check** added: `scripts/validate_spec.py` now walks discovery example JSONs and verifies every column referenced resolves against `findings.yaml`. Catalog well-formedness covers `findings.yaml` and `sources.yaml`.

### Changed

- `CompilerTest` parses every `.phisql` under `spec/v0.1/examples/` but compiles only the redaction subset. The five discovery examples are listed in `DISCOVERY_EXAMPLES_NOT_YET_COMPILED` and skipped explicitly. A discovery compiler will land in a follow-up; the set shrinks as it ships.
- `ExamplesParseTest` parses all 19 examples (14 redaction + 5 discovery).

### Notes

- The RFC process described in `CONTRIBUTING.md` was intentionally skipped for the discovery additions while the project is still finding its shape. Substantial future grammar changes are expected to go through an RFC. Closes philterd/philterd-website#122.

### Added (v0.1 work, pre-v0.2 cut)

- Date-shifting strategies `SHIFT` and `TRUNCATE_TO_YEAR` (DATE entities only). `SHIFT` accepts `days`, `months`, `years`, and `random` arguments, mapping to `shiftDays`/`shiftMonths`/`shiftYears`/`shiftRandom` on the Phileas `dateFilterStrategy`. Example `12-date-shift`.
- `DEFINE IDENTIFIER '<classification>' MATCHING '<regex>' [GROUP n] [CASE SENSITIVE | CASE INSENSITIVE] WITH <strategy>` statement for declaring custom regex identifiers inline (previously only referenceable via `IDENTIFIER('name')`, with no way to supply a pattern). Compiles to an entry in the Phileas `identifiers.identifiers` array. Example `13-custom-identifier`.
- `DETECT PHEYE [LABELS (...)] [ENDPOINT '<url>'] WITH <strategy>` statement for AI/NER detection via PhEye. Compiles to an entry in the Phileas `identifiers.pheyes` array with `phEyeFilterStrategies` and an optional `phEyeConfiguration` (`labels`, `endpoint`). This is the supported way to redact `PERSON` (which the catalog defers as a bare entity because it requires a PhEye block). Example `14-pheye-person-detection`.
- Catalog field `phileas_strategy_def` on strategy entries, declaring which Phileas schema `$def` a strategy validates against (defaults to `baseFilterStrategy`; date-only strategies use `dateFilterStrategy`). `scripts/validate_spec.py` now resolves each strategy against its declared def so date-specific strategies and arguments validate correctly.

- Reference parser implementation under `reference/` (Java, ANTLR4). The parser is generated from `spec/v0.1/grammar/PhiSQL.g4` at build time. The `ExamplesParseTest` parses every `.phisql` example file as part of the test suite; any grammar/example drift fails the build.
- Reference compiler that translates parsed PhiSQL into Phileas JSON. The compiler is driven by the catalog YAML files (`spec/v0.1/catalog/*.yaml`), which are bundled inside the JAR as resources. `CompilerTest` compiles every example `.phisql` file and asserts byte-equivalent JSON output against the corresponding `.json` file. `CompileErrorTest` covers compile-time error cases (unknown entity, unknown strategy argument, invalid enum value).
- Five additional spec examples (06-10) exercising multi-strategy entities, format-preserving encryption, multiple confidence bands, policy-wide ignore patterns, and named strategy arguments. The compiler test suite now covers 10 representative policies, matching the round-trip-coverage criterion from issue #127.
- `spec/v0.1/catalog/policy.yaml` defining the relationship between PhiSQL `POLICY` declarations and Phileas filenames: the filename basename is canonical, `POLICY` is optional, and when present the declared name must match the basename after hyphen/underscore normalization.
- Compiler overloads accepting a filename or an explicit expected name: `Compiler.compile(Path)`, `Compiler.compile(String, String expectedName)`, and `Compiler.compile(DocumentContext, String expectedName)`. `PolicyNamingTest` covers all paths through the new rule.
- Spec example `11-policy-wide-ignore-terms` covering scope-less `IGNORE TERMS`.
- Full Apache 2.0 license headers on every Java file.
- `.github/workflows/reference.yml` to build and test the reference implementation.
- RFC process and contribution guidelines: `CONTRIBUTING.md` at the repo root, `.github/RFC_TEMPLATE.md` for new proposals, and `rfcs/` directory for the historical record. Closes philterd/philterd-website#144.
- RFC 0001 (`rfcs/0001-scope-less-ignore-terms.md`) — worked example RFC documenting the scope-less `IGNORE TERMS` change end to end, for use as a reference by future authors.

### Changed

- Repository renamed from `philterd/phisql-spec` to `philterd/phisql` to reflect that it now contains both the specification and the reference implementation.
- Restructured the v0.1 spec into machine-readable artifacts: ANTLR4 grammar (`PhiSQL.g4`), EBNF grammar (`PhiSQL.ebnf`), and YAML catalog files for entity types, strategies, keywords, and predicates. The previous prose `SPEC.md` has been removed; the artifacts are now the spec.
- The validator (`scripts/validate_spec.py`) now runs three checks on every push and PR: catalog well-formedness, catalog references resolving against the canonical Phileas schema, and example JSON validating against the same schema.
- Grammar: the `literal` production now accepts a bare identifier (`ID`) in addition to string, numeric, and boolean literals. This is required for enum-typed strategy arguments such as `scope=document`. The compiler is expected to validate that bare identifiers correspond to enum values declared in `strategies.yaml` for the relevant argument. Surfaced by `ExamplesParseTest` failing on the support-tickets example.

### Fixed

- Scope-less `IGNORE TERMS (...)` (without a `FOR <entity>` clause) now compiles to the top-level `ignored` array in the Phileas schema instead of throwing a `CompileException`. The top-level `ignored` array uses the `{terms: [...]}` object shape per `$defs.ignored` in the Phileas schema.
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
