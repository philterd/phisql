# Changelog

All notable changes to the PhiSQL specification are documented here.

As of v1.0.0 this project follows [Semantic Versioning](https://semver.org/): additive, backward-compatible changes bump the minor version, and changes that break existing PhiSQL or Phileas JSON require a new major version.

## [1.1.0] - 2026-06-17

Local, on-device inference for `DETECT PHEYE`. A policy can now point PhEye at a local GLiNER model for fully offline redaction, with no remote PhEye service. Additive and backward-compatible: every 1.0.0 policy and compiled Phileas JSON remains valid and unchanged in meaning.

### Added

- **Local GLiNER inference for `DETECT PHEYE`** (RFC #14). A new optional `MODEL '<path>'` clause points PhEye at a local GLiNER model directory (the ONNX model, the SentencePiece tokenizer, and the GLiNER config) instead of, or in addition to, a remote `ENDPOINT`. When `MODEL` is set, detection runs on-device, and `LABELS` is the GLiNER detection prompt. The target model is the GLiNER-based Philterd PII model exported to ONNX. Example `pheye-local-model`.
- **Schema `1.1.0`** (`schema/1.1.0/schema.json`). `phEyeConfiguration` gains two optional properties:
  - `modelPath`: filesystem path to the local GLiNER model directory.
  - `threshold`: minimum span confidence for the local model to return a detection (number, default `0.5`).
- **`MODEL` reserved keyword**, added to the grammar, the EBNF, and `spec/v1.0/catalog/keywords.yaml`.
- **`spec/v1.1.0/examples/pheye-local-model`** example pair (`.phisql` and compiled `.json`), exercised by the Java, Python, and .NET reference test suites.
- **Identifier checksum and structural validation** (RFC #17). The custom `identifier` filter (`filterIdentifier`) gains an optional `validator` property in schema `1.1.0`: a named built-in validator (a `validatorName` string, or `{name, params}`) that a regex match must pass to be kept. This lets a generic regex identifier reject format-valid but checksum-invalid values (a SIN that fails Luhn, a CPF with bad check digits) without a dedicated per-identifier filter and without embedding executable code in a policy.
- **`spec/v1.0/catalog/validators.yaml`**: the source-of-truth catalog for the validator vocabulary (`luhn`, `mod11`, `mod97`, `mod23-letter`, `aba`, `verhoeff`, `damm`, `es-cif`, `de-steuerid`, `de-personalausweis`, `bic-structural`). The schema's `validatorName` enum is kept in sync with it.
- **`spec/v1.1.0/examples/identifier-validator`** example pair (`.phisql` and compiled `.json`), showing both the string and `{name, params}` validator forms set through the `OPTIONS(...)` passthrough, exercised by the Java, Python, and .NET reference test suites.
- **`maskLength` accepts a number** (RFC #13). In schema `1.1.0` the `MASK` strategy's `maskLength` is widened from `"string"` to `["string", "integer"]`, matching its own description ("can also be a number for fixed-length masking") and the strategy catalog (`mask_length: integer`). `REDACT SSN WITH MASK(mask_length = 4)` already compiled to `"maskLength": 4`, which silently violated the schema; that output is now valid, unchanged. Backward-compatible (it only relaxes a constraint). The frozen `schema/1.0.0` is left untouched; the fix lands in the current `1.1.0`.

### Changed

- The Java, Python, and .NET reference implementations target schema `1.1.0` and recognize the `MODEL` clause. The bundled schema version advances accordingly (`redaction.policy.schema.version`, `SchemaVersion`, and `SUPPORTED_SCHEMA_VERSION`).
- The reference implementations bundle the new `validators.yaml` catalog alongside the others (the Java and Python builds copy the catalog directory; the .NET project adds it as an embedded resource).
- The conformance runner (`compliance/run.py`) now validates accept-case output against the current schema version (`1.1.0`) rather than the frozen `1.0.0`, matching the reference implementations and `validate_spec.py`. The `mask-char-length` case is no longer schema-exempt (RFC #13).
- `validate_spec.py` now cross-checks that each strategy argument's catalog `type` is compatible with the schema `type` of the `phileas_field` it maps to, so a catalog/schema type contradiction (RFC #13, `maskLength`) cannot recur silently.
- **Date-only strategies are now enforced** (RFC #9). The Java, Python, and .NET reference compilers reject `SHIFT`, `TRUNCATE_TO_YEAR`, and `RELATIVE` applied to any target other than the `DATE` entity (another entity, a custom identifier, a dictionary, a section, or PhEye), with a clear semantic error. This is a conformance correction, not a new feature: the catalog already classifies these as `dateFilterStrategy` ("DATE entities only"); the compiler was simply lenient. `REDACT SSN WITH SHIFT(days=30)` previously compiled and now fails. Covered by the `reject/semantic/date-only-strategy` conformance case; the matching "Known underspecified areas" note is removed.

### Notes

- `threshold` is schema-only in 1.1: there is no PhiSQL clause for it, so a policy relies on the default or filters detections with `WHERE CONFIDENCE`. Only `MODEL` is expressible in the language.
- The date-only enforcement rejects existing `.phisql` that applied one of these strategies to a non-`DATE` target. Such policies never produced a meaningful redaction (the Phileas runtime would not apply the strategy), so the practical blast radius is small; this is why it lands as a conformance correction in 1.1 rather than a major bump. Existing Phileas JSON policies are unaffected.
- `validator` has no dedicated PhiSQL clause, but like any identifier-filter property it is expressible through the generic `OPTIONS(...)` passthrough, for example `DEFINE IDENTIFIER '...' MATCHING '...' WITH <strategy> OPTIONS (validator = 'luhn')`, which compiles to the `validator` property. A dedicated clause (for example `VALIDATE WITH`) is optional sugar deferred to a later RFC. An unknown validator name is a policy error and must not be silently ignored.

## [1.0.0] - 2026-06-01

First stable release. The PhiSQL language, the redaction policy schema, and the `ai.philterd:phisql` reference jar are all versioned at 1.0.

### Added

- **First stable release of PhiSQL.** The v1.0 grammar and semantics are frozen; conforming implementations may now claim conformance to v1.0.
- **The canonical redaction policy schema (`schema/1.0.0/schema.json`) now lives in this repository** as the source of truth that PhiSQL compiles to and Phileas executes against.
- **Schema bundled in the reference jar.** The build packages `schema/<version>/schema.json` as a JAR resource — the version selected by the `redaction.policy.schema.version` Maven property — and exposes it through the `ai.philterd.phisql.PolicySchema` API (`getSupportedSchemaVersion()`, `getSchema()`), so dependents read the schema without checking out this repository.
- **Maven Central publishing** configured for `ai.philterd:phisql`: attached sources and javadoc jars, GPG signing via the `sign` profile, and the Sonatype Central portal.
- **Full schema coverage.** PhiSQL now exposes every identifier type, strategy, and top-level policy block in the schema except `PERSON` (deferred while the Phileas `pheyes` configuration surface settles). The new constructs:
  - **`RELATIVE`** date strategy (DATE entities only), alongside the existing `SHIFT` and `TRUNCATE_TO_YEAR`. Example `21-date-relative`.
  - **`DEFINE DICTIONARY '<classification>' TERMS ('a', 'b') [FUZZY [SENSITIVITY <auto|off|low|medium|high>]] [CAPITALIZED] WITH <strategy>`** — custom term-list filters, compiling to `identifiers.dictionaries[]`. Example `22-custom-dictionary`.
  - **`DEFINE SECTION START '<regex>' END '<regex>' WITH <strategy>`** — redact a block bounded by start/end patterns, compiling to `identifiers.sections[]`. Example `23-section-redaction`.
  - **`CONFIGURE SPLITTING | PDF | POSTFILTERS | ANALYSIS ( key = value, ... )`** — the global `config` blocks, with the value's JSON type inferred from the literal. Example `24-config-settings`.
  - **`CONFIGURE GRAPHICAL BOX ( x = ..., y = ..., w = ..., h = ..., [page = ...], [color = '...'] )`** — fixed bounding boxes for image/PDF redaction, compiling to `graphical.boundingBoxes[]`. Example `25-graphical-boundingbox`.
- **Field-level completeness.** Every leaf property of every filter, strategy, and config object — scalar, array, or nested object — is now expressible:
  - **`OPTIONS ( key = value, ... )`** — an optional trailing clause on `REDACT`, `DEIDENTIFY`, `DEFINE IDENTIFIER/DICTIONARY/SECTION`, `DETECT PHEYE`, and scope-less `IGNORE` that sets arbitrary leaf properties on the filter object the statement produces (`priority`, `windowSize`, `enabled`, `ignoredFiles`, entity-specific validation flags like `onlyValidCreditCardNumbers`, etc.). Example `26-filter-options`.
  - **Recursive setting values** — a setting value may be a scalar, a nested object `( k = v, ... )`, or an array `[ ... ]`, so any schema structure is expressible, including arrays of objects (`ignoredPatterns`), map objects (`thresholds`), and nested config (`phEyeConfiguration`). A key that collides with a reserved word is quoted (e.g. `'pattern'`). Example `28-nested-options`.
  - **Strategy argument passthrough** — a strategy argument the catalog does not list is no longer rejected; it passes through to the Phileas JSON by its schema property name, so any strategy field (`salt`, `condition`, `truncateDirection`, `anonymizationCandidates`, `futureDates`, ...) is settable. Catalogued arguments are still validated and aliased. Example `27-strategy-params`.
- **Coverage checks** in `scripts/validate_spec.py`: check 5 asserts the reverse of check 2 at the type/strategy/block level, and check 6 descends to every individual leaf property of every policy-bearing object. Each schema field must be exposed by PhiSQL or recorded as a deliberate, reasoned deferral; the build fails if the schema gains a feature PhiSQL neither exposes nor defers, and stale deferrals are flagged.
- `CONFIGURE CRYPTO KEY FROM ENV '<name>'` and `CONFIGURE FPE KEY FROM ENV '<name>' TWEAK FROM ENV '<name>'` statements for supplying the policy-level secrets required by the `ENCRYPT` (`CRYPTO_REPLACE`) and `FPE_ENCRYPT` (`FPE_ENCRYPT_REPLACE`) strategies, which previously had no way to be configured in PhiSQL. Secrets are referenced by environment-variable name only — never inlined — and compile to the Phileas `crypto`/`fpe` blocks using the `env:` prefix (e.g. `"crypto": { "key": "env:CRYPTO_KEY" }`). Example `20-crypto-encryption`.
- **Discovery query verbs.** Three scan verbs and one query verb were added to the grammar:
  - `FIND PII IN '<uri>' [WHERE <predicate>]`
  - `DISCOVER ENTITIES IN '<uri>' [WHERE <predicate>]`
  - `SCAN IN '<uri>' [WHERE <predicate>]`
  - `SELECT <projection> FROM <findings-ref> [WHERE ...] [GROUP BY ...] [LIMIT n]`
  These compile to a separate discovery-query JSON shape (not Phileas JSON). Conforming discovery engines such as Phinder consume the discovery-query JSON.
- **`IN '<uri>'` clause** in discovery statements, accepting URIs from the schemes declared in `spec/v1.0/catalog/sources.yaml` (S3, GCS, Azure Blob, local filesystem, PostgreSQL, MySQL, Snowflake, BigQuery).
- **Discovery WHERE predicates** over finding-row columns. Supported forms: `<column> IN ('a', 'b')`, `<column> <op> <literal>`, and `AND`/`OR`/parenthesization.
- **SELECT projection surface**: column references, `*`, and aggregates (`COUNT`, `AVG`, `SUM`, `MIN`, `MAX`).
- **`spec/v1.0/catalog/findings.yaml`** documenting the canonical findings table schema (columns, types, filterable subset, groupable subset). Sets `phinder` as the default namespace for the unqualified `findings` reference.
- **`spec/v1.0/catalog/sources.yaml`** listing the URI schemes recognized in the `IN` clause. Engines that do not support a scheme must reject statements with a clear error rather than silently no-op.
- **Reserved keywords** added: `FIND`, `PII`, `DISCOVER`, `ENTITIES`, `SCAN`, `IN`, `SELECT`, `FROM`, `BY`, `LIMIT`, `COUNT`, `AVG`, `SUM`, `MIN`, `MAX`. These reservations ship as part of the frozen 1.0.0 surface.
- **Five discovery examples** under `spec/v1.0/examples/` covering S3, GCS, Azure Blob, local filesystem, and a `SELECT ... GROUP BY` over the findings store (`15-find-pii-s3`, `16-discover-entities-gcs`, `17-scan-azure-blob`, `18-find-pii-local-filesystem`, `19-select-findings-groupby`).
- **`columnRef` accepts `CONFIDENCE`** in addition to `ID`, because `CONFIDENCE` is reserved by the redaction predicate but is a valid findings-table column.
- **Validator check** added: `scripts/validate_spec.py` now walks discovery example JSONs and verifies every column referenced resolves against `findings.yaml`. Catalog well-formedness covers `findings.yaml` and `sources.yaml`.

### Changed

- `CompilerTest` parses every `.phisql` under `spec/v1.0/examples/` but compiles only the redaction subset. The five discovery examples are listed in `DISCOVERY_EXAMPLES_NOT_YET_COMPILED` and skipped explicitly. A discovery compiler will land in a follow-up; the set shrinks as it ships.
- `ExamplesParseTest` parses all 20 examples (15 redaction + 5 discovery).

### Notes

- The RFC process described in `CONTRIBUTING.md` was intentionally skipped for the discovery additions while the project is still finding its shape. Substantial future grammar changes are expected to go through an RFC.

### Added (earlier 1.0.0 development)

- Date-shifting strategies `SHIFT` and `TRUNCATE_TO_YEAR` (DATE entities only). `SHIFT` accepts `days`, `months`, `years`, and `random` arguments, mapping to `shiftDays`/`shiftMonths`/`shiftYears`/`shiftRandom` on the Phileas `dateFilterStrategy`. Example `12-date-shift`.
- `DEFINE IDENTIFIER '<classification>' MATCHING '<regex>' [GROUP n] [CASE SENSITIVE | CASE INSENSITIVE] WITH <strategy>` statement for declaring custom regex identifiers inline (previously only referenceable via `IDENTIFIER('name')`, with no way to supply a pattern). Compiles to an entry in the Phileas `identifiers.identifiers` array. Example `13-custom-identifier`.
- `DETECT PHEYE [LABELS (...)] [ENDPOINT '<url>'] WITH <strategy>` statement for AI/NER detection via PhEye. Compiles to an entry in the Phileas `identifiers.pheyes` array with `phEyeFilterStrategies` and an optional `phEyeConfiguration` (`labels`, `endpoint`). This is the supported way to redact `PERSON` (which the catalog defers as a bare entity because it requires a PhEye block). Example `14-pheye-person-detection`.
- Catalog field `phileas_strategy_def` on strategy entries, declaring which Phileas schema `$def` a strategy validates against (defaults to `baseFilterStrategy`; date-only strategies use `dateFilterStrategy`). `scripts/validate_spec.py` now resolves each strategy against its declared def so date-specific strategies and arguments validate correctly.

- Reference parser implementation under `reference/` (Java, ANTLR4). The parser is generated from `spec/v1.0/grammar/PhiSQL.g4` at build time. The `ExamplesParseTest` parses every `.phisql` example file as part of the test suite; any grammar/example drift fails the build.
- Reference compiler that translates parsed PhiSQL into Phileas JSON. The compiler is driven by the catalog YAML files (`spec/v1.0/catalog/*.yaml`), which are bundled inside the JAR as resources. `CompilerTest` compiles every example `.phisql` file and asserts byte-equivalent JSON output against the corresponding `.json` file. `CompileErrorTest` covers compile-time error cases (unknown entity, unknown strategy argument, invalid enum value).
- Five additional spec examples (06-10) exercising multi-strategy entities, format-preserving encryption, multiple confidence bands, policy-wide ignore patterns, and named strategy arguments. The compiler test suite now covers 10 representative policies, matching the round-trip-coverage criterion.
- `spec/v1.0/catalog/policy.yaml` defining the relationship between PhiSQL `POLICY` declarations and Phileas filenames: the filename basename is canonical, `POLICY` is optional, and when present the declared name must match the basename after hyphen/underscore normalization.
- Compiler overloads accepting a filename or an explicit expected name: `Compiler.compile(Path)`, `Compiler.compile(String, String expectedName)`, and `Compiler.compile(DocumentContext, String expectedName)`. `PolicyNamingTest` covers all paths through the new rule.
- Spec example `11-policy-wide-ignore-terms` covering scope-less `IGNORE TERMS`.
- Full Apache 2.0 license headers on every Java file.
- `.github/workflows/reference.yml` to build and test the reference implementation.
- RFC process and contribution guidelines: `CONTRIBUTING.md` at the repo root, `.github/RFC_TEMPLATE.md` for new proposals, and `rfcs/` directory for the historical record.
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
