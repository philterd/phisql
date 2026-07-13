# Release Notes

All notable changes to the PhiSQL specification are documented here: the language, grammar, redaction policy schema, catalog, examples, and conformance suite. Release notes for the reference implementations live alongside each one, under `reference/<language>/`.

As of v1.0.0 this project follows [Semantic Versioning](https://semver.org/): additive, backward-compatible changes bump the minor version, and changes that break existing PhiSQL or Phileas JSON require a new major version.

## [1.3.0] - unreleased

> This version is in development. Changes will be listed here as they land.

## [1.2.0] - 2026-07-13

Overlapping split chunks. A splitting policy can now share a window of characters between adjacent chunks so an entity that straddles a chunk boundary is still detected instead of being missed by both chunks. Additive and backward-compatible: every 1.1.0 policy and compiled Phileas JSON remains valid and unchanged in meaning, and the default `overlap` of `0` preserves the existing non-overlapping behavior.

### Added

- **`overlap` on `config.splitting`** (RFC #19). Optional integer (characters, default `0`) in schema `1.2.0`: each split chunk includes the trailing `overlap` characters of the previous one, so an entity straddling a chunk boundary is still detected. Set via `CONFIGURE SPLITTING (... overlap = 200)`. Example `splitting-overlap`.
- **`id` on filters** (RFC #18). Optional non-PII `string` on the shared filter base (`abstractFilterProperties`), so any filter can be named in logs and diagnostics without printing content. Opaque to redaction. Set via `OPTIONS (id = '...')`. Example `component-ids`.
- **`spanDisambiguation` on `config.analysis`** (RFC #20). Optional boolean (default `true`); set `false` to skip span disambiguation (the context-vector step resolving ambiguous spans such as SSN vs. phone) for lower per-document cost. Set via `CONFIGURE ANALYSIS (spanDisambiguation = FALSE)`. Example `span-disambiguation`.
- **`region` on the phone number filter** (RFC #22). Optional ISO 3166-1 alpha-2 string or array (default `"US"`) on `filterPhoneNumber`, giving the default region(s) for phone numbers written without a `"+"` country code. Set via `OPTIONS (region = 'GB')` or `OPTIONS (region = ['US', 'GB'])`. Example `phone-region`.
- **Strategy `id` is now a plain label** (RFC #18). The existing `id` on `baseFilterStrategy` and `dateFilterStrategy` is redefined from an auto-generated UUID (`format: uuid` dropped) to an optional operator-assigned non-PII label. Still a `string`; output unchanged.
- **`MAP_REPLACE` strategy** (RFC #30). Replaces a detected value with one from a lookup table (`mappings` inline and/or `mappingFiles`) for consistent pseudonyms; a value not in the table falls to an optional `generator` then `fallbackStrategy` (default `REDACT`), so nothing is left in the clear. Added to the `strategy` enum with a `MAP_REPLACE` keyword. Usage: `WITH MAP_REPLACE(mappings = ('Smith' = 'Jones'), fallbackStrategy = 'REDACT')`. Example `map-replace`.
- **Top-level `generators` block and `DEFINE GENERATOR` statement** (RFC #30). A named, reusable generator (a local model endpoint, `type: "ollama"`, required `timeoutMs`) referenced by a `MAP_REPLACE` strategy's `generator` argument to replace a value absent from the table. Syntax: `DEFINE GENERATOR '<name>' TYPE '<type>' OPTIONS ( ... )`. Example `generator-fallback`.
- **`color` on filter strategies** (RFC #31). Optional string on `baseFilterStrategy` and `dateFilterStrategy` setting the PDF/image redaction bar color for a strategy's spans; resolves per span to the strategy `color`, then `config.pdf.redactionColor`, then black. Accepts a named color (`black`, `white`, `red`, `orange`, `yellow`, `green`, `blue`, `gray`) or 6-digit `#RRGGBB`; unrecognized values render black. No effect on text redaction. Usage: `WITH REDACT(color = 'red')`. Example `pdf-strategy-color`.
- **`EIN` entity type** (RFC #33). A first-class identifier for the U.S. Employer Identification Number (federal tax ID, `NN-NNNNNNN`). Adds `ein`/`filterEin` to schema `1.2.0` and an `EIN` catalog row, so `REDACT EIN WITH ...` compiles to an `ein` filter. Optional `onlyValidPrefixes` (default `false`) restricts matches to IRS-issued prefixes; set via `OPTIONS (onlyValidPrefixes = TRUE)`. Example `ein`.

### Changed

- **Schema version advances to `1.2.0`.** The three references target it (`redaction.policy.schema.version`, `SUPPORTED_SCHEMA_VERSION`, `PolicySchema.SupportedSchemaVersion`), and `validate_spec.py` and the conformance accept-case check (`compliance/run.py`) validate against it.
- **`namedArg` accepts the `GENERATOR` and `TYPE` keyword tokens** as argument names (in addition to `ID`), so `MAP_REPLACE`'s `generator` and `type` arguments can be written unquoted, e.g. `WITH MAP_REPLACE(generator = 'namer')`.
- **The two existing color fields document the shared color set** (RFC #31). `config.pdf.redactionColor` and `graphical.boundingBoxes[].color` now state the same named-color set, 6-digit hex form, and black fallback as the strategy `color`. Description-only.
- **`STATIC_REPLACE` now enforces its required `value` argument** (RFC #8). `STATIC_REPLACE` without `value` now fails with a semantic error instead of compiling an empty substitution; a conformance correction pinned by `reject/semantic/static-replace-missing-value`.

### Fixed

- **A `WHERE` clause now compiles to `condition` (singular)** (issue #21). The compiler previously emitted `conditions` (plural), which the schema does not define and the Phileas runtimes ignore, so a `WHERE` clause was silently dropped. Fixed across all three references, the catalog, and every affected fixture. (Remaining `OR`/parenthesis gaps tracked in #21.)

### Notes

- **No dedicated clauses.** `overlap`, `spanDisambiguation`, phone `region`, and both filter and strategy `id` have no dedicated PhiSQL syntax; each is set through the generic `CONFIGURE (...)` / `OPTIONS (...)` / strategy-argument passthrough, with value types inferred from the literal.
- **Runtime behavior lives in Phileas**, identically across the Java, Python, and .NET ports. The schema declares intent; these are implemented separately:
  - Chunk overlap: emitting overlapping chunks and de-duplicating spans at the seam.
  - `spanDisambiguation`: disambiguation runs only when the global feature is enabled and the policy has not set it `false`; a policy can turn it off but not force it on.
  - Phone `region`: used as libphonenumber's default region, scanning once per region for the array form. Multiple regions raise false positives, so a leniency option may follow.
  - EIN detection (matching `NN-NNNNNNN`, SSN disambiguation, `onlyValidPrefixes` against the IRS prefix set): philterd/phileas#325, ports philterd/phileas-dotnet#64 and philterd/phileas-python#53.
  - `color` rendering (bar color, named-set/hex to RGB, black fallback; shared with `config.pdf.redactionColor` and `graphical.boundingBoxes[].color`): philterd/phileas#324, ports philterd/phileas-dotnet#63 and philterd/phileas-python#52.
  - `MAP_REPLACE` / `generators`: map precedence (inline `mappings` over `mappingFiles`), case handling, generator call, `timeoutMs` and terminal `fallbackStrategy`, treating generator output as untrusted, and caching. The compiler enforces unique generator names (`reject/semantic/duplicate-generator`) but does not validate `endpoint`, `model`, or that a referenced generator exists.
- **Warnings.** Do not place PII in an `id` (the schema does not enforce `id` uniqueness). A generator must target an endpoint inside the deployment boundary; keep secrets out of the policy.

## [1.1.0] - 2026-06-17

Local, on-device inference for `DETECT PHEYE`. A policy can now point PhEye at a local GLiNER model for fully offline redaction, with no remote PhEye service. Additive and backward-compatible: every 1.0.0 policy and compiled Phileas JSON remains valid and unchanged in meaning.

### Added

- **Local GLiNER inference for `DETECT PHEYE`** (RFC #14). A new optional `MODEL '<path>'` clause points PhEye at a local GLiNER model directory (the ONNX model, the SentencePiece tokenizer, and the GLiNER config) instead of, or in addition to, a remote `ENDPOINT`. When `MODEL` is set, detection runs on-device, and `LABELS` is the GLiNER detection prompt. The target model is the GLiNER-based Philterd PII model exported to ONNX. Example `pheye-local-model`.
- **Schema `1.1.0`** (`schema/1.1.0/schema.json`). `phEyeConfiguration` gains two optional properties:
  - `modelPath`: filesystem path to the local GLiNER model directory.
  - `threshold`: minimum span confidence for the local model to return a detection (number, default `0.5`).
- **`MODEL` reserved keyword**, added to the grammar, the EBNF, and `spec/v1.0/catalog/keywords.yaml`.
- **`spec/v1.1.0/examples/pheye-local-model`** example pair (`.phisql` and compiled `.json`).
- **Identifier checksum and structural validation** (RFC #17). The custom `identifier` filter (`filterIdentifier`) gains an optional `validator` property in schema `1.1.0`: a named built-in validator (a `validatorName` string, or `{name, params}`) that a regex match must pass to be kept. This lets a generic regex identifier reject format-valid but checksum-invalid values (a SIN that fails Luhn, a CPF with bad check digits) without a dedicated per-identifier filter and without embedding executable code in a policy.
- **`spec/v1.0/catalog/validators.yaml`**: the source-of-truth catalog for the validator vocabulary (`luhn`, `mod11`, `mod97`, `mod23-letter`, `aba`, `verhoeff`, `damm`, `es-cif`, `de-steuerid`, `de-personalausweis`, `bic-structural`). The schema's `validatorName` enum is kept in sync with it.
- **`spec/v1.1.0/examples/identifier-validator`** example pair (`.phisql` and compiled `.json`), showing both the string and `{name, params}` validator forms set through the `OPTIONS(...)` passthrough.
- **`maskLength` accepts a number** (RFC #13). In schema `1.1.0` the `MASK` strategy's `maskLength` is widened from `"string"` to `["string", "integer"]`, matching its own description ("can also be a number for fixed-length masking") and the strategy catalog (`mask_length: integer`). `REDACT SSN WITH MASK(mask_length = 4)` already compiled to `"maskLength": 4`, which silently violated the schema; that output is now valid, unchanged. Backward-compatible (it only relaxes a constraint). The frozen `schema/1.0.0` is left untouched; the fix lands in the current `1.1.0`.

### Changed

- The current schema version advances to `1.1.0`, and the language recognizes the `MODEL` clause.
- The `validators.yaml` catalog is added alongside the other catalogs as part of the spec source of truth.
- The conformance runner (`compliance/run.py`) now validates accept-case output against the current schema version (`1.1.0`) rather than the frozen `1.0.0`. The `mask-char-length` case is no longer schema-exempt (RFC #13).
- `validate_spec.py` now cross-checks that each strategy argument's catalog `type` is compatible with the schema `type` of the `phileas_field` it maps to, so a catalog/schema type contradiction (RFC #13, `maskLength`) cannot recur silently.
- **Date-only strategies are now enforced** (RFC #9). `SHIFT`, `TRUNCATE_TO_YEAR`, and `RELATIVE` applied to any target other than the `DATE` entity (another entity, a custom identifier, a dictionary, a section, or PhEye) are a semantic error. This is a conformance correction, not a new feature: the catalog already classifies these as `dateFilterStrategy` ("DATE entities only"); the language was simply lenient. `REDACT SSN WITH SHIFT(days=30)` previously compiled and now fails. Covered by the `reject/semantic/date-only-strategy` conformance case; the matching "Known underspecified areas" note is removed.

### Notes

- `threshold` is schema-only in 1.1: there is no PhiSQL clause for it, so a policy relies on the default or filters detections with `WHERE CONFIDENCE`. Only `MODEL` is expressible in the language.
- The date-only enforcement rejects existing `.phisql` that applied one of these strategies to a non-`DATE` target. Such policies never produced a meaningful redaction (the Phileas runtime would not apply the strategy), so the practical blast radius is small; this is why it lands as a conformance correction in 1.1 rather than a major bump. Existing Phileas JSON policies are unaffected.
- `validator` has no dedicated PhiSQL clause, but like any identifier-filter property it is expressible through the generic `OPTIONS(...)` passthrough, for example `DEFINE IDENTIFIER '...' MATCHING '...' WITH <strategy> OPTIONS (validator = 'luhn')`, which compiles to the `validator` property. A dedicated clause (for example `VALIDATE WITH`) is optional sugar deferred to a later RFC. An unknown validator name is a policy error and must not be silently ignored.

## [1.0.0] - 2026-06-01

First stable release. The PhiSQL language and the redaction policy schema are versioned at 1.0.

### Added

- **First stable release of PhiSQL.** The v1.0 grammar and semantics are frozen; conforming implementations may now claim conformance to v1.0.
- **The canonical redaction policy schema (`schema/1.0.0/schema.json`) now lives in this repository** as the source of truth that PhiSQL compiles to and Phileas executes against.
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

- The five discovery examples are parsed but not yet compiled; a discovery compiler will land in a follow-up, and the set shrinks as it ships.

### Notes

- The RFC process described in `CONTRIBUTING.md` was intentionally skipped for the discovery additions while the project is still finding its shape. Substantial future grammar changes are expected to go through an RFC.

### Added (earlier 1.0.0 development)

- Date-shifting strategies `SHIFT` and `TRUNCATE_TO_YEAR` (DATE entities only). `SHIFT` accepts `days`, `months`, `years`, and `random` arguments, mapping to `shiftDays`/`shiftMonths`/`shiftYears`/`shiftRandom` on the Phileas `dateFilterStrategy`. Example `12-date-shift`.
- `DEFINE IDENTIFIER '<classification>' MATCHING '<regex>' [GROUP n] [CASE SENSITIVE | CASE INSENSITIVE] WITH <strategy>` statement for declaring custom regex identifiers inline (previously only referenceable via `IDENTIFIER('name')`, with no way to supply a pattern). Compiles to an entry in the Phileas `identifiers.identifiers` array. Example `13-custom-identifier`.
- `DETECT PHEYE [LABELS (...)] [ENDPOINT '<url>'] WITH <strategy>` statement for AI/NER detection via PhEye. Compiles to an entry in the Phileas `identifiers.pheyes` array with `phEyeFilterStrategies` and an optional `phEyeConfiguration` (`labels`, `endpoint`). This is the supported way to redact `PERSON` (which the catalog defers as a bare entity because it requires a PhEye block). Example `14-pheye-person-detection`.
- Catalog field `phileas_strategy_def` on strategy entries, declaring which Phileas schema `$def` a strategy validates against (defaults to `baseFilterStrategy`; date-only strategies use `dateFilterStrategy`). `scripts/validate_spec.py` now resolves each strategy against its declared def so date-specific strategies and arguments validate correctly.
- Five additional spec examples (06-10) exercising multi-strategy entities, format-preserving encryption, multiple confidence bands, policy-wide ignore patterns, and named strategy arguments.
- `spec/v1.0/catalog/policy.yaml` defining the relationship between PhiSQL `POLICY` declarations and Phileas filenames: the filename basename is canonical, `POLICY` is optional, and when present the declared name must match the basename after hyphen/underscore normalization.
- Spec example `11-policy-wide-ignore-terms` covering scope-less `IGNORE TERMS`.
- RFC process and contribution guidelines: `CONTRIBUTING.md` at the repo root, `.github/RFC_TEMPLATE.md` for new proposals, and `rfcs/` directory for the historical record.
- RFC 0001 (`rfcs/0001-scope-less-ignore-terms.md`) — worked example RFC documenting the scope-less `IGNORE TERMS` change end to end, for use as a reference by future authors.

### Changed

- Repository renamed from `philterd/phisql-spec` to `philterd/phisql` to reflect that it now contains both the specification and the reference implementations.
- Restructured the v0.1 spec into machine-readable artifacts: ANTLR4 grammar (`PhiSQL.g4`), EBNF grammar (`PhiSQL.ebnf`), and YAML catalog files for entity types, strategies, keywords, and predicates. The previous prose `SPEC.md` has been removed; the artifacts are now the spec.
- The validator (`scripts/validate_spec.py`) now runs three checks on every push and PR: catalog well-formedness, catalog references resolving against the canonical Phileas schema, and example JSON validating against the same schema.
- Grammar: the `literal` production now accepts a bare identifier (`ID`) in addition to string, numeric, and boolean literals. This is required for enum-typed strategy arguments such as `scope=document`. Bare identifiers must correspond to enum values declared in `strategies.yaml` for the relevant argument.

### Fixed

- Scope-less `IGNORE TERMS (...)` (without a `FOR <entity>` clause) now compiles to the top-level `ignored` array in the Phileas schema instead of raising a compile error. The top-level `ignored` array uses the `{terms: [...]}` object shape per `$defs.ignored` in the Phileas schema.
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
