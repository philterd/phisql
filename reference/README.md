# PhiSQL Reference Implementation

The reference parser and AST library for the [PhiSQL specification](../spec/).

The parser is generated from [`spec/v1.0/grammar/PhiSQL.g4`](../spec/v1.0/grammar/PhiSQL.g4) at build time. The grammar file lives in the spec; this directory is a consumer. There is no separate grammar source in `reference/`.

## Coordinates

```xml
<dependency>
    <groupId>ai.philterd</groupId>
    <artifactId>phisql</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Build

```sh
mvn verify
```

The build:

1. Generates a lexer and parser from `../spec/v1.0/grammar/PhiSQL.g4` into the `ai.philterd.phisql.grammar` package.
2. Compiles the wrapper `PhiSQL` class.
3. Runs `ExamplesParseTest`, which parses every `.phisql` file under `../spec/v1.0/examples/` and asserts it produces no syntax errors.

The example-parsing test is the load-bearing assertion that the reference implementation stays in sync with the spec. Any grammar change that breaks an example, or any new example that the grammar can't parse, fails the build.

## Usage

### Parse

```java
import ai.philterd.phisql.PhiSQL;
import ai.philterd.phisql.grammar.PhiSQLParser;

PhiSQLParser.DocumentContext tree = PhiSQL.parse(
    "POLICY ssn_only; REDACT SSN WITH MASK;"
);
// tree is the ANTLR4 parse tree. Use a Visitor or Listener to walk it.
```

### Compile to Phileas JSON

```java
import ai.philterd.phisql.Compiler;
import ai.philterd.phisql.CompileResult;

Compiler compiler = new Compiler();
CompileResult result = compiler.compile(
    "POLICY hipaa_safe_harbor;\n" +
    "DEIDENTIFY SSN AS REDACT, DATE AS TRUNCATE, EMAIL_ADDRESS AS MASK;"
);

System.out.println(result.policyName());   // "hipaa_safe_harbor"
System.out.println(result.toJsonString()); // Phileas JSON policy
```

The compiler is driven by the catalog YAML files under `spec/v1.0/catalog/`. They are bundled inside the JAR as resources, so the compiler does not depend on the spec being checked out at runtime.

### Compile from a file

```java
Path file = Path.of("policies/hipaa-safe-harbor.phisql");
CompileResult result = compiler.compile(file);

// Policy name comes from the file basename.
result.policyName();  // "hipaa-safe-harbor"
```

The policy name comes from the filename basename. A `POLICY` declaration inside the file is optional; when present, its name must match the basename after hyphen/underscore normalization (so a file named `hipaa-safe-harbor.phisql` may declare `POLICY hipaa_safe_harbor`). The compiler raises a `CompileException` on mismatch.

This rule is defined in [`spec/v1.0/catalog/policy.yaml`](../spec/v1.0/catalog/policy.yaml).

## License

Apache License, Version 2.0. See [LICENSE](../LICENSE).
