# PhiSQL Reference Implementation (.NET / C#)

The .NET reference parser and compiler for the [PhiSQL specification](https://github.com/philterd/phisql/tree/main/spec).
It is a sibling of the [Java](https://github.com/philterd/phisql/tree/main/reference/java)
and [Python](https://github.com/philterd/phisql/tree/main/reference/python) reference
implementations and produces the same Phileas JSON output for the same input.

The lexer and parser are generated from
[`spec/v1.0/grammar/PhiSQL.g4`](https://github.com/philterd/phisql/blob/main/spec/v1.0/grammar/PhiSQL.g4)
with ANTLR (the same grammar the Java and Python references generate from). The
generated C# sources are committed under [`PhiSql/Generated/`](PhiSql/Generated/)
so building and testing the package needs only the .NET SDK (no Java). The
parser walks its parse tree into the AST the compiler consumes (`PhiSql/Parser.cs`).
The compiler is driven by the catalog YAML under
[`spec/v1.0/catalog/`](https://github.com/philterd/phisql/tree/main/spec/v1.0/catalog),
the single source of truth shared by all three implementations.

The grammar in the spec remains the single source of truth.
[`scripts/generate_parser.sh`](scripts/generate_parser.sh) regenerates the
parser from it (it needs a JDK to run the ANTLR tool), and CI regenerates and
runs `git diff --exit-code` over `PhiSql/Generated/`, so any drift between the
grammar and the committed parser fails the build.

## Target framework

**.NET 10.0** (`net10.0`, the current LTS). Dependencies: `YamlDotNet` (catalog
parsing) and `Antlr4.Runtime.Standard` (loads the generated parser), plus, for
the test project only, `xUnit` and `JsonSchema.Net`.

## How the spec data is bundled

The catalog YAML and the policy schema JSON are **embedded into the assembly at
build time**, read directly from `spec/` and `schema/` (see the
`EmbeddedResource` items in `PhiSql/PhiSql.csproj`). This is the .NET analog of
the Maven `copy-resources` steps that pack the same files into the Java JAR and
the Python build step that copies them into the wheel: an application that
depends on `Philterd.PhiSql` gets the schema and catalog with no external files.
The schema version is selected by the `SchemaVersion` MSBuild property; keep it
in sync with `PolicySchema.SupportedSchemaVersion`.

## Usage

### Parse

```csharp
using Philterd.PhiSql;
using Philterd.PhiSql.Ast;

Document document = Parser.Parse("POLICY ssn_only; REDACT SSN WITH MASK;");
// document is the AST (see Ast.cs). Walk it, or use the compiler.
```

### Compile to Phileas JSON

```csharp
using Philterd.PhiSql;

CompileResult result = new Compiler().Compile(
    "POLICY hipaa_safe_harbor;\n" +
    "DEIDENTIFY SSN AS REDACT, DATE AS TRUNCATE, EMAIL_ADDRESS AS MASK;");

Console.WriteLine(result.PolicyName);      // "hipaa_safe_harbor"
Console.WriteLine(result.ToJsonString());  // Phileas JSON policy
```

### Compile from a file

```csharp
CompileResult result = new Compiler().CompileFile("policies/hipaa-safe-harbor.phisql");
// PolicyName is the filename basename; a POLICY declaration, if present, must
// match it after hyphen/underscore normalization, or a CompileException is thrown.
```

### Retrieve the policy schema

An application can read the canonical redaction policy JSON Schema straight from
the library, exactly as the Java (`PolicySchema.getSchema()`) and Python
(`PolicySchema.get_schema()`) references expose it:

```csharp
PolicySchema.GetSupportedSchemaVersion(); // "1.1.0"
PolicySchema.GetSchema();                  // the schema as a JSON string
PolicySchema.GetSchemaJson();              // the schema as a JsonNode
```

### Command line

```sh
dotnet run --project PhiSql.Cli -- path/to/policy.phisql
```

It writes the compiled Phileas JSON to stdout. Exit codes form the conformance
adapter contract: `0` success, `2` parse error, `3` compile error, `64` usage
error, `1` other I/O error.

## License

Apache License, Version 2.0. See [LICENSE](https://github.com/philterd/phisql/blob/main/LICENSE).
