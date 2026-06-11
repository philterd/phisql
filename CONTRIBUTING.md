# Contributing to PhiSQL

PhiSQL is a specification *and* a reference implementation, so changes that touch the grammar, the catalogs, or the compile semantics have a wider blast radius than a typical code change: they ripple into every downstream Philterd tool that consumes the spec. To keep the spec moving without fragmenting it, all such changes go through a lightweight **RFC** (Request for Comments) process described below.

Bug fixes, documentation tweaks, new test cases, and clarifications that do not change observable spec behavior do **not** need an RFC. Open a normal pull request.

## Table of contents

- [What needs an RFC](#what-needs-an-rfc)
- [What does not need an RFC](#what-does-not-need-an-rfc)
- [Changing the schema](#changing-the-schema)
- [How to open an RFC](#how-to-open-an-rfc)
- [Lifecycle](#lifecycle)
- [Deciding and implementing](#deciding-and-implementing)
- [Versioning policy](#versioning-policy)
- [Code of conduct](#code-of-conduct)

> **Process scope.** While Philterd is the sole maintainer, the RFC process is
> deliberately minimal: an RFC is a **GitHub issue** — a short design note opened
> with the [RFC proposal form](.github/ISSUE_TEMPLATE/rfc.yml) — and CI, not a
> review committee, is the gate. There is no review window and no approval quorum.
> The heavier multi-party review returns, via its own RFC, once a third party
> ships a conforming implementation. The value the RFC keeps even for one person
> is the **written rationale** and the **discipline of the core questions** in
> [Deciding and implementing](#deciding-and-implementing).

## What needs an RFC

The redaction policy schema under [`schema/`](schema/) is the canonical contract; changes are proposed against it. File an RFC for any change that:

- **Adds, removes, or modifies the redaction policy schema** under `schema/` — a new entity type, strategy, field, constraint, or enum value. This changes the contract itself; the catalog, grammar, and reference implementation follow from it. A backward-incompatible schema change is a new schema version (a new `schema/<version>/` directory).
- Adds, removes, or modifies grammar productions in `spec/v1.0/grammar/PhiSQL.g4` or `PhiSQL.ebnf`.
- Changes the catalog files in `spec/v1.0/catalog/` in a way that alters what a conforming compiler must accept or reject (adding an entity type, changing a strategy's allowed arguments, reserving a new keyword).
- Changes how PhiSQL compiles to Phileas JSON (the compile contract documented under `catalog/`).
- Introduces a new statement, clause, or predicate form.
- Defers, retires, or renames an existing language feature.
- Adjusts the policy-naming rule, file-layout convention, or any other normative behavior that downstream consumers rely on.

When in doubt, err toward writing one — it is a short note, and the written rationale is the point.

## What does not need an RFC

Open a normal PR for:

- Typo, grammar, and formatting fixes in any document.
- New worked examples under `spec/v1.0/examples/` that exercise *already-specified* grammar.
- Additional reference-implementation tests that lock down *already-specified* behavior.
- Reference-implementation refactoring that does not change observable compile behavior.
- CI/workflow changes that do not affect what the spec accepts or produces.
- Bug fixes where the spec is unambiguous and the implementation diverged from it. (Reference the spec section the fix restores.)

## Changing the schema

The schema under [`schema/`](schema/) is the source of truth for the policy contract, so a change to what a valid policy looks like is, first and foremost, a schema change. An RFC for such a change must:

1. **Update the schema.** Edit `schema/<version>/schema.json` for an additive (backward-compatible) change, or add a new `schema/<new-version>/schema.json` for a backward-incompatible one, bumping the `version` field and `$id` to match.
2. **Update PhiSQL to match.** Reflect the change in the catalog (`spec/v1.0/catalog/`), the grammar, and the reference compiler so PhiSQL can express it and still compiles to valid policy JSON. CI validates every example against the schema in `schema/`.
3. **Account for the runtime.** The schema must not declare anything the Phileas runtime does not implement. Phileas downloads the published schema and embeds it, and a conformance test there fails the build if the schema and the engine drift apart — so a schema addition is complete only once Phileas implements it.

The canonical source is `schema/` in this repository. The copy published at `https://philterd.ai/schemas/redaction-policy/<version>/schema.json` is kept in sync with it; do not edit the published copy directly.

## How to open an RFC

An RFC is a GitHub issue. The issue *is* the RFC — there is no committed RFC file.

1. **Open an issue** with the [RFC proposal form](.github/ISSUE_TEMPLATE/rfc.yml) ("New issue" → "RFC proposal"), which applies the `phisql-rfc` label. The issue number is the RFC's identifier.
2. **Answer the core questions** the form asks: the problem it solves, the exact schema/grammar/catalog delta, whether it is backward-compatible and which version bump it triggers ([minor or major](#versioning-policy)), whether the Phileas runtime supports it, and at least one worked example with its compiled Phileas JSON.
3. **Discuss in the issue thread.** Revise the description as the design firms up; the issue and its comments are the record of how it evolved.

Implementation is a separate, normal pull request — see [Deciding and implementing](#deciding-and-implementing).

## Lifecycle

An RFC is tracked by its issue state and labels:

| State | Meaning |
|-------|---------|
| **Open** (`phisql-rfc`) | Proposed and under consideration. |
| **Accepted** (`phisql-rfc` + `accepted`) | The design is approved; the issue stays open until the implementing PR closes it, then it is closed as completed. |
| **Closed, not planned** | Declined or withdrawn, with a comment stating why. |

There is no fixed review window — accept when you are satisfied, or leave the issue open for comment as long as you like.

## Deciding and implementing

While Philterd is the sole maintainer, **accept** an RFC by adding the `accepted` label once you are satisfied the design answers the core questions below. No approval quorum, no waiting period. (Once a third party ships a conforming implementation, a review window and shared merge authority return, established by their own RFC.)

**Implement** in a normal pull request that references the issue and closes it on merge (`Closes #N`). The PR carries the change — schema, catalog, grammar, the Java and Python reference implementations, and examples — and CI is the reviewer: `validate_spec.py`, the conformance suite, and the accept-case schema check must pass. The issue and its discussion are the durable record of *why*; the merged PR is the record of *what*.

Weigh every proposal against these — the questions that actually catch breakage:

1. **Necessity.** Is there a real problem? Could it be solved without a spec change (a library or convention)?
2. **Phileas-JSON representability.** Does it compile to existing Phileas JSON, or need a Phileas runtime change? The latter raises the bar — "the schema leads; PhiSQL follows."
3. **Backward compatibility.** Does it break existing `.phisql` files or existing Phileas JSON policies? If so it is a major bump and needs a migration story.
4. **Spec clarity.** Is the `schema/<version>/schema.json` delta well-formed? Does the EBNF match the ANTLR grammar, and the catalog match the schema?
5. **Coverage.** Are there worked examples that round-trip through the reference compilers?
6. **Alternatives.** Was the design space genuinely explored, or just the first idea?

## Versioning policy

The PhiSQL spec versions live under `spec/v<MAJOR>.<MINOR>/`. There is no patch level on the spec itself — patch-level fixes to text, comments, or example files do not change the version. The reference implementation is versioned independently and follows standard SemVer.

The redaction policy schema is versioned independently of the PhiSQL spec, under `schema/<version>/`. An additive, backward-compatible change edits the current `schema/<version>/schema.json` in place. A backward-incompatible change mints a new `schema/<version>/` directory with the `version` field and `$id` bumped; the previous version stays published so existing policies keep validating. The Phileas version → schema version mapping is recorded in the Phileas README.

A **minor** version bump (`v1.0` → `v1.1`) is warranted when an Accepted RFC:

- Adds a new statement, clause, predicate, entity type, or strategy.
- Adds a new optional argument to an existing strategy.
- Relaxes a previous restriction (formerly-rejected input is now accepted).
- Adds a new catalog file or new fields to an existing one in a backward-compatible way.

A **major** version bump (`v1.x` → `v2.0`) is warranted when an Accepted RFC:

- Removes or renames any existing statement, clause, entity, or strategy.
- Tightens a previous permissive rule (formerly-accepted input is now rejected).
- Changes the compiled Phileas JSON output for an existing valid PhiSQL input.
- Reserves a new keyword that could have been used as an identifier in a prior version.
- Changes the policy-naming, file-layout, or any other normative convention downstream consumers rely on.

As of the `v1.0` release the compatibility contract is in force: the spec is no longer a draft, the rules above are binding, and a breaking change requires a major version bump rather than landing within a minor version.

Each accepted RFC notes which kind of bump it requires (in the issue); accepted changes are bundled into the next version following these rules.

## Code of conduct

This project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). Be kind, assume good faith, and focus on the proposal rather than the proposer.
