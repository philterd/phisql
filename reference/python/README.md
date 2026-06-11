# PhiSQL Reference Implementation (Python)

The Python reference parser and compiler for the [PhiSQL specification](../../spec/).
It is a sibling of the [Java reference implementation](../java/) and produces the
same Phileas JSON output for the same input.

The parser is a hand-written recursive-descent parser that mirrors
[`spec/v1.0/grammar/PhiSQL.g4`](../../spec/v1.0/grammar/PhiSQL.g4) rule-for-rule.
(The Java reference generates its parser from that grammar with ANTLR; the
Python reference transcribes it instead, keeping the dependency footprint to a
single runtime library.) The grammar file in the spec remains the source of
truth: the test suite parses every `.phisql` example in the spec, so any drift
between the grammar and this parser fails the build.

The compiler is driven by the catalog YAML files under
[`spec/v1.0/catalog/`](../../spec/v1.0/catalog/) — the same files the Java
reference, the spec validator, and the conformance suite use. There is no copy
of the catalog or grammar inside this directory; both are read from the spec.

## Requirements

- Python 3.9+
- [PyYAML](https://pyyaml.org/) (declared as a dependency)

## Install

```sh
cd reference/python
pip install -e ".[test]"
```

This must be run from a checkout of the repository, because the catalog and
schema are read from `spec/` and `schema/`. The files are located by walking up
from the package to find the repository root; set `PHISQL_SPEC_ROOT` to point at
a checkout's root if you run the package from elsewhere.

## Test

```sh
cd reference/python
pytest
```

The suite mirrors the Java reference's tests:

1. `test_examples_parse.py` parses every `.phisql` file under
   `../../spec/v1.0/examples/` and asserts it produces no syntax errors.
2. `test_compiler.py` compiles every redaction example and asserts the output
   equals the sibling `.json` file (compared as parsed JSON).

These two are the load-bearing assertions that the implementation stays in sync
with the spec: any grammar change that breaks an example, or any new example
the parser or compiler can't handle, fails the build.

## Usage

### Parse

```python
from phisql import parse

document = parse("POLICY ssn_only; REDACT SSN WITH MASK;")
# document is an AST (see phisql/ast.py). Walk it directly, or use the compiler.
```

### Compile to Phileas JSON

```python
from phisql import Compiler

result = Compiler().compile(
    "POLICY hipaa_safe_harbor;\n"
    "DEIDENTIFY SSN AS REDACT, DATE AS TRUNCATE, EMAIL_ADDRESS AS MASK;"
)

print(result.policy_name())     # "hipaa_safe_harbor"
print(result.to_json_string())  # Phileas JSON policy
```

### Compile from a file

```python
from phisql import Compiler

result = Compiler().compile_file("policies/hipaa-safe-harbor.phisql")
result.policy_name()  # "hipaa-safe-harbor" (from the filename basename)
```

The policy name comes from the filename basename. A `POLICY` declaration inside
the file is optional; when present, its name must match the basename after
hyphen/underscore normalization (so `hipaa-safe-harbor.phisql` may declare
`POLICY hipaa_safe_harbor`). The compiler raises a `CompileException` on
mismatch. This rule is defined in
[`spec/v1.0/catalog/policy.yaml`](../../spec/v1.0/catalog/policy.yaml).

### Command line

```sh
python -m phisql path/to/policy.phisql      # or: phisql path/to/policy.phisql
```

It writes the compiled Phileas JSON to stdout. Exit codes form the adapter
contract the conformance runner relies on: `0` success, `2` parse error, `3`
compile error, `64` usage error, `1` other I/O error.

## Scope

Like the Java reference, this compiler targets the redaction subset of PhiSQL
(REDACT, DEIDENTIFY, IGNORE, DEFINE IDENTIFIER, DEFINE DICTIONARY, DEFINE
SECTION, DETECT PHEYE, and the CONFIGURE forms) and emits Phileas JSON.
Discovery statements (FIND PII, DISCOVER ENTITIES, SCAN, SELECT FROM findings)
parse successfully but are not yet compiled; they target a separate
discovery-query schema.

## License

Apache License, Version 2.0. See [LICENSE](../../LICENSE).
