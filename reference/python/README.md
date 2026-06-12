# PhiSQL Reference Implementation (Python)

The Python reference parser and compiler for the [PhiSQL specification](https://github.com/philterd/phisql/tree/main/spec).
It is a sibling of the [Java reference implementation](https://github.com/philterd/phisql/tree/main/reference/java) and produces the
same Phileas JSON output for the same input.

The lexer and parser are generated from
[`spec/v1.0/grammar/PhiSQL.g4`](https://github.com/philterd/phisql/blob/main/spec/v1.0/grammar/PhiSQL.g4)
with ANTLR (the same grammar the Java reference generates from). The generated
sources are committed under [`phisql/_generated/`](phisql/_generated/) so that
installing and testing this package stays pure-Python, with no Java needed to
use it. The parser walks its parse tree into the AST the compiler consumes
(`phisql/parser.py`).

The grammar in the spec remains the single source of truth.
[`scripts/generate_parser.sh`](scripts/generate_parser.sh) regenerates the
parser from it, and CI regenerates and runs `git diff --exit-code` over
`phisql/_generated/`, so any drift between the grammar and the committed parser
fails the build. (Regenerating needs a JDK to run the ANTLR tool; using and
testing the package does not.)

The compiler is driven by the catalog YAML files under
[`spec/v1.0/catalog/`](https://github.com/philterd/phisql/tree/main/spec/v1.0/catalog) — the same files the Java
reference, the spec validator, and the conformance suite use. There is no copy
of the catalog or grammar inside this directory; both are read from the spec.

## Requirements

- Python 3.9+
- [PyYAML](https://pyyaml.org/) (declared as a dependency)
- [antlr4-python3-runtime](https://pypi.org/project/antlr4-python3-runtime/) (declared as a dependency; loads the generated parser)

A JDK is required only to *regenerate* the parser (see below), not to install,
use, or test the package.

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

## Regenerating the parser

The lexer/parser/visitor under `phisql/_generated/` are generated from
`spec/v1.0/grammar/PhiSQL.g4`. After changing the grammar, regenerate them:

```sh
cd reference/python
./scripts/generate_parser.sh
```

The script downloads the pinned ANTLR tool jar to a gitignored cache on first
run (override with `ANTLR_JAR=/path/to/antlr-complete.jar`) and needs a JDK on
`PATH`. Commit the regenerated files. CI runs the same script and fails if the
committed output differs, so the grammar stays the single source of truth.

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
[`spec/v1.0/catalog/policy.yaml`](https://github.com/philterd/phisql/blob/main/spec/v1.0/catalog/policy.yaml).

### Command line

```sh
python -m phisql path/to/policy.phisql      # or: phisql path/to/policy.phisql
```

It writes the compiled Phileas JSON to stdout. Exit codes form the adapter
contract the conformance runner relies on: `0` success, `2` parse error, `3`
compile error, `64` usage error, `1` other I/O error.

### Retrieve the policy schema

An application that depends on `phisql` can read the canonical redaction policy
JSON Schema straight from the library — no network fetch, no separate checkout —
exactly as the Java reference exposes it through `ai.philterd.phisql.PolicySchema`:

```python
from phisql import PolicySchema

PolicySchema.get_supported_schema_version()  # "1.0.0"
PolicySchema.get_schema()                    # the schema as a JSON string
PolicySchema.get_schema_dict()               # the schema parsed into a dict
```

The schema (and the catalog the compiler uses) are copied into the package at
build time — see [How the spec data is bundled](#how-the-spec-data-is-bundled) —
so these work from an installed wheel regardless of where it came from.

## How the spec data is bundled

The compiler is driven by the catalog YAML and the policy schema, both of which
live in the repository root (`spec/` and `schema/`). The build copies them into
the package at `phisql/_data/` — the Python analogue of the Maven
`copy-resources` steps that pack the same files into the Java JAR. This is done
by `setup.py` at build time, so:

- an **installed wheel** (or a Git/path install) is self-contained;
- a **source checkout** falls back to reading `spec/`/`schema/` directly, so the
  tests run without a build step;
- set `PHISQL_SPEC_ROOT` to a repository root to override the lookup explicitly.

The repository remains the single source of truth; `phisql/_data/` is a
gitignored build artifact, like the Java `target/` resources.

## Scope

Like the Java reference, this compiler targets the redaction subset of PhiSQL
(REDACT, DEIDENTIFY, IGNORE, DEFINE IDENTIFIER, DEFINE DICTIONARY, DEFINE
SECTION, DETECT PHEYE, and the CONFIGURE forms) and emits Phileas JSON.
Discovery statements (FIND PII, DISCOVER ENTITIES, SCAN, SELECT FROM findings)
parse successfully but are not yet compiled; they target a separate
discovery-query schema.

## License

Apache License, Version 2.0. See [LICENSE](https://github.com/philterd/phisql/blob/main/LICENSE).
