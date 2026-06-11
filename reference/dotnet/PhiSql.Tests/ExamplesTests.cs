// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using System.Text.Json.Nodes;
using Json.Schema;
using Philterd.PhiSql.Ast;
using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>
/// Parses every example, compiles every redaction example and compares it to the
/// sibling .json fixture, and validates both against the canonical schema —
/// the load-bearing assertions that this implementation stays in sync with the
/// spec, mirroring the Java and Python reference test suites.
/// </summary>
public class ExamplesTests
{
    private static readonly EvaluationOptions SchemaOpts = new() { OutputFormat = OutputFormat.List };
    private static readonly JsonSchema Schema = JsonSchema.FromText(PolicySchema.GetSchema());

    [Theory]
    [MemberData(nameof(TestPaths.PhisqlFiles), MemberType = typeof(TestPaths))]
    public void EveryExampleParses(string path)
    {
        // Should not throw.
        Document doc = Parser.Parse(File.ReadAllText(path));
        Assert.NotEmpty(doc.Statements);
    }

    [Theory]
    [MemberData(nameof(TestPaths.RedactionFiles), MemberType = typeof(TestPaths))]
    public void CompiledExampleMatchesFixture(string path)
    {
        CompileResult result = new Compiler().Compile(File.ReadAllText(path));
        JsonNode? actual = JsonNode.Parse(result.ToJsonString());
        JsonNode? expected = JsonNode.Parse(File.ReadAllText(Path.ChangeExtension(path, ".json")));

        Assert.True(JsonNode.DeepEquals(actual, expected),
            $"{Path.GetFileName(path)} did not match its .json fixture.\n" +
            $"actual:   {actual?.ToJsonString()}\n" +
            $"expected: {expected?.ToJsonString()}");
        Assert.NotNull(result.PolicyName);
    }

    [Theory]
    [MemberData(nameof(TestPaths.RedactionFiles), MemberType = typeof(TestPaths))]
    public void CompiledExampleIsSchemaValid(string path)
    {
        JsonNode node = JsonNode.Parse(new Compiler().Compile(File.ReadAllText(path)).ToJsonString())!;
        EvaluationResults results = Schema.Evaluate(node, SchemaOpts);
        Assert.True(results.IsValid, $"Compiled {Path.GetFileName(path)} is not schema-valid");
    }

    [Theory]
    [MemberData(nameof(TestPaths.RedactionFiles), MemberType = typeof(TestPaths))]
    public void FixtureIsSchemaValid(string path)
    {
        JsonNode node = JsonNode.Parse(File.ReadAllText(Path.ChangeExtension(path, ".json")))!;
        EvaluationResults results = Schema.Evaluate(node, SchemaOpts);
        Assert.True(results.IsValid, $"Fixture for {Path.GetFileName(path)} is not schema-valid");
    }

    [Theory]
    [MemberData(nameof(TestPaths.JsonFiles), MemberType = typeof(TestPaths))]
    public void EveryJsonHasPhisqlSibling(string jsonPath)
    {
        Assert.True(File.Exists(Path.ChangeExtension(jsonPath, ".phisql")),
            $"{Path.GetFileName(jsonPath)} has no sibling .phisql");
    }

    [Theory]
    [MemberData(nameof(TestPaths.DiscoveryFiles), MemberType = typeof(TestPaths))]
    public void DiscoveryExampleParsesToDiscoveryStatement(string path)
    {
        Document doc = Parser.Parse(File.ReadAllText(path));
        Assert.Contains(doc.Statements, s => s is DiscoveryStmt);
    }
}
