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

Each implementation has a command-line front end that compiles a file and writes the
policy to stdout. The Python package installs it as the `phisql` command:

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

The Java implementation publishes a self-contained jar alongside the library, with the
`cli` classifier (`phisql-<version>-cli.jar`):

```sh
java -jar phisql-<version>-cli.jar ssn_only.phisql
```

The .NET implementation includes a `PhiSql.Cli` project in the
[repository](https://github.com/philterd/phisql/tree/main/reference/dotnet):

```sh
dotnet run --project PhiSql.Cli -- ssn_only.phisql
```

All three use the same exit codes: `0` compiled, `2` parse error, `3` compile error,
`64` usage error, and `1` for other I/O errors.

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

## Compile warnings

Some valid PhiSQL compiles correctly but does not behave the same in every Phileas
runtime. The compilers report these cases as warnings without failing. Today the only
warnings are for a `WHERE` clause that uses `OR` or parentheses: only phileas-python
evaluates them, and the Java and .NET runtimes do not support them yet (RFC #15).

```sql
REDACT SSN WITH LAST_4 WHERE CONFIDENCE > 0.9 OR CONFIDENCE < 0.2;
```

```text
warning: WHERE uses OR, which only phileas-python evaluates today; the Java and .NET Phileas runtimes do not support it yet (RFC #15).
```

On the command line, warnings are printed to stderr as `warning: ...` lines, so they do not
mix with the policy on stdout. A warning does not change the compiled policy or the exit
code. From code, read them from the compile result: `result.warnings()` in Python and Java,
`result.Warnings` in .NET. The list is empty when there are none.

If you apply the policy with the Java or .NET runtime, rewrite the condition without `OR`
or parentheses, for example as separate statements with their own `WHERE` clauses.

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
