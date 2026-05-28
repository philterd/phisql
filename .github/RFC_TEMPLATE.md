---
rfc: NNNN
title: <short summary, sentence case, no trailing period>
status: Draft
author: <your name> <your-handle>
created: YYYY-MM-DD
target_version: v0.X
versioning_impact: minor | major
---

# RFC NNNN: <short summary>

## Motivation

What problem does this RFC solve? Why does it need to be solved in the spec rather than at a higher layer (a library, a convention, a downstream tool)?

Concrete user stories or real-world policy files that are awkward or impossible to express today are far more persuasive than abstract concerns. Link to issues, prior discussion, or upstream Phileas behavior where relevant.

If a workaround exists, describe it and explain why it is insufficient.

## Proposed grammar changes

The exact additions, removals, or modifications to `spec/v0.1/grammar/PhiSQL.g4` and `PhiSQL.ebnf`. Show the relevant productions before and after.

```antlr
// Before
ignoreStmt
    : IGNORE TERMS '(' termList ')' (FOR entityList)?
    ;

// After
ignoreStmt
    : IGNORE TERMS '(' termList ')' (FOR entityList)?  // FOR optional; scope-less form lands in top-level `ignored`
    ;
```

If the RFC introduces a new catalog file or modifies an existing one, show the diff or the new schema.

If the RFC changes the compile-to-Phileas-JSON contract, describe the new mapping in the same terms used by `spec/v0.1/catalog/*.yaml`.

## Examples

At least one worked PhiSQL example demonstrating the new construct, with the compiled Phileas JSON beside it. More examples are better, especially edge cases.

PhiSQL:

```sql
POLICY my_example;

-- demonstrate the new construct
```

Compiled Phileas JSON:

```json
{
  "name": "my_example",
  "..."
}
```

If the RFC is accepted, these examples land under `spec/v<target_version>/examples/` and become part of the reference test suite.

## Alternatives considered

What other designs were considered? Why was the proposed design chosen over them?

This section is required — even if the answer is "the obvious shape is the right shape." Document the design space so future readers understand why the spec looks the way it does.

For each alternative, briefly state:

- The alternative design.
- Why it was rejected (worse ergonomics, harder to compile, breaks compatibility, conflicts with Phileas, etc.).

## Drawbacks

Why might this RFC be a bad idea? Honest, specific drawbacks build trust.

Common categories:

- Increases grammar surface area / learning curve.
- Adds a Phileas dependency the spec didn't previously have.
- Creates ambiguity with existing constructs.
- Forces downstream implementations to do significant new work.

## Backward compatibility

Does this change break:

- Existing `.phisql` files that parse under the current grammar?
- Existing Phileas JSON policies the spec compiles to?
- Existing downstream consumers (Phileas, Phinder, etc.)?

If yes to any, what is the migration path? Can the old behavior be retained behind a flag? What is the deprecation timeline?

## Versioning impact

Required: state whether acceptance triggers a minor or major spec version bump, with one-sentence justification per the rules in [CONTRIBUTING.md](../CONTRIBUTING.md#versioning-policy).

## Reference implementation

Optional but encouraged. Link to a draft PR, a branch, or pseudocode showing how the reference compiler in `reference/` would implement the change. If the change is purely a grammar relaxation, note that.

## Unresolved questions

Anything the author wants reviewers to specifically weigh in on. Listing open questions is not a weakness — it focuses the discussion.

## Future possibilities

Optional. Adjacent constructs this RFC enables but does not propose. Helps reviewers see the broader trajectory without expanding the scope of this RFC.
