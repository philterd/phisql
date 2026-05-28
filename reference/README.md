# PhiSQL Reference Implementation

The reference parser and AST library for the [PhiSQL specification](../spec/).

The parser is generated from [`spec/v0.1/grammar/PhiSQL.g4`](../spec/v0.1/grammar/PhiSQL.g4) at build time. The grammar file lives in the spec; this directory is a consumer. There is no separate grammar source in `reference/`.

## Coordinates (planned)

```xml
<dependency>
    <groupId>ai.philterd</groupId>
    <artifactId>phisql</artifactId>
    <version>0.1-draft-SNAPSHOT</version>
</dependency>
```

> [!IMPORTANT]
> Pre-1.0. The API may change. Maven Central publication is gated on PhiSQL v1.0.

## Build

```sh
mvn verify
```

The build:

1. Generates a lexer and parser from `../spec/v0.1/grammar/PhiSQL.g4` into the `ai.philterd.phisql.grammar` package.
2. Compiles the wrapper `PhiSQL` class.
3. Runs `ExamplesParseTest`, which parses every `.phisql` file under `../spec/v0.1/examples/` and asserts it produces no syntax errors.

The example-parsing test is the load-bearing assertion that the reference implementation stays in sync with the spec. Any grammar change that breaks an example, or any new example that the grammar can't parse, fails the build.

## Usage

```java
import ai.philterd.phisql.PhiSQL;
import ai.philterd.phisql.grammar.PhiSQLParser;

PhiSQLParser.DocumentContext tree = PhiSQL.parse(
    "POLICY ssn_only; REDACT SSN WITH MASK;"
);
// tree is the ANTLR4 parse tree. Use a Visitor or Listener to walk it.
```

## License

Apache License, Version 2.0. See [LICENSE](../LICENSE).
