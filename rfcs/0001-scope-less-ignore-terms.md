---
rfc: 0001
title: Allow scope-less `IGNORE TERMS` to compile to top-level `ignored`
status: Accepted
author: Jeff Zemerick <jzonthemtn>
created: 2026-05-28
target_version: v0.1
versioning_impact: minor
---

# RFC 0001: Allow scope-less `IGNORE TERMS` to compile to top-level `ignored`

> This RFC is included in the repository as the **worked reference example** for the PhiSQL RFC process. It documents a real change that was accepted in commit [5e86cb2](https://github.com/philterd/phisql/commit/5e86cb2). Future authors can use it as a model for how an RFC should look end-to-end.

## Motivation

The Phileas JSON policy schema supports a top-level `ignored` array of objects, each of which carries a `terms` list (and optionally a name, case-sensitivity flag, and pattern). Phileas applies these ignored terms across **every** filter in the policy at runtime — they are policy-wide allowlist entries, not per-entity ones.

`philterd/pii-redaction-policies` uses this construct in several published policies to suppress common false-positive strings (`TEST`, `EXAMPLE`, `SAMPLE`, organization-specific placeholders) that would otherwise trigger redaction across multiple entity types. Without a way to express it in PhiSQL, those policies cannot be authored in PhiSQL — defeating the convenience-authoring-layer goal stated in the README.

The PhiSQL v0.1 draft already had grammar for `IGNORE TERMS (...) FOR <entity>`, which compiles to a per-entity `ignored` entry. The omission was that the grammar accepted `IGNORE TERMS (...)` *without* a `FOR` clause and the compiler rejected it, even though the natural compile target — top-level `ignored` — already exists in Phileas JSON.

This is a small, additive change: relax the compiler to accept the scope-less form rather than rejecting it.

## Proposed grammar changes

No change to `PhiSQL.g4` or `PhiSQL.ebnf` is required. The grammar already makes `FOR entityList` optional:

```antlr
ignoreStmt
    : IGNORE
      ( TERMS stringList
      | PATTERN STRING_LITERAL
      )
      (FOR entityList)?
    ;
```

The change is to the **compiler contract** documented in `spec/v1.0/catalog/` and enforced by the reference compiler:

- **Before:** `IGNORE TERMS (...)` without a `FOR` clause raised a `CompileException`.
- **After:** `IGNORE TERMS (...)` without a `FOR` clause compiles to one entry appended to the top-level `ignored` array of the Phileas JSON output, in the `{ "terms": [...] }` object shape defined by `$defs.ignored` in the Phileas schema.

The existing scoped form (`IGNORE TERMS (...) FOR <entity>`) is unchanged: it continues to compile to a per-entity ignored entry.

## Examples

PhiSQL source (`spec/v1.0/examples/11-policy-wide-ignore-terms.phisql`):

```sql
-- Policy-wide ignore terms. Without a FOR <entity> clause, IGNORE TERMS
-- compiles to the top-level `ignored` array in the Phileas schema and
-- applies across all filters in the policy.

POLICY suppress_known_test_data;

REDACT SSN, EMAIL_ADDRESS WITH MASK;

IGNORE TERMS ('TEST', 'EXAMPLE', 'SAMPLE');
```

Compiled Phileas JSON (`spec/v1.0/examples/11-policy-wide-ignore-terms.json`):

```json
{
  "identifiers": {
    "ssn": {
      "ssnFilterStrategies": [
        { "strategy": "MASK" }
      ]
    },
    "emailAddress": {
      "emailAddressFilterStrategies": [
        { "strategy": "MASK" }
      ]
    }
  },
  "ignored": [
    {
      "terms": ["TEST", "EXAMPLE", "SAMPLE"]
    }
  ]
}
```

The example file landed alongside the implementation and is exercised by `CompilerTest`, which asserts byte-equivalent JSON output against the checked-in `.json` file.

## Alternatives considered

**Alternative 1: Require an explicit policy-wide scope keyword.**

Something like `IGNORE TERMS (...) FOR ALL;` or `IGNORE TERMS (...) GLOBALLY;` to make the policy-wide nature visually distinct from the per-entity form.

Rejected because: the *absence* of a `FOR` clause already reads naturally as "no scope restriction." Adding ceremony to express the default makes the language wordier without disambiguating anything (there is no third possible scope). It would also introduce a new reserved keyword for no semantic gain.

**Alternative 2: Compile scope-less `IGNORE TERMS` to per-entity entries on every declared entity.**

Mechanically expand `IGNORE TERMS (...)` to one ignored entry per filter in the policy.

Rejected because: it produces verbose JSON that differs from the natural hand-written Phileas policy, breaks round-tripping with the published `pii-redaction-policies` corpus, and silently changes meaning if the policy later adds a new entity (the new entity would not inherit the ignore terms).

**Alternative 3: Make scope-less `IGNORE TERMS` a parse error and require users to enumerate every entity.**

Rejected because: this is exactly the current pre-RFC behavior and is the problem the RFC exists to solve.

## Drawbacks

- A reader of a `.phisql` file must know that omitting `FOR` means "policy-wide" rather than "this is a syntax error." This is mitigated by the worked example, which makes the convention discoverable.
- The grammar already accepted the form, so the prior `CompileException` was effectively a hidden semantic rule. Removing it tightens the gap between syntactic and semantic acceptance — a good outcome long-term but a one-time behavior change for any tool that depended on the rejection.

## Backward compatibility

- **Existing `.phisql` files:** No file in the repository or in `pii-redaction-policies` used the scope-less form (since it was rejected). No file breaks.
- **Existing Phileas JSON:** The compiled output uses an existing Phileas schema construct (`$defs.ignored`) that Phileas already validates and executes correctly. No runtime change.
- **Downstream consumers:** Anyone relying on the `CompileException` as a signal would see that signal go away. No known consumer relies on it; the exception was never documented as a stable API.

This is a strictly-additive change.

## Versioning impact

**Minor.** The change relaxes a previous restriction: input that was formerly rejected is now accepted. Per the [versioning policy](../CONTRIBUTING.md#versioning-policy), this qualifies for a minor bump. Because this RFC lands inside the same v0.1 draft cycle in which the restriction was introduced, no version increment is needed yet; the cumulative changes will be reflected in the eventual v0.1 release notes.

## Reference implementation

Landed in commit [5e86cb2](https://github.com/philterd/phisql/commit/5e86cb2) — "Add policy-naming rule, fix scope-less IGNORE TERMS, license headers". Specifically:

- `reference/src/main/java/ai/philterd/phisql/Compiler.java` — the `ignoreStmt` branch was updated to write to the top-level `ignored` array when the `FOR` clause is absent, rather than raising `CompileException`.
- `spec/v1.0/examples/11-policy-wide-ignore-terms.phisql` and `.json` — the worked example.
- `reference/src/test/java/ai/philterd/phisql/CompilerTest.java` — picks up the new example via the existing parameterized round-trip test (no new test method needed).

## Unresolved questions

None at acceptance time. One follow-up worth tracking but explicitly *out of scope* for this RFC:

- Phileas's `ignored` schema also supports `caseSensitive` and `pattern` fields. PhiSQL has no syntax for those today. A future RFC could extend the `IGNORE` statement with options like `IGNORE TERMS (...) CASE INSENSITIVE` or `IGNORE PATTERN '<regex>'` (the latter grammar already exists; the compile target needs definition).

## Future possibilities

- A scope-less `IGNORE PATTERN '<regex>'` form, mirroring the scope-less `IGNORE TERMS` accepted here. The grammar already permits it; only the compile mapping needs to be specified.
- A named ignored entry (`IGNORE TERMS (...) AS 'known-test-data'`) compiling to the `name` field of the Phileas `ignored` object, to aid debugging of which suppression matched at runtime.
