---
rfc: 0005
title: Enforce required strategy arguments at compile time
status: Draft
author: Jeff Zemerick <jzonthemtn>
created: 2026-06-08
target_version: v2.0
versioning_impact: major
---

# RFC 0005: Enforce required strategy arguments at compile time

> Number `0005` is provisional pending maintainer assignment. Originates from
> [philterd/philterd-website#226](https://github.com/philterd/philterd-website/issues/226)
> and the "Known underspecified areas" note in
> [`compliance/README.md`](../compliance/README.md), which states this contract
> should be tightened via "an RFC plus a reference change."

## Motivation

`spec/v1.0/catalog/strategies.yaml` marks the `value` argument of
`STATIC_REPLACE` as `required: true` (it maps to the Phileas `staticReplacement`
field). A static replacement with nothing to substitute is not a well-formed
redaction: there is no value to write in place of the detected entity.

The reference compiler does not enforce this. Today:

```sql
REDACT SURNAME WITH STATIC_REPLACE(scope=document);
```

compiles successfully (exit 0) and emits a `STATIC_REPLACE` strategy object with
no `staticReplacement` field, instead of being rejected for the missing required
argument.

This is one of two gaps the conformance suite deliberately leaves unpinned under
**Known underspecified areas** in `compliance/README.md`. The suite "should only
assert behavior the spec defines unambiguously," and because the reference does
not enforce the catalog's `required` marking, the suite neither accepts nor
rejects the form. The note explicitly anticipates this RFC: *"When the contract
is tightened (an RFC plus a reference change), matching cases should be added
here."*

The fix cannot be a silent bug-fix PR. The catalog's `required` marking is
currently unenforced *and* the conformance suite treats the behavior as
unsettled rather than as a clear implementation divergence, so formalizing the
tightening through the RFC process — and deciding its versioning impact — is the
correct path. This RFC also establishes the general rule (enforce *any* required
strategy argument), with `STATIC_REPLACE.value` as the first and currently only
instance.

## Proposed schema changes

N/A — no schema change. The Phileas `staticReplacement` field already exists and
its semantics are unchanged. This RFC changes only what the PhiSQL compiler
*requires the author to supply*, not the shape of the compiled policy.

## Proposed grammar changes

N/A — no grammar change. `strategy args` already permits `value` to be supplied;
the grammar cannot express "this named argument is mandatory" and is not the
right layer to. The change is to the **compile contract** documented by
`spec/v1.0/catalog/strategies.yaml` and enforced by the reference compiler.

The catalog already carries the normative marking; this RFC makes it binding:

```yaml
# spec/v1.0/catalog/strategies.yaml  (unchanged — already present)
- name: STATIC_REPLACE
  phileas_enum: STATIC_REPLACE
  description: Replace every match with a fixed value.
  args:
    - name: value
      phileas_field: staticReplacement
      type: string
      required: true        # <-- currently unenforced; this RFC enforces it
    - name: scope
      phileas_field: replacementScope
      type: enum
      enum_values: [DOCUMENT, CONTEXT]
```

New compile contract:

- **Before:** a strategy missing a `required` argument compiles, emitting a
  strategy object without the corresponding Phileas field.
- **After:** a strategy missing a `required` argument is a compile-time
  (semantic) error naming the strategy and the missing argument. This applies to
  both the no-argument-list form (`STATIC_REPLACE`) and the partial form
  (`STATIC_REPLACE(scope=document)`).

## Examples

**Rejected — missing required `value`:**

```sql
POLICY static_missing_value;

REDACT SURNAME WITH STATIC_REPLACE(scope=document);
```

Compile result:

```
error: STATIC_REPLACE requires argument 'value'
```

**Accepted — `value` supplied:**

```sql
POLICY static_with_value;

REDACT SURNAME WITH STATIC_REPLACE(value='[REDACTED]');
```

Compiled Phileas JSON:

```json
{
  "identifiers": {
    "surname": {
      "surnameFilterStrategies": [
        { "strategy": "STATIC_REPLACE", "staticReplacement": "[REDACTED]" }
      ]
    }
  }
}
```

If accepted, the rejected case lands as a `reject/semantic/` conformance case
under `compliance/cases/`, and the `STATIC_REPLACE` bullet is removed from the
"Known underspecified areas" section of `compliance/README.md`.

## Alternatives considered

**Alternative 1: Fix it silently as a bug, no RFC.**

The catalog already says `required: true`, so one could argue the reference
simply diverged from an unambiguous spec (the `CONTRIBUTING.md` carve-out for
"bug fixes where the spec is unambiguous and the implementation diverged from
it").

Rejected because: `compliance/README.md` explicitly calls for an RFC, and the
behavior is documented as *underspecified* rather than as a clear bug. Treating a
formerly-accepted input becoming rejected as an invisible patch would bypass the
versioning decision this RFC exists to make.

**Alternative 2: Leave the form permissive.**

Continue accepting `STATIC_REPLACE` with no `value`.

Rejected because: it admits malformed policies (a static replacement that
replaces with nothing) and renders the catalog's `required` marking inert and
misleading.

**Alternative 3: Validate at runtime in Phileas instead of at compile time.**

Let the policy compile and have Phileas reject or no-op it.

Rejected because: PhiSQL's value is catching authoring errors early, at compile
time, with a message that names the PhiSQL construct. Deferring to the runtime
pushes the error far from where the author can act on it.

## Drawbacks

- It is, strictly, a formerly-accepted input becoming rejected — a behavior
  change for any tool or file that relied on the permissive reference behavior.
- It introduces the first piece of "required argument" validation, which must be
  modeled in the catalog loader and the compiler (see Reference implementation).
  The mechanism should be general, not special-cased to `STATIC_REPLACE`, so the
  surface area is slightly larger than a one-line guard.

## Backward compatibility

- **Existing `.phisql` files:** any file using `STATIC_REPLACE` without a `value`
  stops compiling. Such files do not produce a meaningful redaction, so the
  practical blast radius is expected to be small, but the break is real. No
  example in this repository or in `philterd/pii-redaction-policies` uses the
  form.
- **Existing Phileas JSON policies:** unaffected. This changes only PhiSQL
  compilation; it does not alter the schema or the runtime.
- **Downstream consumers:** a consumer that accepted such PhiSQL via the
  reference compiler would now receive a `CompileException`. No consumer is known
  to depend on the permissive behavior.

## Versioning impact

**This is the central question the RFC must settle; the frontmatter records the
conservative reading.**

- **Conservative (recorded): major, `v2.0`.** Per the
  [versioning policy](../CONTRIBUTING.md#versioning-policy), "tightens a previous
  permissive rule (formerly-accepted input is now rejected)" is a major bump, and
  as of v1.0 the compatibility contract is binding.
- **Alternative reading: conformance correction, no bump.** Because
  `strategies.yaml` already declares `value` required, a maintainer may instead
  rule that the reference merely diverged from an unambiguous spec and the fix
  restores conformance without a version change.

The conformance suite's decision to leave this unpinned leans toward the former.
A maintainer ruling resolves it; this RFC defaults to `major`/`v2.0` so the
stricter consequence is the documented baseline.

## Reference implementation

The reference compiler does not model `required` today:

- `Catalog.StrategyArg` (`reference/.../Catalog.java`) is
  `record StrategyArg(String name, String phileasField, String type, List<String> enumValues)`
  — no `required` field — and the catalog loader ignores the `required:` key when
  reading `args`.
- `Compiler.compileStrategyArgs` (`reference/.../Compiler.java`) iterates only
  over the arguments that were *supplied*; it never checks for missing ones, and
  it early-returns when `strategyArgs()` is null.

Sketch of the change:

1. Add a `boolean required` component to `StrategyArg` and parse `required:` in
   the `Catalog` loader (defaulting to `false`).
2. In `compileStrategyArgs`, after binding supplied arguments, iterate
   `strategy.args()` and raise `CompileException("<STRATEGY> requires argument
   '<name>'")` for any `required` argument that was not supplied — including the
   `strategyArgs() == null` path, so the bare `STATIC_REPLACE` form is also
   rejected.
3. Add the `reject/semantic/` conformance case and a reference unit test; remove
   the resolved bullet from `compliance/README.md`.

## Unresolved questions

- **Minor vs. major (or no bump).** Is this a v2.0 tightening or a conformance
  correction? See Versioning impact. This is the one question the RFC most needs
  a ruling on.
- **Scope of "required."** `value` is the only argument currently marked
  `required` in any catalog. Should this RFC also audit the strategy catalog for
  other arguments that *ought* to be required (e.g., is any other strategy
  meaningfully incomplete without a particular argument)? Proposed answer: no —
  keep this RFC to enforcing the existing marking; propose new `required` markings
  in their own RFCs.

## Future possibilities

- The sibling underspecified gap — date-only strategies (`SHIFT`,
  `TRUNCATE_TO_YEAR`, `RELATIVE`) accepted on non-date entities — is the same
  class of "the catalog says more than the compiler enforces" problem and is
  addressed in its own RFC. The required-argument machinery introduced here does
  not solve it (it is an entity/strategy compatibility check, not an argument
  check), but both close the gap between the catalog's declared contract and what
  the reference enforces.
