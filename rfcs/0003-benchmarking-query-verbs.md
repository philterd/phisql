---
rfc: 0003
title: Benchmarking query verbs over Philter Scope policy evaluations
status: Draft
author: Jeff Zemerick <jzonthemtn>
created: 2026-06-08
target_version: v1.1
versioning_impact: minor
---

# RFC 0003: Benchmarking query verbs over Philter Scope policy evaluations

## Motivation

PhiSQL v1.0 ships the redaction authoring surface (compiles to Phileas JSON) and the
**discovery** query surface (`SELECT ... FROM findings`, compiling to discovery-query JSON
consumed by Phinder). [RFC 0002] adds the **monitoring** surface (`SELECT ... FROM
phield.trends`, compiling to monitoring-query JSON consumed by Phield). The README's Status
section names the remaining surface — "cross-tool query verbs" — as deferred alongside
discovery and monitoring.

Philter Scope is the Philterd benchmarking tool: it evaluates a redaction policy against a
labeled gold-standard dataset and reports detection quality (precision, recall, F1, a
confusion matrix), optionally broken down per entity type. The central question an operator
asks Philter Scope is "did my policy change make detection better or worse?" — and today
there is no portable, declarative way to ask it. Comparing `hipaa-v2` against `hipaa-v1` on
a clinical gold standard means driving Philter Scope's native interface directly, which is
tool-specific and unavailable to the PhiSQL CLI and anything else that only speaks PhiSQL.

Concretely, an operator wants to write:

```sql
COMPARE POLICY 'hipaa-v2' AGAINST 'hipaa-v1'
  ON DATASET 'clinical-gold-standard'
  REPORT precision, recall, f1 PER entity_type;
```

and have it run against any conforming benchmarking engine, exactly as a discovery
`SELECT ... FROM findings` runs against any conforming discovery engine.

**Why this belongs in the spec rather than a higher layer.** This is the same argument the
discovery and monitoring surfaces already settled: cross-tool query verbs are first-class in
PhiSQL, and the portability guarantee — "any conforming engine answers the same query the
same way" — only exists if the grammar, the metric vocabulary, and the compile target live
in the spec. A library wrapper around Philter Scope's API would be Scope-specific and would
give no other benchmarking engine a contract to conform to. Acceptance criterion two of the
originating issue ("metric definitions formalized and aligned with current Philter Scope
output") is itself a spec task: the definitions of precision/recall/F1/confusion_matrix must
be written down once, in a catalog, so every engine computes them identically.

**Workaround today.** None within PhiSQL. Operators drive Philter Scope's native interface,
which is non-portable and unavailable to PhiSQL-only tooling.

This RFC closes [philterd/philterd-website#124]. It is a sibling of the discovery
([philterd/philterd-website#122]) and monitoring ([philterd/philterd-website#123]) query
surfaces and follows the same architectural pattern.

## Proposed schema changes

**N/A — no redaction policy schema change.**

Like the discovery and monitoring verbs, benchmarking queries do **not** compile to Phileas
JSON and do not touch the canonical redaction policy schema under `schema/`. They compile to
a separate *benchmark-query JSON* shape (defined below), consumed by a conforming
benchmarking engine such as Philter Scope. The README governance posture — "Anything PhiSQL
can express must be representable as Phileas JSON" — applies to the redaction surface; the
query surfaces are explicitly separate compile targets. No `schema/` edit, no `version`/`$id`
bump, and no Phileas runtime change is required.

Note one subtlety: a benchmarking statement *references* policies by name (`'hipaa-v2'`,
`'hipaa-v1'`). Those policies are ordinary Phileas JSON policies (or `.phisql` files that
compile to them), resolved by the benchmarking engine — but the benchmarking statement
itself neither contains nor alters a policy. It is a query *about* policies, not a policy.

## Proposed grammar changes

The v1.0 grammar is frozen, so these additions land in a v1.1 grammar
(`spec/v1.1/grammar/PhiSQL.g4` and `PhiSQL.ebnf` — see the **Unresolved questions** note on
the minor-version directory layout, shared with RFC 0002). The additions are strictly
additive: every v1.0 statement continues to parse unchanged.

A new top-level `benchmark stmt` is added as an alternative of `statement`, in EBNF (the
`.g4` changes mirror these productions):

```ebnf
(* Before — statement alternatives, v1.0 *)
statement        = policy decl
                 | configure stmt
                 | redact stmt
                 | deidentify stmt
                 | ignore stmt
                 | define identifier stmt
                 | define dictionary stmt
                 | define section stmt
                 | detect stmt
                 | discovery stmt ;

(* After — one new alternative *)
statement        = policy decl
                 | configure stmt
                 | redact stmt
                 | deidentify stmt
                 | ignore stmt
                 | define identifier stmt
                 | define dictionary stmt
                 | define section stmt
                 | detect stmt
                 | discovery stmt
                 | benchmark stmt ;

(* New productions *)
benchmark stmt   = compare stmt | measure stmt ;

(* Two policies head-to-head. *)
compare stmt     = "COMPARE" , "POLICY" , policy ref , "AGAINST" , policy ref
                 , on dataset clause
                 , report clause ;

(* A single policy against the dataset's gold standard.
   BENCHMARK and MEASURE are synonyms (see Unresolved questions). *)
measure stmt     = ( "BENCHMARK" | "MEASURE" ) , "POLICY" , policy ref
                 , on dataset clause
                 , report clause ;

policy ref       = string literal ;   (* a policy name / file basename, e.g. 'hipaa-v2' *)

on dataset clause = "ON" , "DATASET" , string literal ;   (* gold-standard dataset name *)

report clause    = "REPORT" , metric list , [ "PER" , report dimension ] ;

metric list      = metric , { "," , metric } ;

metric           = id ;   (* validated against metrics.yaml: precision, recall, f1, confusion_matrix *)

report dimension = id ;   (* validated against metrics.yaml report_dimensions: entity_type *)
```

**Reserved keywords added:** `COMPARE`, `BENCHMARK`, `MEASURE`, `AGAINST`, `DATASET`,
`REPORT`, `PER`, `ON`. (`POLICY` is already reserved in v1.0.) These are added to
`spec/v1.1/catalog/keywords.yaml`. Following the discovery/monitoring precedent, the metric
names (`precision`, `recall`, `f1`, `confusion_matrix`), the report dimension (`entity_type`),
the policy names, and the dataset names are **not** reserved — they are validated against the
benchmarking catalog (or resolved by the engine) in their syntactic positions, exactly as
entity types and strategy names are reserved only in their positions, and as `findings` is
validated against `findings.yaml` rather than reserved.

### New catalog file

A new catalog `spec/v1.1/catalog/metrics.yaml` declares the benchmarking metric vocabulary
and report dimensions, with each metric's definition written down so every conforming engine
computes it identically. This directly satisfies acceptance criterion two ("metric
definitions formalized and aligned with current Philter Scope output").

```yaml
# PhiSQL v1.1 benchmarking metric catalog.
#
# Defines the metrics a `REPORT` clause may request and the dimensions a `PER`
# clause may break them down by. A finding is a true positive (TP) when a
# detected span matches a gold-standard annotation of the same entity_type at
# the same location per the engine's span-matching rule; a false positive (FP)
# is a detected span with no matching annotation; a false negative (FN) is an
# annotation the policy failed to detect. Conforming benchmarking engines
# (e.g., Philter Scope) must compute these identically.
#
# Status: Draft (v1.1).

version: v1.1

metrics:
  - name: precision
    type: number
    range: [0.0, 1.0]
    definition: "TP / (TP + FP) — fraction of detections that were correct."
  - name: recall
    type: number
    range: [0.0, 1.0]
    definition: "TP / (TP + FN) — fraction of gold-standard PII that was detected."
  - name: f1
    type: number
    range: [0.0, 1.0]
    definition: "2 * (precision * recall) / (precision + recall) — harmonic mean; 0 when both are 0."
  - name: confusion_matrix
    type: object
    definition: >-
      Per-cell counts {tp, fp, fn} for the evaluated scope. True negatives are
      not counted for span detection (the negative space is unbounded), so the
      matrix is reported as the TP/FP/FN triple rather than a full 2x2.

report_dimensions:
  # Dimensions a `PER` clause may break the requested metrics down by.
  # Without a `PER` clause, metrics are reported once over the whole dataset.
  - name: entity_type
    description: >-
      One row of metrics per catalog entity type (SSN, CREDIT_CARD, …) present
      in the dataset's gold standard.
```

### Compile target: benchmark-query JSON

A benchmarking statement compiles to a *benchmark-query JSON* object — a sibling of the
discovery-query and monitoring-query shapes, **not** Phileas JSON. The shape:

```json
{
  "queryType": "benchmark",
  "mode": "compare | single",
  "candidate": "<policy ref>",
  "baseline": "<policy ref, compare mode only>",
  "dataset": "<dataset name>",
  "metrics": [ /* requested metric names */ ],
  "per": "<report dimension, or null>"
}
```

`COMPARE` emits `"mode": "compare"` with both `candidate` and `baseline`; `BENCHMARK`/
`MEASURE` emit `"mode": "single"` with `candidate` only and `baseline: null`. Conforming
benchmarking engines consume this JSON; an engine that cannot resolve a referenced policy or
dataset, or does not support a requested metric, must reject the query with a clear error
rather than silently no-op (the same rule `sources.yaml` applies to unsupported schemes).

## Examples

These land under `spec/v1.1/examples/` and become part of the reference test suite. As with
the discovery and monitoring examples, they are parsed by `ExamplesParseTest` and listed in
the compiler's not-yet-compiled skip set until the benchmarking compiler ships (see
**Reference implementation**).

### Example 1 — compare two policies, per entity type

PhiSQL (`spec/v1.1/examples/32-compare-policies.phisql`):

```sql
-- Did hipaa-v2 improve detection over hipaa-v1 on the clinical gold standard?
COMPARE POLICY 'hipaa-v2' AGAINST 'hipaa-v1'
  ON DATASET 'clinical-gold-standard'
  REPORT precision, recall, f1 PER entity_type;
```

Compiled benchmark-query JSON (`spec/v1.1/examples/32-compare-policies.json`):

```json
{
  "queryType": "benchmark",
  "mode": "compare",
  "candidate": "hipaa-v2",
  "baseline": "hipaa-v1",
  "dataset": "clinical-gold-standard",
  "metrics": ["precision", "recall", "f1"],
  "per": "entity_type"
}
```

### Example 2 — single-policy confusion matrix

PhiSQL (`spec/v1.1/examples/33-benchmark-confusion-matrix.phisql`):

```sql
-- Where is the pci-dss policy making mistakes on call-center transcripts?
BENCHMARK POLICY 'pci-dss'
  ON DATASET 'call-center-transcripts'
  REPORT confusion_matrix;
```

Compiled benchmark-query JSON (`spec/v1.1/examples/33-benchmark-confusion-matrix.json`):

```json
{
  "queryType": "benchmark",
  "mode": "single",
  "candidate": "pci-dss",
  "baseline": null,
  "dataset": "call-center-transcripts",
  "metrics": ["confusion_matrix"],
  "per": null
}
```

### Example 3 — single-policy measurement, per entity type (`MEASURE` synonym)

PhiSQL (`spec/v1.1/examples/34-measure-per-entity.phisql`):

```sql
-- Per-entity precision and recall for the gdpr policy on EU support email.
MEASURE POLICY 'gdpr'
  ON DATASET 'eu-support-emails'
  REPORT precision, recall PER entity_type;
```

Compiled benchmark-query JSON (`spec/v1.1/examples/34-measure-per-entity.json`):

```json
{
  "queryType": "benchmark",
  "mode": "single",
  "candidate": "gdpr",
  "baseline": null,
  "dataset": "eu-support-emails",
  "metrics": ["precision", "recall"],
  "per": "entity_type"
}
```

## Alternatives considered

**Alternative 1: Reuse `SELECT ... FROM <benchmark-table>` instead of new verbs.**
Model benchmarking as a query over a virtual results table, e.g.
`SELECT entity_type, precision, recall FROM benchmark('hipaa-v2', 'clinical-gold-standard')`.

Rejected because: benchmarking is fundamentally an *action* (run a policy over a dataset and
score it), not a projection over an existing stored table the way discovery `findings` and
monitoring `phield.trends` are. Discovery and monitoring read rows that already exist;
benchmarking *produces* them by executing an evaluation. Dressing that up as a `SELECT` over
a table-valued function hides the cost and the imperative nature, and the `COMPARE ... AGAINST`
two-policy shape does not map cleanly onto a single `FROM`. Distinct verbs (`COMPARE`,
`BENCHMARK`/`MEASURE`) read as what they are. (Discovery's own scan verbs — `FIND PII`,
`DISCOVER ENTITIES`, `SCAN` — set the precedent that actions get verbs, not `SELECT`.)

**Alternative 2: Reserve the metric names (`PRECISION`, `RECALL`, `F1`, `CONFUSION_MATRIX`) as keywords.**
Bake the metric vocabulary into the grammar.

Rejected because: it contradicts the established precedent (entity types, strategies, and
`findings` columns are catalog-validated, not reserved) and makes the metric set
un-extensible without a grammar change every time Philter Scope adds a metric (e.g. a future
`specificity` or `support`). Keeping metrics in `metrics.yaml` lets the vocabulary grow
without touching the grammar and avoids colliding metric names with user-chosen identifiers
elsewhere.

**Alternative 3: Drop `MEASURE`, keep only `BENCHMARK` for the single-policy case.**
The originating issue lists `COMPARE POLICY`, `BENCHMARK`, and `MEASURE`, but only `COMPARE`
and `BENCHMARK` appear in its examples.

Partially adopted: this RFC accepts `MEASURE` as an exact synonym of `BENCHMARK` (identical
grammar, identical compiled JSON) so the verb the issue named is available, but flags in
**Unresolved questions** whether two spellings for one operation earn their keep or whether
one should be dropped before acceptance to keep the surface minimal.

**Alternative 4: Make `ON DATASET` take a URI from `sources.yaml` instead of a bare name.**
Reuse the discovery source catalog so a dataset is addressed as `s3://…`/`file://…`.

Rejected for now because: a Philter Scope dataset is a *labeled* gold standard (documents
plus annotations), not a raw source location — it is a named, versioned artifact the
benchmarking engine manages, more like a policy name than a bucket path. Treating it as an
opaque engine-resolved name keeps that distinction clear. Allowing URI-addressed datasets is
noted under **Future possibilities** if a concrete need appears.

## Drawbacks

- **A new statement family and eight new reserved keywords** — the largest keyword addition
  of any query surface so far. More keywords means more potential collisions for any
  pre-v1.1 `.phisql` that used `compare`, `report`, `per`, `on`, etc. as bare identifiers
  (mitigated: PhiSQL identifiers are policy/dictionary/classification names, where these
  words are unlikely, and keyword matching is case-insensitive so the risk is explicit).
- **A third non-Phileas compile target.** Benchmark-query JSON joins discovery-query and
  monitoring-query JSON as shapes PhiSQL emits but Phileas does not consume — each a contract
  to version and document independently.
- **Metric semantics are a commitment.** Writing precision/recall/F1/confusion_matrix
  definitions into `metrics.yaml` means the spec now owns those definitions; if Philter Scope's
  span-matching rule differs in a subtlety (partial-span credit, entity-type confusions), the
  catalog and the engine must be reconciled or they drift. The catalog states the matching
  rule explicitly to minimize this.
- **New downstream obligation.** Philter Scope must consume the benchmark-query JSON for the
  verbs to be more than syntax — mirroring the v1.0 state where the discovery compiler had
  not yet landed.

## Backward compatibility

- **Existing `.phisql` files:** All additions are new productions guarded by new leading
  keywords; nothing previously accepted is rejected. The only behavior change is that the
  eight new keywords become reserved — a file that used one as a bare identifier name would
  need to quote it, but no such file exists in the repository or in
  `pii-redaction-policies`.
- **Existing Phileas JSON / runtime:** Untouched. Benchmarking does not compile to Phileas
  JSON and requires no runtime change.
- **Existing downstream consumers:** The discovery-query and monitoring-query JSON shapes are
  unchanged. New consumers (benchmarking engines) opt in by implementing benchmark-query
  JSON; existing consumers are unaffected.

This is a strictly-additive change.

## Versioning impact

**Minor.** The change only adds new statements, clauses, and a catalog; nothing previously
accepted is rejected (modulo the new reserved words, which collide with no existing file) and
no existing compile output changes. Per the [versioning policy](../CONTRIBUTING.md#versioning-policy),
additive, backward-compatible changes bump the minor version — this targets the **v1.1** spec
release, the same minor cycle as [RFC 0002]; the two query-surface RFCs are independent and
may be batched into one v1.1 release or split across v1.1/v1.2 at the maintainers' discretion.

## Reference implementation

Not yet implemented; to land in a follow-up PR linked from this RFC, in two parts:

1. **Grammar + catalog + examples (parse-complete).** Add the v1.1 grammar productions,
   `metrics.yaml`, the eight new reserved keywords, and the three example `.phisql`/`.json`
   pairs. `ExamplesParseTest` parses all of them; the three benchmarking examples join the
   compiler's not-yet-compiled skip set until step 2. `scripts/validate_spec.py` is extended
   to verify every metric and report dimension referenced in a benchmarking example resolves
   against `metrics.yaml`, mirroring the existing discovery-column check.
2. **Benchmarking compiler.** Implement `COMPARE`/`BENCHMARK`/`MEASURE` → benchmark-query
   JSON in the reference compiler and remove the three examples from the skip set, so the
   round-trip test asserts byte-equivalent JSON against the checked-in files.

Philter Scope's consumption of the benchmark-query JSON is tracked separately in the Philter
Scope repository and does not block acceptance of this RFC (acceptance requires the worked
examples, which are included above).

## Unresolved questions

- **`BENCHMARK` vs `MEASURE`.** This RFC accepts both as synonyms for single-policy
  evaluation. Should the spec keep both spellings, or pick one (and reserve the other for a
  distinct future meaning, e.g. `MEASURE` for a single scalar metric vs `BENCHMARK` for a
  full report)? Resolving this before acceptance avoids reserving a keyword we may want to
  repurpose.
- **Minor-version directory layout.** Shared with [RFC 0002]: there is no precedent yet for a
  minor spec version directory. Should v1.1 additions go in a new `spec/v1.1/` tree or be
  annotated in place under `spec/v1.0/`? This should be decided once and applied to both
  query-surface RFCs.
- **Confusion-matrix shape.** The catalog defines `confusion_matrix` as a `{tp, fp, fn}`
  triple (no true negatives, since the negative space for span detection is unbounded). Is
  that the shape Philter Scope actually emits, and does it need per-entity-type cells when
  combined with `PER entity_type` (i.e., a matrix per entity type)? This is the crux of
  acceptance criterion two and should be confirmed against current Philter Scope output.
- **Dataset addressing.** Datasets are opaque engine-resolved names here. Should the spec
  define a dataset catalog or naming convention, or is engine resolution sufficient?
- **Thresholding.** Should `REPORT` support a confidence threshold (e.g.
  `REPORT precision, recall AT CONFIDENCE 0.8`) so a policy can be scored at a chosen operating
  point, or is that out of scope until a concrete need appears?

## Future possibilities

These are explicitly **out of scope** for this RFC but become reachable once the surface
above exists:

- **More metrics** (`specificity`, `support`, `f_beta`) added to `metrics.yaml` without a
  grammar change.
- **More `PER` dimensions** (per dataset slice, per source, per confidence bucket).
- **URI-addressed datasets** via `sources.yaml`, for ad-hoc benchmarking against a raw
  labeled corpus in object storage.
- **A pass/fail gate** (`COMPARE ... REQUIRE recall >= 0.95`) so benchmarking can run in CI
  and fail a policy change that regresses detection — the natural pairing with the
  cross-tool query verbs the README anticipates.
- **Comparing more than two policies** in one statement (a leaderboard over a policy set).

[RFC 0002]: 0002-monitoring-query-verbs.md
[philterd/philterd-website#124]: https://github.com/philterd/philterd-website/issues/124
[philterd/philterd-website#123]: https://github.com/philterd/philterd-website/issues/123
[philterd/philterd-website#122]: https://github.com/philterd/philterd-website/issues/122
