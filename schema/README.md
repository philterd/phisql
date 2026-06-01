# Phileas Policy JSON Schema

A [JSON Schema (Draft 2020-12)](https://json-schema.org/) for Phileas redaction policy files. It covers all supported filter types, strategies, and configuration options.

Use it for validation in CI, editor autocompletion, or as a reference for the policy format.

## Versioning

The schema is versioned. The version appears both in the schema's `$id` URL and in a top-level `version` field, for example:

```json
{
  "$id": "https://www.philterd.ai/schemas/redaction-policy/1.0.0/schema.json",
  "version": "1.0.0"
}
```

There is a one-to-one relationship between a Phileas release and the schema version it understands: a given build of Phileas supports exactly one schema version, the version of the schema bundled with that build. Any backward-incompatible change to the schema is a new version.

This repository is the canonical home of the schema: each version is authored under `schema/<version>/schema.json` (for example, [`1.0.0/schema.json`](1.0.0/schema.json)). It is published to `https://philterd.ai/schemas/redaction-policy/<version>/schema.json`, which serves the same file for editor and runtime consumption. Phileas consumes the published copy at build time (the version is the `redaction.policy.schema.version` Maven property in its `pom.xml`) and embeds it in the jar, so the Phileas runtime reads the same schema it was built against.

## Reading the supported version from Phileas

The version is exposed at runtime through the `ai.philterd.phileas.policy.PolicySchema` API, which reads the schema embedded in the jar:

```java
import ai.philterd.phileas.policy.PolicySchema;

String version = PolicySchema.getSupportedSchemaVersion(); // e.g. "1.0.0"
String schema  = PolicySchema.getSchema();                 // the full schema JSON
```

## Editor Support

Add this to the top of your policy JSON file to enable autocompletion and inline validation in supported editors (VS Code, IntelliJ, etc.):

```json
{
  "$schema": "https://www.philterd.ai/schemas/redaction-policy/1.0.0/schema.json",
  ...
}
```

## Validating a Policy

A policy is an ordinary JSON file; validate it against the in-repo schema with any JSON Schema (Draft 2020-12) validator. For example, with [`check-jsonschema`](https://github.com/python-jsonschema/check-jsonschema):

```bash
pip install check-jsonschema
check-jsonschema --schemafile schema/1.0.0/schema.json my-policy.json
```

Validate multiple files at once:

```bash
check-jsonschema --schemafile schema/1.0.0/schema.json policy1.json policy2.json
```

To validate the spec's own catalogs and examples against this schema (the check CI runs), use [`scripts/validate_spec.py`](../scripts/validate_spec.py) — see the repository [README](../README.md#validation).
