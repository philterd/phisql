# PhiSQL RFCs

This directory holds the historical record of accepted, rejected, and withdrawn RFCs (Requests for Comments) that have shaped the PhiSQL specification.

For the RFC process itself — when to file one, the template, the lifecycle, and the review criteria — see [../CONTRIBUTING.md](../CONTRIBUTING.md).

## Index

| Number | Title                                                                                | Status   | Target  |
|--------|--------------------------------------------------------------------------------------|----------|---------|
| [0001](0001-scope-less-ignore-terms.md) | Allow scope-less `IGNORE TERMS` to compile to top-level `ignored` | Accepted | v0.1    |
| [0002](0002-monitoring-query-verbs.md) | Monitoring query verbs over Phield trend and alert data | Draft | v1.1    |
| [0003](0003-benchmarking-query-verbs.md) | Benchmarking query verbs over Philter Scope policy evaluations | Draft | v1.1    |
| [0004](0004-cross-tool-join-semantics.md) | Cross-tool join semantics across the Philterd toolkit | Draft | v1.2    |
| [0005](0005-required-strategy-arguments.md) | Enforce required strategy arguments at compile time | Draft | v2.0    |

## Numbering

RFCs are numbered sequentially in the order they are *assigned*, not in the order they are accepted. Numbers are zero-padded to four digits (`0001`, `0042`, `0123`). Withdrawn numbers are retired, not re-used, so the historical record remains stable.

The next available number is assigned by a maintainer when the originating issue is filed with the `phisql-rfc` label.
