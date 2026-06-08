---
rfc: 0004
title: Cross-tool join semantics across the Philterd toolkit
status: Draft
author: Jeff Zemerick <jzonthemtn>
created: 2026-06-08
target_version: v1.2
versioning_impact: minor
---

# RFC 0004: Cross-tool join semantics across the Philterd toolkit

## Motivation

PhiSQL's query surfaces have so far been single-tool: discovery reads Phinder's findings
(v1.0), monitoring reads Phield's trends and alerts ([RFC 0002]), and benchmarking
evaluates policies via Philter Scope ([RFC 0003]). Each answers a question about *one* tool.
The questions that make the Philterd toolkit more than the sum of its parts span *several*
tools at once:

- "Which detected entity types did human reviewers override most often?" — joins Phinder
  findings to Arbiter reviews.
- "Which discovery scans later triggered monitoring anomalies?" — joins Phinder findings to
  Phield alerts.
- "Is the entity type my reviewers keep overriding also the one my policy benchmarks worst
  on?" — joins Arbiter reviews to Philter Scope benchmarks.

None of these is expressible today. An operator must run three separate queries against
three tools and reconcile the results by hand. This RFC defines **cross-tool joins**: a
single PhiSQL `SELECT` that spans discovery (`phinder.findings`), review
(`arbiter.reviews`), monitoring (`phield.trends`/`phield.alerts`), and benchmarking
(`scope.benchmarks`) data, with the join evaluated by a federated query engine.

This is the "cross-tool query verbs" capability the README Status section names as the
endpoint of the query-surface roadmap, and the originating issue calls it "the
category-defining feature." It is also the most ambitious: it introduces join syntax, two
new tool namespaces (Arbiter and the Philter Scope results store), a cross-catalog join-key
convention, and — the load-bearing decision — an **execution model**.

**Why this belongs in the spec rather than a higher layer.** A join is only meaningful if
the two sides agree on what a join key *means*: that `phinder.findings.document_id` and
`arbiter.reviews.document_id` identify the same document, that `entity_type` uses one shared
vocabulary across all four tools. That agreement is a cross-catalog contract — exactly what
the spec exists to hold. A library that joined results ad hoc would re-invent that contract
per consumer and per tool pair, with no guarantee any two implementations agree. The whole
value proposition ("one query, four tools, consistent answer") collapses without the spec
defining the join keys, the join semantics, and the plan a conforming engine executes.

This RFC closes [philterd/philterd-website#125]. It is the capstone of the query-surface
series that began with discovery ([philterd/philterd-website#122]) and continued through
monitoring ([philterd/philterd-website#123] → RFC 0002) and benchmarking
([philterd/philterd-website#124] → RFC 0003).

**Dependencies.** This RFC builds directly on [RFC 0002] and [RFC 0003]: it joins the
`phield.*` tables those RFCs define and reuses the `value expr` / `INTERVAL` / `BETWEEN`
grammar [RFC 0002] introduces (the second worked example below crosses `scan_date` and an
alert `timestamp` window). It should be accepted *after* 0002 and 0003, and targets a later
minor release (**v1.2**) so it does not gate the simpler single-tool surfaces.

## Proposed schema changes

**N/A — no redaction policy schema change.**

As with every query surface, cross-tool joins do not compile to Phileas JSON and do not
touch the redaction policy schema under `schema/`. A join `SELECT` compiles to a
*join-query plan JSON* shape (defined below), consumed by a conforming PhiSQL query engine
that federates per-namespace leaf queries. No `schema/` edit, no `version`/`$id` bump, no
Phileas runtime change.

One **additive catalog change to an existing v1.0 catalog** is required and is called out
explicitly: `findings.yaml` gains an optional `document_id` column so Phinder findings can
join to Arbiter reviews on a shared document identity (see below). It is additive — a new
optional column, no existing column changed — and therefore backward compatible.

## Proposed grammar changes

The v1.0 grammar is frozen; these additions land in a v1.2 grammar
(`spec/v1.2/grammar/PhiSQL.g4` and `PhiSQL.ebnf`). They are strictly additive. The
single-tool `SELECT` of v1.0/v1.1 is the zero-join case of the generalized form below, so
every existing query parses and compiles unchanged.

The discovery/monitoring `SELECT` is extended with join clauses, qualified column
references, projection aliases, and `ORDER BY`. Shown in EBNF (the `.g4` mirrors these):

```ebnf
(* Before — single-table SELECT (v1.1, post-RFC 0002) *)
select form      = "SELECT" , projection list , "FROM" , table ref
                 , [ where discovery ]
                 , [ group by clause ]
                 , [ limit clause ] ;

(* After — optional joins, ORDER BY *)
select form      = "SELECT" , projection list , "FROM" , table ref , { join clause }
                 , [ where discovery ]
                 , [ group by clause ]
                 , [ order by clause ]
                 , [ limit clause ] ;

join clause      = [ join type ] , "JOIN" , table ref , join condition ;

join type        = "INNER"
                 | "LEFT" , [ "OUTER" ]
                 | "RIGHT" , [ "OUTER" ]
                 | "FULL" , [ "OUTER" ] ;   (* default when omitted: INNER *)

join condition   = "ON" , join predicate
                 | "USING" , "(" , column ref , { "," , column ref } , ")" ;

join predicate   = value expr , compare op , value expr        (* value expr from RFC 0002 *)
                 | value expr , "BETWEEN" , value expr , "AND" , value expr
                 | "(" , join predicate , ")"
                 | join predicate , ( "AND" | "OR" ) , join predicate ;

order by clause  = "ORDER" , "BY" , sort key , { "," , sort key } ;
sort key         = ( column ref | numeric literal ) , [ "ASC" | "DESC" ] ;
```

Projections, `WHERE`, `GROUP BY`, and `ORDER BY` are widened to accept **qualified column
references** (`<table>.<column>`) so a query can disambiguate columns that exist in more
than one joined table, and projections gain an optional `AS` alias (the issue's
`COUNT(*) AS overrides`, later referenced by `ORDER BY overrides`):

```ebnf
(* Before *)
column ref       = id | "CONFIDENCE" ;
projection       = "*" | aggregate | column ref ;

(* After *)
column ref       = [ id , "." ] , ( id | "CONFIDENCE" ) ;   (* findings.entity_type *)
projection       = "*" | ( ( aggregate | column ref ) , [ "AS" , id ] ) ;
```

In a `value expr` (RFC 0002), a `factor` that is a `column ref` now also accepts the
qualified form, so join predicates and `WHERE` clauses can compare columns from different
tables (`findings.entity_type = alerts.entity_type`, `alerts.timestamp BETWEEN
findings.scan_date AND findings.scan_date + INTERVAL '1 hour'`).

**Reserved keywords added:** `JOIN`, `INNER`, `LEFT`, `RIGHT`, `FULL`, `OUTER`, `USING`,
`ORDER`, `ASC`, `DESC`. (`ON` and `BETWEEN` are reserved by RFC 0002; `AS` and `BY` are
reserved in v1.0.) Added to `spec/v1.2/catalog/keywords.yaml`. Table/namespace and column
names remain catalog-validated, not reserved, per the established precedent.

### New tool namespaces and catalogs

Two tools that have no spec presence today are introduced as queryable namespaces. Each
gets a catalog mirroring `findings.yaml` (columns, types, filterable/groupable subsets,
default namespace). Conforming engines must surface at least the `required: true` columns.

**`spec/v1.2/catalog/reviews.yaml` — `arbiter.reviews`** (Arbiter, the human-review tool):

```yaml
version: v1.2
default_namespace: arbiter
table:
  name: reviews
  namespace: arbiter
  description: One row per human review decision on a detected finding.
columns:
  - { name: review_id,   type: string,    required: true,  description: Stable id of the review record. }
  - { name: document_id, type: string,    required: true,  description: Document the reviewed finding lives in. Shared join key with phinder.findings.document_id. }
  - { name: finding_id,  type: string,    required: false, description: The phinder.findings.finding_id this review concerns, when traceable to a specific finding. }
  - { name: entity_type, type: string,    required: true,  description: Entity type of the reviewed finding. Shared vocabulary with all toolkit tables. }
  - { name: decision,    type: string,    required: true,  description: "Reviewer decision. One of: confirm, override, escalate." }
  - { name: reviewer,    type: string,    required: false, description: Identifier of the reviewer or review queue. }
  - { name: policy_name, type: string,    required: false, description: Policy under review. Shared join key with scope.benchmarks.policy_name. }
  - { name: timestamp,   type: timestamp, required: true,  description: When the decision was recorded. }
filterable_columns: [document_id, finding_id, entity_type, decision, reviewer, policy_name, timestamp]
groupable_columns:  [document_id, entity_type, decision, reviewer, policy_name]
```

**`spec/v1.2/catalog/benchmarks.yaml` — `scope.benchmarks`** (the persisted results of
Philter Scope runs; the query-time, stored counterpart to the action verbs in [RFC 0003]):

```yaml
version: v1.2
default_namespace: scope
table:
  name: benchmarks
  namespace: scope
  description: >-
    One row per (benchmark run, entity_type) of persisted Philter Scope results.
    The stored counterpart to RFC 0003's COMPARE/BENCHMARK/MEASURE action verbs:
    those run an evaluation; this table is where their results live so they can
    be joined against live data.
columns:
  - { name: benchmark_id, type: string,    required: true,  description: Stable id of the benchmark run. }
  - { name: policy_name,  type: string,    required: true,  description: Policy that was evaluated. Shared join key with arbiter.reviews.policy_name. }
  - { name: dataset,      type: string,    required: true,  description: Gold-standard dataset the run scored against. }
  - { name: entity_type,  type: string,    required: true,  description: Entity type this row's metrics are for. Shared vocabulary with all toolkit tables. }
  - { name: precision,    type: number,    required: false, description: Per-entity precision, per metrics.yaml (RFC 0003). }
  - { name: recall,       type: number,    required: false, description: Per-entity recall, per metrics.yaml. }
  - { name: f1,           type: number,    required: false, description: Per-entity F1, per metrics.yaml. }
  - { name: run_date,     type: timestamp, required: true,  description: When the benchmark run executed. }
filterable_columns: [policy_name, dataset, entity_type, precision, recall, f1, run_date]
groupable_columns:  [policy_name, dataset, entity_type]
```

### Common join-key conventions

Acceptance criterion two ("common identifier conventions documented across all toolkit
tables") is met by a new convention catalog `spec/v1.2/catalog/join-keys.yaml` that names
the canonical cross-tool join keys, the tables that expose them, and their shared meaning.
A `USING (col)` join is only valid when every joined table declares `col` as a join key
here; otherwise the engine must reject the query.

```yaml
version: v1.2
# Canonical join keys shared across toolkit tables. A USING(col) join is valid
# only if every participating table lists col below. ON-joins may use any
# compatible columns, but these are the identifiers guaranteed to mean the same
# thing across tools.
join_keys:
  - name: document_id
    type: string
    meaning: Stable identity of a source document across tools.
    exposed_by: [phinder.findings, arbiter.reviews]
  - name: entity_type
    type: string
    meaning: PII entity type, drawn from entity-types.yaml in every table.
    exposed_by: [phinder.findings, arbiter.reviews, phield.trends, phield.alerts, scope.benchmarks]
  - name: scan_id
    type: string
    meaning: Identity of a discovery scan.
    exposed_by: [phinder.findings]   # extend as other tools adopt scan provenance
  - name: policy_name
    type: string
    meaning: Name/basename of a redaction policy.
    exposed_by: [arbiter.reviews, scope.benchmarks]
```

To make `document_id` a usable join key on the discovery side, `findings.yaml` gains it as
an **optional additive column** (the one existing-catalog change noted above):

```yaml
# added to spec/v1.0 findings.yaml columns: (additive, optional)
  - name: document_id
    type: string
    required: false
    description: >-
      Stable identity of the source document this finding lives in, shared with
      arbiter.reviews.document_id for cross-tool joins. Optional: engines that do
      not track document identity omit it, and joins that need it will simply
      match nothing for those rows (see incomplete-join semantics below).
```

### Compile target: join-query plan JSON

A join `SELECT` compiles to a *join-query plan JSON* — a sibling of the discovery,
monitoring, and benchmark query shapes. The plan names one **leaf query per namespace**
(each itself a discovery-/monitoring-/reviews-/benchmarks-query over a single table, reusing
the existing per-tool shapes), a **join graph**, and the **post-join** projection / filter /
group / order / limit:

```json
{
  "queryType": "join",
  "leaves": [
    { "alias": "<table alias>", "namespace": "<tool>", "table": "<table>",
      "query": { /* single-table query JSON for this leaf */ } }
  ],
  "joins": [
    { "type": "inner | left | right | full",
      "left": "<alias>", "right": "<alias>",
      "using": ["<col>"]          /* OR */,
      "on": { /* join predicate tree over qualified columns */ } }
  ],
  "where":  { /* post-join predicate tree, or null */ },
  "projections": [ /* qualified columns, aggregates, each with optional alias */ ],
  "groupBy": [ /* qualified columns / ordinals */ ],
  "orderBy": [ { "expr": "<col-or-alias-or-ordinal>", "dir": "asc | desc" } ],
  "limit": null
}
```

A conforming engine executes each leaf against its owning tool, then performs the joins,
filter, aggregation, ordering, and limiting over the combined rows. A leaf whose tool is
unreachable is an **error**, not an empty result (see semantics below).

## Execution model (acceptance criterion three)

**Decision: federated execution by a dedicated PhiSQL query engine. The reference
implementation compiles the plan but does not execute it.**

Rationale, stated against the three candidates the issue lists:

1. **In the reference implementation (rejected as the executor).** The reference
   implementation is a parser/compiler: it has no data access, no network, and no business
   touching four tools' storage. Making it a query engine would couple the spec's reference
   compiler to every tool's API and storage format, violate its single responsibility, and
   not scale past toy datasets held in memory. The reference implementation's job here ends
   at emitting a correct join-query plan and validating join keys against the catalogs —
   exactly as it stops at discovery-query JSON today without crawling S3.

2. **Federated queries to each tool's storage (chosen).** The plan's leaves are ordinary
   single-tool queries in the shapes the tools already consume. A federated PhiSQL query
   engine pushes each leaf to its owning tool (Phinder, Arbiter, Phield, Philter Scope),
   receives rows, and performs the join itself. This respects tool ownership of storage
   (each tool stays the source of truth for its own data), reuses the per-tool query
   contracts unchanged, degrades predictably (a missing tool fails its leaf, not the whole
   toolkit's data model), and lets each tool scale and secure its own store. It is the only
   option consistent with the README's "each tool owns its data" posture and with how the
   discovery/monitoring/benchmark shapes were already designed as independent contracts.

3. **A common materialized warehouse (rejected as a mandate, allowed as an option).**
   Requiring every tool to export into one queryable store would give the simplest join
   execution but impose a heavy operational burden, duplicate every tool's data, and create
   a staleness/consistency problem the federated model avoids. The spec therefore does **not
   mandate** materialization — but it does not forbid it either: an engine is free to back
   the join with a warehouse as an implementation detail, as long as it answers the same
   join-query plan with the same semantics. The contract is the plan and the semantics, not
   the topology.

The spec defines the plan and the semantics; **where** the join physically happens is an
engine choice, with federation the recommended and reference model. The PhiSQL query engine
itself is a new component tracked outside this RFC; this RFC specifies the contract it must
honor.

## Semantics for missing and incomplete data (acceptance criterion four, part)

- **Default join is `INNER`.** Only rows with a match on both sides survive. `JOIN` with no
  type keyword means `INNER JOIN`.
- **Outer joins preserve the named side.** `LEFT JOIN` keeps every left row; right-side
  columns are `NULL` where no match exists. `RIGHT`/`FULL` symmetrically. This is the
  mechanism for "findings that were never reviewed" (`LEFT JOIN arbiter.reviews`, then
  `WHERE reviews.review_id IS NULL` once `IS NULL` lands — see Unresolved questions).
- **`NULL` from a non-match is distinct from a tool error.** A leaf that returns zero rows
  (the tool is up, nothing matched) yields legitimate non-matches/`NULL`s under outer joins.
  A leaf whose tool is **unreachable or rejects the query** is a hard error: the engine must
  fail the whole query with a clear message naming the offending namespace, never silently
  substitute empty rows. (Same "reject, don't no-op" rule `sources.yaml` already states.)
- **Aggregates follow standard SQL null handling.** `COUNT(*)` counts joined rows;
  `COUNT(col)` and `AVG(col)`/`SUM(col)` ignore `NULL`. So a `LEFT JOIN` plus `COUNT(reviews.review_id)`
  counts only reviewed findings, while `COUNT(*)` counts all.
- **Join-key compatibility is validated at compile time.** `USING (col)` requires every
  joined table to declare `col` in `join-keys.yaml`; a mismatch (or joining on columns of
  incompatible declared types) is a compile error, not a runtime surprise.
- **Optional join keys match nothing when absent.** Because `document_id` is optional in
  `findings.yaml`, a findings row from an engine that does not populate it simply fails to
  match any review row — an inner join drops it, an outer join keeps it with `NULL`s. This is
  defined, not undefined, behavior.

## Examples

At least four cross-tool examples land under `spec/v1.2/examples/`, parsed by
`ExamplesParseTest` and held in the compiler's not-yet-compiled skip set until the join
compiler ships.

### Example 1 — findings × reviews: most-overridden entity types

PhiSQL (`spec/v1.2/examples/35-findings-join-reviews.phisql`):

```sql
-- Which detected entity types did reviewers override most often?
SELECT findings.entity_type, COUNT(*) AS overrides
  FROM phinder.findings
  JOIN arbiter.reviews USING (document_id)
  WHERE reviews.decision = 'override'
  GROUP BY findings.entity_type
  ORDER BY overrides DESC;
```

Compiled join-query plan JSON (`spec/v1.2/examples/35-findings-join-reviews.json`):

```json
{
  "queryType": "join",
  "leaves": [
    { "alias": "findings", "namespace": "phinder", "table": "findings",
      "query": { "queryType": "discovery", "table": "phinder.findings", "projections": ["*"], "filters": null } },
    { "alias": "reviews", "namespace": "arbiter", "table": "reviews",
      "query": { "queryType": "discovery", "table": "arbiter.reviews", "projections": ["*"],
                 "filters": { "op": "=", "left": { "kind": "column", "name": "decision" },
                              "right": { "kind": "literal", "type": "string", "value": "override" } } } }
  ],
  "joins": [ { "type": "inner", "left": "findings", "right": "reviews", "using": ["document_id"] } ],
  "where": null,
  "projections": [
    { "kind": "column", "name": "findings.entity_type" },
    { "kind": "aggregate", "fn": "COUNT", "arg": "*", "as": "overrides" }
  ],
  "groupBy": [ { "kind": "column", "name": "findings.entity_type" } ],
  "orderBy": [ { "expr": "overrides", "dir": "desc" } ],
  "limit": null
}
```

(The `reviews.decision = 'override'` filter is pushed down into the `arbiter.reviews` leaf so
the tool returns only override rows; an engine may equivalently keep it as a post-join
`where`. Pushdown is an engine optimization the plan permits but does not require.)

### Example 2 — findings × alerts: scans that later triggered anomalies

PhiSQL (`spec/v1.2/examples/36-findings-join-alerts.phisql`):

```sql
-- Which discovery findings sit in a scan that triggered a Phield alert
-- of the same entity type within an hour of the scan?
SELECT findings.path, alerts.severity
  FROM phinder.findings
  JOIN phield.alerts
    ON findings.entity_type = alerts.entity_type
   AND alerts.timestamp BETWEEN findings.scan_date
                            AND findings.scan_date + INTERVAL '1 hour';
```

Compiled plan (`spec/v1.2/examples/36-findings-join-alerts.json`) — abbreviated to the join
graph; both leaves are unfiltered single-table queries:

```json
{
  "queryType": "join",
  "leaves": [
    { "alias": "findings", "namespace": "phinder", "table": "findings", "query": { "queryType": "discovery", "table": "phinder.findings", "projections": ["*"], "filters": null } },
    { "alias": "alerts",   "namespace": "phield",   "table": "alerts",   "query": { "queryType": "monitoring", "table": "phield.alerts", "projections": ["*"], "filters": null } }
  ],
  "joins": [
    { "type": "inner", "left": "findings", "right": "alerts",
      "on": { "op": "AND", "args": [
        { "op": "=", "left": { "kind": "column", "name": "findings.entity_type" }, "right": { "kind": "column", "name": "alerts.entity_type" } },
        { "op": "BETWEEN", "left": { "kind": "column", "name": "alerts.timestamp" },
          "low":  { "kind": "column", "name": "findings.scan_date" },
          "high": { "kind": "arith", "op": "+", "left": { "kind": "column", "name": "findings.scan_date" }, "right": { "kind": "interval", "value": "1 hour" } } }
      ] } }
  ],
  "where": null,
  "projections": [ { "kind": "column", "name": "findings.path" }, { "kind": "column", "name": "alerts.severity" } ],
  "groupBy": [], "orderBy": [], "limit": null
}
```

### Example 3 — findings × reviews (LEFT): never-reviewed findings

PhiSQL (`spec/v1.2/examples/37-findings-leftjoin-reviews.phisql`):

```sql
-- High-confidence findings that no reviewer has acted on yet, by entity type.
SELECT findings.entity_type, COUNT(*) AS unreviewed
  FROM phinder.findings
  LEFT JOIN arbiter.reviews USING (document_id)
  WHERE findings.confidence > 0.9
    AND reviews.review_id IS NULL
  GROUP BY findings.entity_type
  ORDER BY unreviewed DESC;
```

This example demonstrates outer-join `NULL` semantics: `LEFT JOIN` keeps every qualifying
finding, and `reviews.review_id IS NULL` selects the ones with no matching review. It depends
on an `IS NULL` predicate (see Unresolved questions); its compiled plan sets the join `type`
to `"left"` and carries `reviews.review_id IS NULL` in the post-join `where`.

### Example 4 — reviews × benchmarks: do overrides track poor benchmarks?

PhiSQL (`spec/v1.2/examples/38-reviews-join-benchmarks.phisql`):

```sql
-- For the hipaa-v2 policy, per entity type: how many reviewer overrides,
-- alongside that entity type's benchmarked precision.
SELECT reviews.entity_type, COUNT(*) AS overrides, benchmarks.precision
  FROM arbiter.reviews
  JOIN scope.benchmarks USING (entity_type)
  WHERE reviews.decision = 'override'
    AND reviews.policy_name = 'hipaa-v2'
    AND benchmarks.policy_name = 'hipaa-v2'
  GROUP BY reviews.entity_type, benchmarks.precision
  ORDER BY overrides DESC;
```

The compiled plan joins the `arbiter.reviews` and `scope.benchmarks` leaves on
`entity_type`, pushes the `decision`/`policy_name` filters into the reviews leaf and the
`policy_name` filter into the benchmarks leaf, and applies the grouping/ordering post-join.

## Alternatives considered

**Alternative 1: No joins — document a manual multi-query convention instead.**
Tell operators to run the single-tool queries separately and join in a spreadsheet or
script.

Rejected because: that is the status quo the issue exists to end, and it provides no shared
contract for what a join key means across tools, so two people "joining findings to reviews"
could silently do it differently. The category-defining value is precisely a *single*
portable query.

**Alternative 2: Make the reference implementation the query engine.**
Have `reference/` actually fetch from each tool and compute the join.

Rejected — see the Execution model section. The reference implementation is a compiler, not a
data plane; coupling it to four tools' storage breaks its single responsibility and does not
scale.

**Alternative 3: Mandate a materialized cross-tool warehouse.**
Require every tool to export into one store and run joins there.

Rejected as a mandate (allowed as an engine option) — see Execution model. Operationally
heavy, duplicative, and introduces staleness the federated model avoids; the spec fixes the
plan and semantics, not the topology.

**Alternative 4: Implicit joins via a comma-separated `FROM` + `WHERE` (SQL-89 style).**
`FROM phinder.findings, arbiter.reviews WHERE findings.document_id = reviews.document_id`.

Rejected because: explicit `JOIN ... ON/USING` makes the join graph, the join type
(inner vs outer), and the join keys syntactically explicit and machine-extractable into the
plan's `joins` array. Implicit joins bury the graph inside a flat `WHERE`, make outer joins
inexpressible, and are exactly the style modern SQL guidance discourages.

**Alternative 5: Reserve the tool/table names (`PHINDER`, `ARBITER`, `SCOPE`, …) as keywords.**
Rejected, consistent with every prior query-surface RFC: namespaces and columns are
catalog-validated, not reserved, so the toolkit can add tables and columns without grammar
changes.

## Drawbacks

- **Largest single grammar and concept expansion in the language's history.** Joins,
  qualified columns, aliases, `ORDER BY`, outer-join null semantics, and ten new reserved
  keywords. This is a real step up in learning curve and in what a conforming parser must
  implement.
- **Introduces two tools to the spec that had no presence (Arbiter, the Scope results
  store), and a brand-new execution component** (the federated query engine). The verbs are
  inert syntax until that engine and those tools' query endpoints exist — a larger downstream
  obligation than any prior surface.
- **A cross-catalog contract to keep consistent.** Join keys (`document_id`, `entity_type`,
  `policy_name`) must mean the same thing in every catalog forever; the `join-keys.yaml`
  convention is now a thing that can drift from reality if a tool renames a column.
- **Touches a v1.0 stable catalog.** Adding `document_id` to `findings.yaml` is additive and
  safe, but it is the first time a query-surface RFC reaches back into a frozen-version
  catalog; the precedent (additive optional columns to existing catalogs are allowed in a
  minor version) should be confirmed.
- **Federation has real failure modes.** Partial tool availability, per-tool latency skew,
  and large intermediate result sets are now the engine's problem; the spec defines correct
  *answers* but cannot make a slow federated join fast.

## Backward compatibility

- **Existing `.phisql` files:** The single-table `SELECT` is the zero-join case of the new
  form; every v1.0/v1.1 query parses and compiles identically. The new reserved keywords
  collide with no existing file. The `findings.yaml` `document_id` addition is an optional
  column; existing discovery queries and their compiled output are unchanged.
- **Existing Phileas JSON / runtime:** Untouched. Joins do not compile to Phileas JSON.
- **Existing downstream consumers:** Discovery-, monitoring-, and benchmark-query JSON shapes
  are unchanged and are reused verbatim as join leaves. New consumers (the federated query
  engine, Arbiter's and Scope's query endpoints) opt in; existing single-tool consumers are
  unaffected.

This is a strictly-additive change.

## Versioning impact

**Minor.** All additions are new grammar, new catalogs, and one additive optional column on
an existing catalog; nothing previously accepted is rejected (modulo new reserved words,
which collide with no existing file) and no existing compile output changes. Per the
[versioning policy](../CONTRIBUTING.md#versioning-policy) this is a minor bump. It targets
**v1.2**, after the v1.1 monitoring/benchmarking surfaces it depends on; it must not be
released before [RFC 0002] and [RFC 0003], whose `phield.*` and `scope.*` tables and
`value expr`/`INTERVAL` grammar it reuses.

## Reference implementation

Not yet implemented; to land in a follow-up PR linked from this RFC, in two parts:

1. **Grammar + catalogs + examples (parse-complete).** Add the v1.2 grammar (joins,
   qualified columns, aliases, `ORDER BY`), `reviews.yaml`, `benchmarks.yaml`,
   `join-keys.yaml`, the `findings.yaml` `document_id` column, the ten new reserved keywords,
   and the four example `.phisql`/`.json` pairs. `scripts/validate_spec.py` is extended to
   (a) resolve every qualified column in a join example against the owning table's catalog and
   (b) verify every `USING` key is declared for all participating tables in `join-keys.yaml`.
2. **Join-plan compiler.** Emit join-query plan JSON in the reference compiler — including
   join-key validation and leaf-query construction — and remove the examples from the skip
   set so the round-trip test asserts byte-equivalent plans against the checked-in files.

The **federated PhiSQL query engine** that *executes* the plan is a separate component
tracked outside this RFC; per the execution-model decision, the reference implementation
compiles the plan but does not run it. Acceptance requires the worked examples (included
above), not a running engine.

## Unresolved questions

- **`IS NULL` / `IS NOT NULL` predicate.** Outer-join filtering ("findings with no review,"
  Example 3) needs a null test that PhiSQL does not have. Should this RFC add `IS NULL` /
  `IS NOT NULL` to the predicate grammar, or should it be split into its own small RFC that
  this one depends on? Example 3 assumes it lands here.
- **`scope.benchmarks` vs RFC 0003's action verbs.** RFC 0003 models benchmarking as actions
  (`COMPARE`/`BENCHMARK`/`MEASURE`) that *run* an evaluation; this RFC adds a *stored*
  `scope.benchmarks` table to join against. Is persisting benchmark results into a queryable
  table in scope for Philter Scope, and should the two RFCs be reconciled so the action verbs
  write the rows this table reads?
- **Arbiter as a first-class tool.** Arbiter has no other spec presence. Is defining
  `arbiter.reviews` here the right first step, or should an Arbiter discovery/query surface be
  designed before it is joined against?
- **Aggregates and `GROUP BY` over qualified columns / non-grouped projections.** Standard SQL
  requires every non-aggregated projection to appear in `GROUP BY` (Example 4 groups by
  `benchmarks.precision` for exactly this reason). Should the compiler enforce that rule, or
  defer it to the engine?
- **Federation limits.** Should the spec cap join arity (number of tools per query) or
  require the engine to document result-size/timeout limits, to keep "one query, four tools"
  from becoming an unbounded fan-out?
- **Minor-version directory layout.** Shared with [RFC 0002]/[RFC 0003]: the convention for
  `spec/v1.x/` directories needs to be settled once.

## Future possibilities

- **`IS NULL`, `CASE`, and richer expressions** that joins make newly worth having.
- **Subqueries / CTEs** (`WITH`) for multi-step cross-tool analysis.
- **Materialized cross-tool views** an engine can cache, given the federated baseline.
- **More tool namespaces** as the toolkit grows, each added by a catalog with declared join
  keys — no grammar change required.
- **A pass/fail gate over a join** (e.g. alert when override-rate for an entity type exceeds a
  threshold *and* its benchmarked precision is below one), the natural pairing of joins with
  the benchmarking gate sketched in RFC 0003's future possibilities.

[RFC 0002]: 0002-monitoring-query-verbs.md
[RFC 0003]: 0003-benchmarking-query-verbs.md
[philterd/philterd-website#125]: https://github.com/philterd/philterd-website/issues/125
[philterd/philterd-website#124]: https://github.com/philterd/philterd-website/issues/124
[philterd/philterd-website#123]: https://github.com/philterd/philterd-website/issues/123
[philterd/philterd-website#122]: https://github.com/philterd/philterd-website/issues/122
