# Using PhiSQL

PhiSQL is a specification, and the rest of this site defines the language. This page
covers the practical step the spec deliberately leaves out: turning a PhiSQL document into
a Phileas policy you can actually apply.

A PhiSQL document compiles to a
[Phileas redaction policy](https://philterd.ai/schemas/redaction-policy/1.0.0/schema.json).
Once compiled, the policy is applied by Phileas or Philter like any other policy. Nothing
downstream needs to know the policy was authored in PhiSQL.

## Reference implementations

Three implementations produce identical output from the same input.

| Language | Package | Availability |
|---|---|---|
| Java | `ai.philterd:phisql` | Maven Central |
| .NET | `Philterd.PhiSql` | NuGet |
| Python | `phisql` | PyPI |

Implementation versions and the schema version move independently. See the
[compatibility table](https://github.com/philterd/phisql#reference-implementation-compatibility)
for which implementation release targets which schema version.

## Compiling a document

Given `ssn_only.phisql`:

```sql
POLICY ssn_only;

REDACT SSN WITH MASK;
```

### Command line

The Python implementation ships a `phisql` command that compiles a file and writes the
policy to stdout:

```sh
phisql ssn_only.phisql
```

```json
{
  "identifiers": {
    "ssn": {
      "ssnFilterStrategies": [
        {
          "strategy": "MASK"
        }
      ]
    }
  }
}
```

Redirect it to a file to hand the result to Philter or Phileas:

```sh
phisql ssn_only.phisql > ssn_only.json
```

### From Python

```python
from phisql import Compiler

result = Compiler().compile("POLICY ssn_only; REDACT SSN WITH MASK;")

result.policy_name()      # "ssn_only"
result.to_json_string()   # the Phileas JSON policy
```

Install the package from PyPI:

```sh
pip install phisql
```

### From Java

Add `ai.philterd:phisql` from Maven Central. Phileas can also load PhiSQL directly with
`Policy.fromPhiSQL(...)`, which compiles the document and applies the resulting policy in
one step, so a Java caller does not have to handle the JSON at all.

## Checking your work

Every construct on this site has a
[worked example](examples/index.md) paired with the policy JSON it compiles to. When a
statement does not produce what you expected, the example for that construct is the
fastest way to see the intended output.

CI in the specification repository parses every example with all three implementations and
validates the compiled JSON against the Phileas schema, so the examples and the language
cannot drift apart.

## Reporting a problem

A compiler that produces the wrong JSON for a documented construct is a bug in that
implementation. A gap in the language itself, or a change to the grammar, schema, or
catalogs, goes through the RFC process described in
[CONTRIBUTING.md](https://github.com/philterd/phisql/blob/main/CONTRIBUTING.md). Both start
as an issue in [philterd/phisql](https://github.com/philterd/phisql/issues).
