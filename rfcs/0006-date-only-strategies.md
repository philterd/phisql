---
rfc: 0006
title: Enforce date-only strategies only on the DATE entity
status: Draft
author: Jeff Zemerick <jzonthemtn>
created: 2026-06-08
target_version: v2.0
versioning_impact: major
---

# RFC 0006: Enforce date-only strategies only on the DATE entity

> Number `0006` is provisional pending maintainer assignment. Originates from
> [philterd/philterd-website#225](https://github.com/philterd/philterd-website/issues/225)
> and the "Known underspecified areas" note in
> [`compliance/README.md`](../compliance/README.md). Sibling of
> [RFC 0005](0005-required-strategy-arguments.md); both close the gap between the
> catalog's declared contract and what the reference compiler enforces.

## Motivation

`spec/v1.0/catalog/strategies.yaml` classifies `SHIFT`, `TRUNCATE_TO_YEAR`, and
`RELATIVE` as date-only: each sets `phileas_strategy_def: dateFilterStrategy`,
and each description says "DATE entities only." The worked examples reinforce it
(`12-date-shift`, `21-date-relative`). Nothing in the catalog suggests these
strategies are valid on, say, `SSN`.

The reference compiler does not enforce the classification. Today:

```sql
REDACT SSN WITH SHIFT(days=30);
```

compiles successfully (exit 0), emitting a `SHIFT` strategy into
`ssnFilterStrategies` — a date transform on a non-date value that the Phileas
runtime cannot apply meaningfully.

This is the second of the two gaps the conformance suite leaves unpinned under
**Known underspecified areas** in `compliance/README.md`. The suite "should only
assert behavior the spec defines unambiguously," and because the contract here
is enforced more loosely than the catalog reads, the suite neither accepts nor
rejects the form. The note anticipates this RFC: *"When the contract is tightened
(an RFC plus a reference change), matching cases should be added here."* The
sibling gap (required strategy arguments) is [RFC 0005](0005-required-strategy-arguments.md).

## Proposed schema changes

N/A — no schema change. The Phileas `dateFilterStrategy` shape and the `date`
filter are unchanged. This RFC changes only which PhiSQL entity/strategy
*pairings* the compiler accepts.

## Proposed grammar changes

N/A — no grammar change is proposed, and this is itself a design decision (see
Alternatives). The grammar's `strategy name` production is a flat list of
strategy keywords with no notion of which entity a strategy may attach to;
encoding "date-only" syntactically would fragment the grammar by entity context
for a single special case. The constraint is better expressed as a **semantic
check** in the compiler — the same layer that already rejects unknown entity
types and invalid enum values — against the catalog's existing date-only
classification.

The change is to the **compile contract** documented by
`spec/v1.0/catalog/strategies.yaml`:

```yaml
# spec/v1.0/catalog/strategies.yaml  (unchanged — already present)
- name: SHIFT
  phileas_enum: SHIFT
  phileas_strategy_def: dateFilterStrategy   # <-- marks date-only; now binding
  description: >
    Shift a detected date ... DATE entities only.
  ...
- name: TRUNCATE_TO_YEAR
  phileas_strategy_def: dateFilterStrategy
  ...
- name: RELATIVE
  phileas_strategy_def: dateFilterStrategy
  ...
```

New compile contract:

- **Before:** a date-only strategy attaches to any entity's strategies array.
- **After:** a date-only strategy may attach only to the `DATE` entity. Applied
  to any other entity type — including a custom identifier, dictionary, or
  section — it is a compile-time (semantic) error naming the strategy and the
  offending entity.

## Examples

**Rejected — date-only strategy on a non-`DATE` entity:**

```sql
POLICY shift_on_ssn;

REDACT SSN WITH SHIFT(days=30);
```

Compile result:

```
error: SHIFT is a date-only strategy and cannot be applied to SSN
```

**Accepted — date-only strategy on `DATE` (unchanged from today):**

```sql
POLICY shift_dates;

REDACT DATE WITH SHIFT(days=30);
```

Compiled Phileas JSON:

```json
{
  "identifiers": {
    "date": {
      "dateFilterStrategies": [
        { "strategy": "SHIFT", "shiftDays": 30 }
      ]
    }
  }
}
```

If accepted, the rejected case lands as a `reject/semantic/` conformance case
under `compliance/cases/`, and the date-only bullet is removed from the "Known
underspecified areas" section of `compliance/README.md`.

## Alternatives considered

**Alternative 1: Semantic check only, no grammar change (proposed).**

Enforce the constraint in the compiler against the catalog's
`dateFilterStrategy` classification.

Chosen because: it mirrors how the compiler already reports unknown entities and
invalid enums, keeps the grammar a clean context-free surface, and needs no new
keywords or productions.

**Alternative 2: Encode date-only in the grammar.**

Split `strategy expr` so that only `DATE`'s strategy position admits `SHIFT` /
`TRUNCATE_TO_YEAR` / `RELATIVE`.

Rejected because: it couples the strategy vocabulary to entity context, bloats
the grammar (and the generated parser) for one special case, and still cannot
express the constraint for custom identifiers cleanly.

**Alternative 3: Leave the pairing permissive.**

Continue accepting date strategies on any entity.

Rejected because: it produces policies the runtime cannot honor and makes the
catalog's date-only classification inert and misleading.

## Drawbacks

- It is, strictly, a formerly-accepted input becoming rejected — a behavior
  change for any tool or file that relied on the permissive reference behavior.
- It introduces the first entity/strategy *compatibility* check. The compiler
  must learn which strategies are date-only (from the catalog) and which entity
  is `DATE`, adding a small amount of cross-cutting validation.

## Backward compatibility

- **Existing `.phisql` files:** any file applying `SHIFT`, `TRUNCATE_TO_YEAR`, or
  `RELATIVE` to a non-`DATE` entity stops compiling. Such policies do not produce
  a meaningful redaction, so the practical blast radius is expected to be small.
  No example in this repository uses such a pairing.
- **Existing Phileas JSON policies:** unaffected. This changes only PhiSQL
  compilation, not the schema or runtime.
- **Downstream consumers:** a consumer that accepted such PhiSQL via the
  reference compiler would now receive a `CompileException`. No consumer is known
  to depend on the permissive behavior.

## Versioning impact

**The central question the RFC must settle; the frontmatter records the
conservative reading** (identical in shape to RFC 0005).

- **Conservative (recorded): major, `v2.0`.** Per the
  [versioning policy](../CONTRIBUTING.md#versioning-policy), "tightens a previous
  permissive rule (formerly-accepted input is now rejected)" is a major bump, and
  as of v1.0 the compatibility contract is binding.
- **Alternative reading: conformance correction, no bump.** Because the catalog
  already classifies these strategies as date-only, a maintainer may rule that
  the reference merely diverged from an unambiguous spec.

The conformance suite's decision to leave this unpinned leans toward the former.
A maintainer ruling resolves it. RFC 0005 and this RFC should be decided together
so the two sibling tightenings land in the same version.

## Reference implementation

The reference compiler does not model date-only strategies today:

- `Catalog.Strategy` (`reference/.../Catalog.java`) is
  `record Strategy(String name, String phileasEnum, List<StrategyArg> args)` —
  the catalog's `phileas_strategy_def` is not read, so the compiler has no way to
  know a strategy is date-only.
- `Compiler.appendStrategy` (`reference/.../Compiler.java`) binds a compiled
  strategy object into the target entity's strategies array (for `REDACT` and
  `DEIDENTIFY`) without consulting the strategy's date-only status; the
  `DEFINE IDENTIFIER/DICTIONARY/SECTION` and `DETECT` handlers bind strategies to
  non-date targets the same way.

Sketch of the change:

1. Add a `boolean dateOnly` (or expose `phileas_strategy_def`) to
   `Catalog.Strategy` and set it in the loader when
   `phileas_strategy_def == "dateFilterStrategy"`.
2. At each site that binds a strategy to a target — primarily `appendStrategy`
   for `REDACT`/`DEIDENTIFY`, plus the `DEFINE`/`DETECT` strategy-binding paths —
   reject a `dateOnly` strategy whose target entity is not `DATE` with
   `CompileException("<STRATEGY> is a date-only strategy and cannot be applied to
   <ENTITY>")`.
3. Add the `reject/semantic/` conformance case and a reference unit test; remove
   the resolved bullet from `compliance/README.md`.

## Unresolved questions

- **Minor vs. major (or no bump).** Is this a v2.0 tightening or a conformance
  correction? See Versioning impact. Decide jointly with RFC 0005.
- **Custom identifiers and dictionaries.** The proposal rejects date-only
  strategies on *all* non-`DATE` targets, including custom identifiers and
  dictionaries. Is there any real use case for a date transform on a custom
  identifier whose matches are dates? Proposed answer: no — a custom identifier
  that detects dates should use the `DATE` entity or be reconsidered; keeping the
  rule simple ("`DATE` only") is preferable to a per-target allowlist.

## Future possibilities

- A general "strategy applicability" matrix in the catalog, if more
  entity/strategy constraints emerge beyond the date-only case. This RFC does not
  propose one — it enforces the single existing classification — but the
  `dateOnly` flag is the first row of what could become such a table.
