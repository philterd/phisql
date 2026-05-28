# PhiSQL Specification

**Version:** v0.1 (DRAFT)
**Status:** Draft. Subject to change before v1.0.
**Scope:** Redaction subset.

> [!IMPORTANT]
> This is a **draft** specification. The grammar and semantics may change before v1.0 is published. Implementations may track the draft but **must not** claim conformance until v1.0.

## Table of contents

1. [Introduction](#1-introduction)
2. [Relationship to the Phileas policy schema](#2-relationship-to-the-phileas-policy-schema)
3. [Document structure](#3-document-structure)
4. [Lexical structure](#4-lexical-structure)
5. [Grammar](#5-grammar)
6. [Entity types](#6-entity-types)
7. [Filter strategies](#7-filter-strategies)
8. [Statements](#8-statements)
9. [Worked examples](#9-worked-examples)
10. [Appendix A: PhiSQL to Phileas JSON mapping](#appendix-a-phisql-to-phileas-json-mapping)
11. [Appendix B: Reserved keywords](#appendix-b-reserved-keywords)

---

## 1. Introduction

PhiSQL is a declarative SQL-like language for expressing redaction policies. The v0.1 draft covers the **redaction subset**: a single statement describes which entity types to detect, which strategies to apply to each, and under what conditions.

The motivation is operational consistency. Today, the same conceptual operation (redact SSNs as MASK) is expressed with different surfaces by different tools. PhiSQL unifies authoring across the Philterd toolkit while leaving the existing runtime contracts unchanged.

Discovery, monitoring, benchmarking, and cross-tool join verbs are scoped for later drafts.

## 2. Relationship to the Phileas policy schema

The [Phileas JSON policy schema](https://github.com/philterd/phileas/blob/main/policy-schema/redaction-policy-schema.json) is the **canonical execution contract** for redaction. PhiSQL is a **convenience authoring layer** that compiles to it.

```
PhiSQL source  →  Compiler  →  Phileas JSON policy  →  Phileas runtime
```

The v0.1 governance posture:

- **Phileas JSON leads; PhiSQL follows.** Anything PhiSQL can express must be representable as Phileas JSON. The compilation step is deterministic and lossless.
- **The runtime does not change.** Phileas continues to execute against the JSON schema it already understands. PhiSQL adoption requires no engine work.
- **The policy library stays in JSON.** [`philterd/pii-redaction-policies`](https://github.com/philterd/pii-redaction-policies) remains the source of truth for distributable policies. PhiSQL examples are added alongside, not as replacements.
- **No proprietary extensions.** PhiSQL must not introduce constructs that have no Phileas JSON equivalent. If a use case needs something the JSON schema cannot express, the JSON schema extension comes first; the PhiSQL surface for it follows.
- **Backward compatible forever.** Existing JSON policies remain canonical. There is no migration; PhiSQL is additive.

A future PhiSQL major version may revisit whether PhiSQL should become canonical (with JSON as an internal compilation artifact), but that decision is explicitly out of scope until PhiSQL has proven itself across multiple products.

### 2.1 Policy metadata

The Phileas JSON policy schema does **not** include top-level `name` or `description` fields. Policy identity is derived from the **filename** of the JSON policy (e.g., `hipaa-safe-harbor.json` is the `hipaa_safe_harbor` policy). Human-readable description and provenance live in a sibling Markdown file (e.g., `hipaa-safe-harbor.md`).

PhiSQL `POLICY` and `DESCRIPTION` clauses therefore have **non-JSON destinations**:

| PhiSQL | Destination |
|---|---|
| `POLICY <name>` | Output filename: `<name>.json` |
| `DESCRIPTION '<text>'` | Sibling Markdown file: `<name>.md` |

The PhiSQL compiler emits both files when invoked from the command line. Implementations may also emit only the JSON, in which case metadata is preserved in compiler diagnostics rather than written to disk.

## 3. Document structure

A PhiSQL document is a sequence of one or more **statements** separated by semicolons. Each statement compiles to a complete Phileas policy or to a fragment that merges into a named policy.

Statement-level constructs in v0.1:

- `POLICY` declarations (named policy headers).
- `REDACT` statements (per-entity redaction rules).
- `DEIDENTIFY` statements (multi-entity convenience form).
- `IGNORE` statements (terms and patterns to skip).

## 4. Lexical structure

### 4.1 Comments

```
-- Single-line comment.

/* Multi-line
   comment. */
```

### 4.2 Identifiers

Identifiers match the regex `[A-Za-z_][A-Za-z0-9_]*`. They are case-insensitive for **keywords** and **entity type names**, and case-sensitive for **user-defined names** (policy names, dictionary names).

### 4.3 String literals

Single-quoted strings are the canonical form: `'healthcare'`. Backslash escapes for embedded quotes and newlines: `'don\'t'`, `'line1\nline2'`.

### 4.4 Numeric literals

Decimal integers and floats. No scientific notation in v0.1.

### 4.5 Whitespace

Whitespace is significant only as a token separator.

## 5. Grammar

The grammar is presented in EBNF. Terminals are lowercase or quoted; nonterminals are PascalCase.

```ebnf
Document        = { Statement ";" } ;

Statement       = PolicyDecl
                | RedactStmt
                | DeidentifyStmt
                | IgnoreStmt ;

PolicyDecl      = "POLICY" Identifier
                  [ "DESCRIPTION" StringLiteral ] ;

RedactStmt      = "REDACT" EntityList
                  [ "WITH" StrategyExpr ]
                  [ "WHERE" Predicate ] ;

DeidentifyStmt  = "DEIDENTIFY"
                  EntityAssignment { "," EntityAssignment } ;

EntityAssignment = EntityType "AS" StrategyExpr ;

IgnoreStmt      = "IGNORE"
                  ( "TERMS" StringList | "PATTERN" StringLiteral )
                  [ "FOR" EntityList ] ;

EntityList      = EntityType { "," EntityType } ;

EntityType      = SimpleEntityType | CustomIdentifier ;

SimpleEntityType = Identifier ;  -- see section 6

CustomIdentifier = "IDENTIFIER" "(" StringLiteral ")" ;

StrategyExpr    = StrategyName [ "(" StrategyArgs ")" ] ;

StrategyName    = "MASK" | "REDACT" | "ENCRYPT" | "FPE_ENCRYPT"
                | "HASH_SHA256" | "RANDOM_REPLACE" | "STATIC_REPLACE"
                | "LAST_4" | "TRUNCATE" | "ABBREVIATE" ;

StrategyArgs    = NamedArg { "," NamedArg } ;

NamedArg        = Identifier "=" Literal ;

Predicate       = ConfidenceExpr | LogicalExpr ;

ConfidenceExpr  = "CONFIDENCE" CompareOp NumericLiteral ;

CompareOp       = ">" | ">=" | "<" | "<=" | "=" ;

LogicalExpr     = Predicate ( "AND" | "OR" ) Predicate
                | "(" Predicate ")" ;

StringList      = "(" StringLiteral { "," StringLiteral } ")" ;

Literal         = StringLiteral | NumericLiteral | BooleanLiteral ;
```

## 6. Entity types

Entity type identifiers map one-to-one to non-deprecated identifier fields in the Phileas schema's `$defs.identifiers.properties`:

| PhiSQL | Phileas JSON field | Strategies field |
|---|---|---|
| `AGE` | `age` | `ageFilterStrategies` |
| `BANK_ROUTING_NUMBER` | `bankRoutingNumber` | `bankRoutingNumberFilterStrategies` |
| `BITCOIN_ADDRESS` | `bitcoinAddress` | `bitcoinAddressFilterStrategies` |
| `CITY` | `city` | `cityFilterStrategies` |
| `COUNTY` | `county` | `countyFilterStrategies` |
| `CREDIT_CARD` | `creditCard` | `creditCardFilterStrategies` |
| `CURRENCY` | `currency` | `currencyFilterStrategies` |
| `DATE` | `date` | `dateFilterStrategies` |
| `DRIVERS_LICENSE` | `driversLicense` | `driversLicenseFilterStrategies` |
| `EMAIL_ADDRESS` | `emailAddress` | `emailAddressFilterStrategies` |
| `FIRST_NAME` | `firstName` | `firstNameFilterStrategies` |
| `HOSPITAL` | `hospital` | `hospitalFilterStrategies` |
| `IBAN_CODE` | `ibanCode` | `ibanCodeFilterStrategies` |
| `IP_ADDRESS` | `ipAddress` | `ipAddressFilterStrategies` |
| `MAC_ADDRESS` | `macAddress` | `macAddressFilterStrategies` |
| `MEDICAL_CONDITION` | `medicalCondition` | `medicalConditionFilterStrategies` |
| `PASSPORT_NUMBER` | `passportNumber` | `passportNumberFilterStrategies` |
| `PHONE_NUMBER` | `phoneNumber` | `phoneNumberFilterStrategies` |
| `PHONE_NUMBER_EXTENSION` | `phoneNumberExtension` | `phoneNumberExtensionFilterStrategies` |
| `PHYSICIAN_NAME` | `physicianName` | `physicianNameFilterStrategies` |
| `SSN` | `ssn` | `ssnFilterStrategies` |
| `STATE` | `state` | `stateFilterStrategies` |
| `STATE_ABBREVIATION` | `stateAbbreviation` | `stateAbbreviationFilterStrategies` |
| `STREET_ADDRESS` | `streetAddress` | `streetAddressFilterStrategies` |
| `SURNAME` | `surname` | `surnameFilterStrategies` |
| `TRACKING_NUMBER` | `trackingNumber` | `trackingNumberFilterStrategies` |
| `URL` | `url` | `urlFilterStrategies` |
| `VIN` | `vin` | `vinFilterStrategies` |
| `ZIP_CODE` | `zipCode` | `zipCodeFilterStrategy` (singular, accepts array) |

Custom identifier sets are referenced by classification name:

| PhiSQL | Phileas JSON destination |
|---|---|
| `IDENTIFIER('mrn')` | Appends to `identifiers.identifiers[]` with `classification: "mrn"` |

### 6.1 Entity types not yet in v0.1

- **`PERSON`** is deprecated in the Phileas schema (use the `pheyes` block with PhEye labels). PhiSQL v0.1 does not include `PERSON`; use `FIRST_NAME`, `SURNAME`, and/or `PHYSICIAN_NAME` instead. A future PhiSQL version will add a PhEye-backed `PERSON` mapping once the PhEye lens configuration surface is settled.
- **Section detection (`sections`)**, **graphical filters (`graphical`)**, and **dictionaries (`dictionaries`)** beyond simple ignore lists are not in v0.1.

## 7. Filter strategies

Strategy names map one-to-one to the Phileas `baseFilterStrategy.strategy` enum:

| PhiSQL | Phileas `strategy` value |
|---|---|
| `REDACT` | `REDACT` |
| `RANDOM_REPLACE` | `RANDOM_REPLACE` |
| `STATIC_REPLACE` | `STATIC_REPLACE` |
| `ENCRYPT` | `CRYPTO_REPLACE` |
| `FPE_ENCRYPT` | `FPE_ENCRYPT_REPLACE` |
| `HASH_SHA256` | `HASH_SHA256_REPLACE` |
| `LAST_4` | `LAST_4` |
| `MASK` | `MASK` |
| `TRUNCATE` | `TRUNCATE` |
| `ABBREVIATE` | `ABBREVIATE` |

### 7.1 Strategy arguments

Common named arguments and their Phileas JSON destinations on `baseFilterStrategy`:

| PhiSQL arg | Phileas field | Example |
|---|---|---|
| `format=` | `redactionFormat` | `MASK(format='{{{REDACTED-%t}}}')` |
| `scope=` | `replacementScope` (`DOCUMENT` or `CONTEXT`) | `STATIC_REPLACE(value='X', scope=document)` |
| `value=` | `staticReplacement` | `STATIC_REPLACE(value='X')` |
| `mask_char=` | `maskCharacter` | `MASK(mask_char='*')` |
| `mask_length=` | `maskLength` | `MASK(mask_length=5)` |

Strategy arguments are optional. Omitting them compiles to Phileas defaults.

## 8. Statements

### 8.1 POLICY

Declares the policy's filename and (optionally) the description that goes into the sibling Markdown file. See [Policy metadata](#21-policy-metadata) for how these compile.

```sql
POLICY hipaa_safe_harbor
  DESCRIPTION 'HIPAA Safe Harbor de-identification (45 CFR 164.514(b)(2)).';
```

### 8.2 REDACT

Declares one or more entity types to detect and a strategy to apply.

```sql
REDACT SSN WITH MASK;

REDACT EMAIL_ADDRESS, PHONE_NUMBER WITH REDACT;

REDACT CREDIT_CARD WITH LAST_4 WHERE CONFIDENCE > 0.85;
```

Each entity type compiles to the corresponding identifier field in Phileas JSON, with the strategy appearing in the entity's strategies array.

### 8.3 DEIDENTIFY

A convenience form for declaring multiple entity types with distinct strategies in a single statement.

```sql
DEIDENTIFY
  SSN            AS LAST_4,
  DATE           AS TRUNCATE,
  EMAIL_ADDRESS  AS REDACT;
```

Equivalent to three `REDACT` statements with the same entity-to-strategy mappings.

### 8.4 IGNORE

Adds terms or patterns to the policy's ignore lists.

```sql
IGNORE TERMS ('Acme Corp', 'TestUser') FOR FIRST_NAME;

IGNORE PATTERN '\b[A-Z]{2}\d{4}\b';
```

`IGNORE TERMS ... FOR <entity>` compiles to the matching entity's `ignored` array. `IGNORE PATTERN` without a `FOR` clause compiles to the top-level `ignoredPatterns` array. `IGNORE PATTERN ... FOR <entity>` compiles to the entity's `ignoredPatterns` array.

## 9. Worked examples

Each example shows the PhiSQL source and the resulting Phileas JSON. The examples in this section are also available as files under [`spec/v0.1/examples/`](examples/) and are validated against the Phileas policy schema as part of the spec's CI.

### 9.1 Minimal: redact SSNs

**PhiSQL:** [`examples/01-ssn-only.phisql`](examples/01-ssn-only.phisql)

```sql
POLICY ssn_only;
REDACT SSN WITH MASK;
```

**Phileas JSON:** [`examples/01-ssn-only.json`](examples/01-ssn-only.json)

```json
{
  "identifiers": {
    "ssn": {
      "ssnFilterStrategies": [
        { "strategy": "MASK" }
      ]
    }
  }
}
```

### 9.2 HIPAA Safe Harbor (subset)

**PhiSQL:** [`examples/02-hipaa-safe-harbor.phisql`](examples/02-hipaa-safe-harbor.phisql)

```sql
POLICY hipaa_safe_harbor
  DESCRIPTION 'HIPAA Safe Harbor de-identification (45 CFR 164.514(b)(2)).';

DEIDENTIFY
  PHYSICIAN_NAME  AS RANDOM_REPLACE,
  HOSPITAL        AS RANDOM_REPLACE,
  DATE            AS TRUNCATE,
  AGE             AS REDACT,
  SSN             AS REDACT,
  PHONE_NUMBER    AS REDACT,
  EMAIL_ADDRESS   AS REDACT,
  STREET_ADDRESS  AS REDACT,
  CITY            AS REDACT,
  STATE           AS REDACT,
  ZIP_CODE        AS REDACT;
```

### 9.3 PCI DSS scope reduction

**PhiSQL:** [`examples/03-pci-dss-scope-reduction.phisql`](examples/03-pci-dss-scope-reduction.phisql)

```sql
POLICY pci_dss_scope_reduction
  DESCRIPTION 'PCI DSS v4.0 Req 3.2-3.4: PAN to last 4, full CVV redaction.';

REDACT CREDIT_CARD WITH LAST_4 WHERE CONFIDENCE > 0.85;
```

### 9.4 FRBP 9037 bankruptcy filings

**PhiSQL:** [`examples/04-frbp-9037.phisql`](examples/04-frbp-9037.phisql)

```sql
POLICY frbp_9037
  DESCRIPTION 'FRBP 9037: SSN to last 4, dates to year only, accounts to last 4.';

DEIDENTIFY
  SSN     AS LAST_4,
  DATE    AS TRUNCATE,
  SURNAME AS ABBREVIATE;

REDACT IDENTIFIER('account_number') WITH LAST_4;
```

### 9.5 Multi-strategy with ignore list

**PhiSQL:** [`examples/05-support-tickets-with-allowlist.phisql`](examples/05-support-tickets-with-allowlist.phisql)

```sql
POLICY support_tickets
  DESCRIPTION 'Customer support ticket redaction with allowlist.';

REDACT FIRST_NAME, SURNAME WITH STATIC_REPLACE(value='Customer', scope=document);
REDACT EMAIL_ADDRESS WITH MASK;
REDACT PHONE_NUMBER WITH MASK;

IGNORE TERMS ('Acme', 'AcmeCorp') FOR FIRST_NAME;
IGNORE TERMS ('Corp', 'Support', 'Engineering') FOR SURNAME;
```

---

## Appendix A: PhiSQL to Phileas JSON mapping

This appendix is the authoritative compilation reference. The reference implementation at [`philterd/phisql`](https://github.com/philterd/phisql) implements every row.

### A.1 Statement-level mapping

| PhiSQL construct | Phileas JSON destination |
|---|---|
| `POLICY <name>` | Output filename `<name>.json` |
| `POLICY <name> DESCRIPTION '<text>'` | Output filename + sibling `<name>.md` |
| `REDACT <entity> WITH <strategy>` | Appends `{strategy: ...}` to `<entity>FilterStrategies` of `identifiers.<entity>` |
| `REDACT <entity> WITH <strategy> WHERE <pred>` | as above, with `conditions` set on the strategy object |
| `DEIDENTIFY <e1> AS <s1>, <e2> AS <s2>, ...` | equivalent to N `REDACT` statements |
| `IGNORE TERMS (...) FOR <entity>` | `identifiers.<entity>.ignored = [...]` |
| `IGNORE PATTERN '<regex>'` | Appends to top-level `ignoredPatterns` |
| `IGNORE PATTERN '<regex>' FOR <entity>` | Appends to `identifiers.<entity>.ignoredPatterns` |
| `REDACT IDENTIFIER('<name>') WITH <strategy>` | Appends an object with `classification: "<name>"` to `identifiers.identifiers[]` |

### A.2 Entity type mapping

See [section 6](#6-entity-types).

### A.3 Strategy name mapping

See [section 7](#7-filter-strategies).

### A.4 Strategy argument mapping

See [section 7.1](#71-strategy-arguments).

### A.5 Predicate mapping

| PhiSQL predicate | Phileas JSON destination |
|---|---|
| `CONFIDENCE > 0.85` | `conditions: "confidence > 0.85"` on the strategy object |
| `CONFIDENCE >= 0.5 AND CONFIDENCE < 0.9` | `conditions: "confidence >= 0.5 and confidence < 0.9"` |

## Appendix B: Reserved keywords

```
ABBREVIATE  AND  AS
CONFIDENCE
DEIDENTIFY  DESCRIPTION
ENCRYPT
FOR  FPE_ENCRYPT
HASH_SHA256
IDENTIFIER  IGNORE
LAST_4
MASK
OR
PATTERN  POLICY
RANDOM_REPLACE  REDACT
STATIC_REPLACE
TERMS  TRUNCATE
WHERE  WITH
```

Entity type identifiers from [section 6](#6-entity-types) are also reserved when used as the operand of a redaction statement.

---

## Change log

| Version | Date | Notes |
|---|---|---|
| v0.1 | 2026-05-28 | Initial draft. Redaction subset only. |
