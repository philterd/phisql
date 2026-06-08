---
rfc: 0002
title: Monitoring query verbs over Phield trend and alert data
status: Draft
author: Jeff Zemerick <jzonthemtn>
created: 2026-06-08
target_version: v1.1
versioning_impact: minor
---

# RFC 0002: Monitoring query verbs over Phield trend and alert data

## Motivation

PhiSQL v1.0 ships two query surfaces: the redaction authoring surface (compiles to
Phileas JSON) and the **discovery** query surface (`FIND PII`, `DISCOVER ENTITIES`,
`SCAN`, and `SELECT ... FROM findings`, which compile to a separate discovery-query
JSON shape consumed by Phinder). The README's Status section names the third surface
explicitly as deferred:

> PhiSQL v1.0 is a complete authoring surface for the Phileas redaction policy
> schema. Discovery, **monitoring**, and cross-tool query verbs are scoped for later
> versions.

Phield is the Philterd monitoring tool: it tracks how PII flows through systems over
time and raises alerts when entity-detection rates deviate from their baseline. Today
the only way to ask "how is PII trending through my systems, and where are the
anomalies?" is to query Phield's storage directly through whatever native interface it
exposes — there is no portable, declarative way to express the question. That defeats
the same convenience-authoring goal that motivated the discovery verbs: a Philterd
operator who has learned PhiSQL for redaction and discovery should be able to write
one-line monitoring queries in the same language instead of dropping to a tool-specific
API.

Concretely, an operator wants to write:

```sql
SELECT entity_type, AVG(count_per_minute)
  FROM phield.trends
  WHERE deviation > 2 * stddev
    AND timestamp > NOW() - INTERVAL '1 hour';
```

and have it run against any conforming monitoring engine, exactly as a discovery
`SELECT ... FROM findings` runs against any conforming discovery engine.

**Why this belongs in the spec rather than a higher layer.** The discovery surface
established that cross-tool query verbs are a first-class part of PhiSQL, and it did so
by defining the query shape *in the spec's own catalogs* (`findings.yaml`,
`sources.yaml`) rather than deferring to a library. A library wrapper around Phield's
native API would be Phield-specific and would not give other monitoring engines a
contract to conform to. The portability guarantee — "any conforming engine answers the
same query the same way" — only exists if the grammar, the table schemas, and the
compile target live in the spec.

**Workaround today.** None within PhiSQL. Operators query Phield's native interface
directly, which is non-portable and unavailable to the PhiSQL CLI and other tools that
only speak PhiSQL.

This RFC closes [philterd/philterd-website#123]. It is the direct sibling of
[philterd/philterd-website#122], which the discovery verbs closed; this RFC follows the
same architectural pattern.

## Proposed schema changes

**N/A — no redaction policy schema change.**

Like the discovery verbs, monitoring queries do **not** compile to Phileas JSON and do
not touch the canonical redaction policy schema under `schema/`. They compile to a
separate *monitoring-query JSON* shape (defined below, in the same spirit as the
discovery-query JSON), consumed by a conforming monitoring engine such as Phield. The
README governance posture — "Anything PhiSQL can express must be representable as
Phileas JSON" — applies to the redaction surface; the query surfaces (discovery,
monitoring) are explicitly separate compile targets and are not constrained by the
Phileas schema. No `schema/` edit, no `version`/`$id` bump, and no Phileas runtime
change is required.

## Proposed grammar changes

The v1.0 grammar is frozen, so these additions land in a v1.1 grammar
(`spec/v1.1/grammar/PhiSQL.g4` and `PhiSQL.ebnf` — see the **Unresolved questions**
section on the minor-version directory layout). The additions are strictly additive:
every v1.0 statement continues to parse unchanged.

The discovery `SELECT` form is generalized so that `FROM` can target a monitoring table
in addition to the findings store, and the projection, `WHERE`, and `GROUP BY` surfaces
are extended with the time-range, arithmetic, and time-bucket constructs monitoring
needs. Shown in EBNF (the `.g4` changes mirror these productions):

```ebnf
(* Before — v1.0 discovery SELECT *)
discovery stmt   = ( "FIND" , "PII" , in clause , [ where discovery ] )
                 | ( "DISCOVER" , "ENTITIES" , in clause , [ where discovery ] )
                 | ( "SCAN" , in clause , [ where discovery ] )
                 | ( "SELECT" , projection list , "FROM" , findings ref
                   , [ where discovery ]
                   , [ group by clause ]
                   , [ limit clause ] ) ;

(* After — the SELECT arm targets a generalized table ref *)
discovery stmt   = ( "FIND" , "PII" , in clause , [ where discovery ] )
                 | ( "DISCOVER" , "ENTITIES" , in clause , [ where discovery ] )
                 | ( "SCAN" , in clause , [ where discovery ] )
                 | ( "SELECT" , projection list , "FROM" , table ref
                   , [ where discovery ]
                   , [ group by clause ]
                   , [ limit clause ] ) ;

(* `findings ref` is renamed to `table ref`; the production is unchanged.
   It resolves against the union of findings.yaml (namespace `phinder`) and
   the new monitoring catalog (namespace `phield`). An unqualified name uses
   the catalog-declared default namespace, exactly as `findings` does today. *)
table ref        = [ id , "." ] , id ;   (* phield.trends, phield.alerts, findings *)
```

Projection gains a time-bucket function:

```ebnf
(* Before *)
projection       = "*" | aggregate | column ref ;

(* After *)
projection       = "*" | aggregate | time bucket | column ref ;

time bucket      = "TIME_BUCKET" , "(" , string literal , "," , column ref , ")" ;
```

The `WHERE` predicate RHS is widened from a bare literal to a value expression, and a
`BETWEEN` form is added, so time-range and anomaly predicates are expressible:

```ebnf
(* Before *)
discovery predicate
                 = ( column ref , "IN" , string list )
                 | ( column ref , compare op , ( string literal | numeric literal | boolean literal ) )
                 | ( "(" , discovery predicate , ")" )
                 | ( discovery predicate , ( "AND" | "OR" ) , discovery predicate ) ;

(* After *)
discovery predicate
                 = ( column ref , "IN" , string list )
                 | ( column ref , "BETWEEN" , value expr , "AND" , value expr )
                 | ( column ref , compare op , value expr )
                 | ( "(" , discovery predicate , ")" )
                 | ( discovery predicate , ( "AND" | "OR" ) , discovery predicate ) ;

(* New: arithmetic value expressions, with NOW()/INTERVAL for time math.
   Standard precedence: */ bind tighter than +-. *)
value expr       = term , { ( "+" | "-" ) , term } ;
term             = factor , { ( "*" | "/" ) , factor } ;
factor           = numeric literal
                 | string literal
                 | boolean literal
                 | column ref
                 | now expr
                 | "(" , value expr , ")" ;
now expr         = "NOW" , "(" , ")" ;
interval literal = "INTERVAL" , string literal ;   (* e.g. INTERVAL '1 hour' *)
```

`INTERVAL '<n unit>'` is a `factor` participating in `+`/`-` against a `NOW()` or a
`timestamp` column (`NOW() - INTERVAL '1 hour'`). For clarity the production above lists
it as a named form; in the `.g4` it is an alternative of `factor` guarded so that an
interval may only be added to or subtracted from a timestamp-typed operand — a check the
reference compiler enforces against the column types declared in the monitoring catalog,
rather than the grammar.

`GROUP BY` accepts positional ordinals and time buckets, so the issue's
`GROUP BY 1, 2` and `GROUP BY TIME_BUCKET(...)` both parse:

```ebnf
(* Before *)
group by clause  = "GROUP" , "BY" , column ref , { "," , column ref } ;

(* After *)
group by clause  = "GROUP" , "BY" , group key , { "," , group key } ;
group key        = numeric literal      (* 1-based ordinal into the projection list *)
                 | time bucket
                 | column ref ;
```

**Reserved keywords added:** `NOW`, `INTERVAL`, `BETWEEN`, `TIME_BUCKET`. These are
added to `spec/v1.1/catalog/keywords.yaml`. Following the discovery precedent, the table
and namespace names (`phield`, `trends`, `alerts`) and the column names (`deviation`,
`stddev`, `count_per_minute`, `severity`, …) are **not** reserved — they are validated
against the monitoring catalog in their syntactic positions, exactly as `findings` and
`phinder` are validated against `findings.yaml` rather than reserved.

### New catalog file

A new catalog `spec/v1.1/catalog/monitoring.yaml` declares the two monitoring tables,
mirroring the structure of `findings.yaml` (columns, types, filterable subset, groupable
subset, default namespace). Conforming monitoring engines must surface at least the
`required: true` columns; unknown columns are parse-only/opaque.

```yaml
# PhiSQL v1.1 monitoring table catalog.
#
# Defines the tables, columns, and types that the `SELECT ... FROM phield.<table>`
# form projects, filters, and aggregates over. Conforming monitoring engines
# (e.g., Phield) must surface at least the columns marked `required: true`.
#
# Status: Draft (v1.1).

version: v1.1

default_namespace: phield

tables:
  - name: trends
    namespace: phield
    description: >-
      Time-bucketed PII detection rates with per-bucket baseline statistics,
      one row per (bucket, entity_type, source).
    columns:
      - name: timestamp
        type: timestamp
        required: true
        description: >-
          ISO 8601 UTC start of the time bucket this row summarizes. The target
          column for time-range predicates (`timestamp > NOW() - INTERVAL '1 hour'`,
          `timestamp BETWEEN ... AND ...`) and for `TIME_BUCKET(...)`.
      - name: entity_type
        type: string
        required: true
        description: >-
          Catalog entity type (e.g., SSN, CREDIT_CARD, EMAIL_ADDRESS), from
          entity-types.yaml or a user-defined identifier classification.
      - name: source_uri
        type: string
        required: true
        description: >-
          The monitored source the rate was observed in, using the same URI
          schemes as sources.yaml.
      - name: count_per_minute
        type: number
        required: true
        description: Detections per minute in this bucket for this entity_type/source.
      - name: mean
        type: number
        required: false
        description: Rolling baseline mean of count_per_minute for this series.
      - name: stddev
        type: number
        required: false
        description: Rolling baseline standard deviation of count_per_minute.
      - name: deviation
        type: number
        required: false
        description: >-
          Absolute difference between count_per_minute and `mean`. Combined with
          `stddev` it expresses anomaly predicates such as `deviation > 2 * stddev`.
    filterable_columns: [timestamp, entity_type, source_uri, count_per_minute, deviation, stddev]
    groupable_columns:  [timestamp, entity_type, source_uri]

  - name: alerts
    namespace: phield
    description: >-
      Discrete monitoring alerts raised when a trend breaches a rule, one row
      per alert.
    columns:
      - name: alert_id
        type: string
        required: true
        description: Stable identifier for the alert.
      - name: timestamp
        type: timestamp
        required: true
        description: ISO 8601 UTC time the alert fired.
      - name: entity_type
        type: string
        required: true
        description: Entity type the alert concerns.
      - name: source_uri
        type: string
        required: false
        description: Source the alert concerns, when attributable to one source.
      - name: severity
        type: string
        required: true
        description: >-
          Alert severity. One of `low`, `medium`, `high`, `critical`.
      - name: rule
        type: string
        required: false
        description: Identifier of the monitoring rule that raised the alert.
      - name: message
        type: string
        required: false
        description: Human-readable description of the alert.
    filterable_columns: [timestamp, entity_type, source_uri, severity, rule]
    groupable_columns:  [timestamp, entity_type, source_uri, severity, rule]
```

### Compile target: monitoring-query JSON

`SELECT ... FROM phield.<table>` compiles to a monitoring-query JSON object — a sibling
shape to the discovery-query JSON, **not** Phileas JSON. The shape:

```json
{
  "queryType": "monitoring",
  "table": "phield.trends",
  "projections": [ /* columns, aggregates, time_buckets */ ],
  "filters": { /* predicate tree with time-range and arithmetic operands */ },
  "groupBy": [ /* columns, ordinals, time_buckets */ ],
  "limit": null
}
```

The exact field shapes are specified alongside the examples below and are documented in
`monitoring.yaml` in the same descriptive style the discovery compile contract uses.
Conforming monitoring engines consume this JSON; engines that do not support a referenced
table or column must reject the query with a clear error rather than silently no-op
(same rule sources.yaml applies to unsupported schemes).

## Examples

These land under `spec/v1.1/examples/` and become part of the reference test suite. As
with the v1.0 discovery examples, they are parsed by `ExamplesParseTest` and listed in
the compiler's not-yet-compiled set until the monitoring compiler ships (see **Reference
implementation**).

### Example 1 — anomaly query (trend lookup with time range)

PhiSQL (`spec/v1.1/examples/29-trends-anomaly.phisql`):

```sql
-- Entity types whose detection rate in the last hour deviated more than
-- two standard deviations from baseline.
SELECT entity_type, AVG(count_per_minute)
  FROM phield.trends
  WHERE deviation > 2 * stddev
    AND timestamp > NOW() - INTERVAL '1 hour';
```

Compiled monitoring-query JSON (`spec/v1.1/examples/29-trends-anomaly.json`):

```json
{
  "queryType": "monitoring",
  "table": "phield.trends",
  "projections": [
    { "kind": "column", "name": "entity_type" },
    { "kind": "aggregate", "fn": "AVG", "arg": "count_per_minute" }
  ],
  "filters": {
    "op": "AND",
    "args": [
      {
        "op": ">",
        "left": { "kind": "column", "name": "deviation" },
        "right": {
          "kind": "arith", "op": "*",
          "left": { "kind": "literal", "type": "number", "value": 2 },
          "right": { "kind": "column", "name": "stddev" }
        }
      },
      {
        "op": ">",
        "left": { "kind": "column", "name": "timestamp" },
        "right": {
          "kind": "arith", "op": "-",
          "left": { "kind": "now" },
          "right": { "kind": "interval", "value": "1 hour" }
        }
      }
    ]
  },
  "groupBy": [],
  "limit": null
}
```

### Example 2 — bucketed aggregation over alerts

PhiSQL (`spec/v1.1/examples/30-alerts-time-bucket.phisql`):

```sql
-- High-severity alert counts in five-minute buckets, by entity type.
SELECT entity_type, TIME_BUCKET('5 minutes', timestamp), COUNT(*)
  FROM phield.alerts
  WHERE severity = 'high'
  GROUP BY 1, 2;
```

Compiled monitoring-query JSON (`spec/v1.1/examples/30-alerts-time-bucket.json`):

```json
{
  "queryType": "monitoring",
  "table": "phield.alerts",
  "projections": [
    { "kind": "column", "name": "entity_type" },
    { "kind": "timeBucket", "width": "5 minutes", "column": "timestamp" },
    { "kind": "aggregate", "fn": "COUNT", "arg": "*" }
  ],
  "filters": {
    "op": "=",
    "left": { "kind": "column", "name": "severity" },
    "right": { "kind": "literal", "type": "string", "value": "high" }
  },
  "groupBy": [
    { "kind": "ordinal", "value": 1 },
    { "kind": "ordinal", "value": 2 }
  ],
  "limit": null
}
```

### Example 3 — explicit time-range window (`BETWEEN`)

PhiSQL (`spec/v1.1/examples/31-trends-between.phisql`):

```sql
-- SSN detection rate per source over a fixed window.
SELECT source_uri, AVG(count_per_minute)
  FROM phield.trends
  WHERE entity_type = 'SSN'
    AND timestamp BETWEEN '2026-06-08T00:00:00Z' AND '2026-06-08T06:00:00Z'
  GROUP BY source_uri
  LIMIT 50;
```

Compiled monitoring-query JSON (`spec/v1.1/examples/31-trends-between.json`):

```json
{
  "queryType": "monitoring",
  "table": "phield.trends",
  "projections": [
    { "kind": "column", "name": "source_uri" },
    { "kind": "aggregate", "fn": "AVG", "arg": "count_per_minute" }
  ],
  "filters": {
    "op": "AND",
    "args": [
      {
        "op": "=",
        "left": { "kind": "column", "name": "entity_type" },
        "right": { "kind": "literal", "type": "string", "value": "SSN" }
      },
      {
        "op": "BETWEEN",
        "left": { "kind": "column", "name": "timestamp" },
        "low":  { "kind": "literal", "type": "string", "value": "2026-06-08T00:00:00Z" },
        "high": { "kind": "literal", "type": "string", "value": "2026-06-08T06:00:00Z" }
      }
    ]
  },
  "groupBy": [ { "kind": "column", "name": "source_uri" } ],
  "limit": 50
}
```

## Alternatives considered

**Alternative 1: A dedicated `MONITOR` verb instead of reusing `SELECT`.**
A new top-level statement, e.g. `MONITOR TRENDS WHERE ...` / `MONITOR ALERTS ...`.

Rejected because: the data being queried is tabular (rows of buckets and alerts) and the
operations are exactly projection/filter/aggregate/group — the semantics `SELECT` already
carries. The discovery surface already reads tabular stores with `SELECT ... FROM
findings`; a parallel `SELECT ... FROM phield.trends` keeps one mental model and one set
of clauses (`WHERE`, `GROUP BY`, `LIMIT`) instead of forking a second, near-identical
query dialect. A bespoke `MONITOR` verb would duplicate every clause for no expressive
gain.

**Alternative 2: Reserve `PHIELD`, `TRENDS`, `ALERTS` (and the column names) as keywords.**
Bake the table and column vocabulary into the grammar.

Rejected because: it contradicts the discovery precedent, where `findings`/`phinder` and
all finding columns are catalog-validated identifiers, not reserved words. Reserving them
would (a) make the monitoring vocabulary un-extensible without a grammar change every time
Phield adds a column, and (b) needlessly collide with user-chosen names elsewhere. Keeping
the vocabulary in `monitoring.yaml` lets engines surface additional columns and lets the
spec evolve the table schema without touching the grammar.

**Alternative 3: Push time math to literal strings (no `NOW()`/`INTERVAL` grammar).**
Require operators to compute and inline absolute timestamps, e.g.
`WHERE timestamp > '2026-06-08T13:00:00Z'`, with no relative-time syntax.

Rejected because: the headline user story is "the last hour / the last 5 minutes," which
is inherently relative. Forcing absolute timestamps makes every monitoring query a
two-step ritual (compute the boundary, then paste it) and makes saved queries
non-reusable — a saved "last hour" query would silently mean a fixed past hour. `NOW()`
and `INTERVAL` are the minimal additions that make relative windows first-class. (Absolute
windows remain available via `BETWEEN`, as Example 3 shows.)

**Alternative 4: Add a `STDDEV()` aggregate and express anomalies as `count > AVG + 2*STDDEV(...)`.**
Compute the baseline inside the query instead of reading precomputed `mean`/`stddev`/
`deviation` columns from the trends table.

Rejected because: it conflates two responsibilities. Baseline computation (windowing,
seasonality, smoothing) is the monitoring engine's job and is far richer than a single
aggregate; PhiSQL should *read* the engine's baseline columns, not re-derive them. Exposing
`mean`/`stddev`/`deviation` as columns keeps the query declarative and lets the engine own
the statistics. A `STDDEV()` aggregate can be added later by a separate RFC if a genuine
need appears (see **Future possibilities**).

## Drawbacks

- **Grammar surface area grows meaningfully.** Value expressions (arithmetic with
  precedence), `BETWEEN`, `NOW()`/`INTERVAL`, and `TIME_BUCKET` are the largest single
  expansion of the query surface since discovery. More grammar is more to learn, more to
  implement in conforming parsers, and more to keep consistent between `PhiSQL.g4` and
  `PhiSQL.ebnf`.
- **A second non-Phileas compile target.** Monitoring-query JSON joins discovery-query
  JSON as a shape that PhiSQL emits but Phileas does not consume. Each such target is a
  contract the project must version and document independently of the redaction schema.
- **New downstream obligation.** A monitoring engine must exist and conform for the verbs
  to be more than syntax. Until Phield consumes the monitoring-query JSON, these queries
  parse and compile but have nothing to run against — mirroring the v1.0 state where the
  discovery compiler had not yet landed.
- **Arithmetic invites scope creep.** Once `*`, `+`, `-` are in predicates, users will
  reasonably ask for functions, `CASE`, more aggregates, etc. The RFC deliberately stops
  at the minimum needed for anomaly/time predicates; holding that line will take review
  discipline.

## Backward compatibility

- **Existing `.phisql` files:** All additions are new productions or relaxations
  (widening a literal RHS to a value expression, of which a bare literal is the trivial
  case). Every v1.0 statement — redaction, discovery, and `SELECT ... FROM findings` —
  parses and compiles unchanged. No file in the repository breaks.
- **Existing Phileas JSON / runtime:** Untouched. Monitoring does not compile to Phileas
  JSON and requires no runtime change.
- **Existing downstream consumers:** The discovery-query JSON shape is unchanged. The
  `findings ref` → `table ref` rename is internal to the grammar (same production body)
  and does not change discovery output. New consumers (monitoring engines) opt in by
  implementing the new monitoring-query JSON; existing consumers are unaffected.

This is a strictly-additive change.

## Versioning impact

**Minor.** The change only adds new statements/clauses and relaxes an existing one;
nothing previously accepted is rejected and no existing compile output changes. Per the
[versioning policy](../CONTRIBUTING.md#versioning-policy), additive, backward-compatible
changes bump the minor version — this is the **v1.1** spec release.

## Reference implementation

Not yet implemented; to land in a follow-up PR linked from this RFC, in two parts:

1. **Grammar + catalog + examples (parse-complete).** Add the v1.1 grammar productions,
   `monitoring.yaml`, the new reserved keywords, and the three example `.phisql`/`.json`
   pairs. `ExamplesParseTest` parses all of them; the three monitoring examples join the
   `DISCOVERY_EXAMPLES_NOT_YET_COMPILED`-style skip set in `CompilerTest` until step 2.
   `scripts/validate_spec.py` is extended to walk monitoring example JSONs and verify every
   referenced table/column resolves against `monitoring.yaml`, mirroring the existing
   discovery-column check.
2. **Monitoring compiler.** Implement `SELECT ... FROM phield.<table>` → monitoring-query
   JSON in the reference compiler and remove the three examples from the skip set, so the
   round-trip test asserts byte-equivalent JSON against the checked-in files.

Phield's consumption of the monitoring-query JSON is tracked separately in the Phield
repository and does not block acceptance of this RFC (acceptance requires the worked
examples, which are included above).

## Unresolved questions

- **Minor-version directory layout.** There is no precedent yet for a minor spec version
  in this repo — everything lives under `spec/v1.0/`, and the discovery verbs landed there
  during the 1.0 dev cycle. Should v1.1 additions go in a new `spec/v1.1/` tree (grammar +
  catalogs copied forward and extended), or should the v1.0 grammar be annotated with
  version-gated additions in place? This RFC assumes a new `spec/v1.1/` tree; maintainers
  should confirm the convention, since it affects every future minor version, not just this
  one.
- **`INTERVAL` unit grammar.** This RFC treats the interval body as an opaque string
  (`'1 hour'`, `'5 minutes'`) validated by the engine, matching how `TIME_BUCKET`'s width
  is handled. Should the spec instead enumerate accepted units (`second`/`minute`/`hour`/
  `day`/…) in the catalog and have the compiler validate them, for earlier and more
  portable error messages?
- **Severity as an enum.** `severity` is declared as a free `string` with documented values
  `low|medium|high|critical`. Should the catalog formally constrain it to an enum so the
  compiler rejects `severity = 'urgent'` at compile time rather than deferring to the engine?
- **Default time window.** Should a monitoring `SELECT` with no time predicate be rejected,
  warned, or allowed to scan all of history? Discovery has no equivalent concern; monitoring
  stores can be very large, so an implicit unbounded scan may be a footgun worth disallowing.

## Future possibilities

These are explicitly **out of scope** for this RFC but become reachable once the surface
above exists:

- **A `STDDEV()` (and other statistical) aggregate**, for engines that prefer in-query
  baseline computation over precomputed `mean`/`stddev` columns.
- **`ORDER BY` / `LIMIT n` ranking** to surface "top N noisiest sources," which pairs
  naturally with bucketed aggregation.
- **A streaming/`WATCH` verb** that turns a monitoring `SELECT` into a standing
  subscription rather than a point-in-time query.
- **Cross-surface joins** (correlating `phield.alerts` with `phinder.findings`), the
  "cross-tool query verbs" the README lists alongside monitoring as a later-version goal.

[philterd/philterd-website#123]: https://github.com/philterd/philterd-website/issues/123
[philterd/philterd-website#122]: https://github.com/philterd/philterd-website/issues/122
