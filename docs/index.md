# PhiSQL Specification

PhiSQL is the declarative query language for PII privacy operations across the
[Philterd](https://philterd.ai) toolkit. This site is the canonical, versioned
reference for the PhiSQL specification.

A PhiSQL document is a sequence of statements that compile to a
[Phileas redaction policy](https://philterd.ai/schemas/redaction-policy/1.0.0/schema.json):

```sql
POLICY ssn_only;

REDACT SSN WITH MASK;
```

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

## How this site is built

The spec is a set of **machine-readable artifacts** — the
[grammar](reference/grammar.md), the catalog YAML files, and the
[worked examples](examples/index.md). There is no separate prose spec
document; the artifacts are the spec. Every page under **Reference** and
**Examples** is generated directly from those artifacts, so the published
reference cannot drift from the catalogs it describes.

## Where to start

- **[Grammar](reference/grammar.md)** — the full EBNF and production rules.
- **[Verbs](reference/verbs.md)** — the statements: `REDACT`, `DEIDENTIFY`,
  `IGNORE`, `DEFINE`, `DETECT`, and the discovery verbs.
- **[Clauses](reference/clauses.md)** — `WITH`, `WHERE`, `OPTIONS`, `IN`,
  `GROUP BY`, `LIMIT`.
- **[Type system](reference/type-system.md)** — entity types, strategies,
  predicates, and literal value types.
- **[Examples](examples/index.md)** — every worked example, paired with the
  policy JSON it compiles to.

## Status

PhiSQL **v1.0 is stable**. The grammar and semantics of the v1.0 surface are
frozen. Subsequent changes follow the
[versioning policy](https://github.com/philterd/phisql/blob/main/CONTRIBUTING.md#versioning-policy):
additive features land in minor versions, breaking changes require a new major
version. Use the version selector in the header to view other releases of this
spec.

## Repository

The spec, reference implementation, and these docs live in
[philterd/phisql](https://github.com/philterd/phisql). Feedback is welcome via
[GitHub issues](https://github.com/philterd/phisql/issues).
