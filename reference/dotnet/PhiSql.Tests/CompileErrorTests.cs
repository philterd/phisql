// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using System.Text.Json.Nodes;
using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>Verifies that well-formed-but-uncompilable PhiSQL throws CompileException.</summary>
public class CompileErrorTests
{
    [Fact]
    public void RejectsUnknownEntityType()
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile("REDACT NOT_AN_ENTITY WITH MASK;"));
        Assert.Contains("NOT_AN_ENTITY", ex.Message);
    }

    [Fact]
    public void PassesThroughUncataloguedStrategyArgument()
    {
        JsonNode strategy = new Compiler().Compile("REDACT SSN WITH MASK(salt=TRUE);")
            .PolicyJson["identifiers"]!["ssn"]!["ssnFilterStrategies"]![0]!;
        Assert.True(strategy["salt"]!.GetValue<bool>());
    }

    [Fact]
    public void RejectsInvalidEnumValue()
    {
        var ex = Assert.Throws<CompileException>(
            () => new Compiler().Compile("REDACT SSN WITH STATIC_REPLACE(value='X', scope=invalid);"));
        string m = ex.Message.ToLowerInvariant();
        Assert.True(m.Contains("scope") || m.Contains("invalid"), ex.Message);
    }

    [Fact]
    public void RejectsDateOnlyStrategyOnNonDateEntity()
    {
        var ex = Assert.Throws<CompileException>(
            () => new Compiler().Compile("REDACT SSN WITH SHIFT(days=30);"));
        Assert.Contains("SHIFT", ex.Message);
        Assert.Contains("date-only", ex.Message);
    }

    [Fact]
    public void AllowsDateOnlyStrategyOnDate()
    {
        // Positive control: a date-only strategy on DATE compiles.
        JsonNode strategy = new Compiler().Compile("REDACT DATE WITH SHIFT(days=30);")
            .PolicyJson["identifiers"]!["date"]!["dateFilterStrategies"]![0]!;
        Assert.Equal("SHIFT", strategy["strategy"]!.GetValue<string>());
    }

    [Fact]
    public void RejectsStaticReplaceWithoutValue()
    {
        // The catalog marks STATIC_REPLACE's `value` required; omitting it is a
        // semantic error rather than a malformed strategy.
        var ex = Assert.Throws<CompileException>(
            () => new Compiler().Compile("REDACT SURNAME WITH STATIC_REPLACE(scope=document);"));
        Assert.Contains("STATIC_REPLACE requires argument 'value'", ex.Message);
    }

    [Fact]
    public void AllowsStaticReplaceWithValue()
    {
        // Positive control: STATIC_REPLACE with a value compiles.
        JsonNode strategy = new Compiler().Compile("REDACT SURNAME WITH STATIC_REPLACE(value='Customer');")
            .PolicyJson["identifiers"]!["surname"]!["surnameFilterStrategies"]![0]!;
        Assert.Equal("Customer", strategy["staticReplacement"]!.GetValue<string>());
    }

    [Fact]
    public void RejectsDuplicateGeneratorName()
    {
        // Two DEFINE GENERATOR statements with the same name would collide in the
        // single name-keyed generators object; that is a semantic error.
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'A: {{token}}', timeoutMs = 1000);\n" +
            "DEFINE GENERATOR 'g' TYPE 'ollama' OPTIONS (prompt = 'B: {{token}}', timeoutMs = 1000);"));
        Assert.Contains("Duplicate generator name", ex.Message);
    }

    [Fact]
    public void AllowsTwoDistinctGenerators()
    {
        // Positive control: distinct names both land in the generators block.
        JsonNode generators = new Compiler().Compile(
            "DEFINE GENERATOR 'a' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);\n" +
            "DEFINE GENERATOR 'b' TYPE 'ollama' OPTIONS (prompt = '{{token}}', timeoutMs = 1000);")
            .PolicyJson["generators"]!;
        Assert.NotNull(generators["a"]);
        Assert.NotNull(generators["b"]);
    }

    [Fact]
    public void CompilesReviewSamplingRate()
    {
        var review = new Compiler().Compile("REDACT SSN WITH MASK;\nCONFIGURE review (samplingRate = 0.10);")
            .PolicyJson["config"]!["review"]!;
        Assert.Equal(0.1, review["samplingRate"]!.GetValue<double>());
    }

    [Fact]
    public void ReviewIsNotReserved()
    {
        // REVIEW is matched contextually, so it stays usable as an identifier.
        var policy = new Compiler().Compile("POLICY review;\nREDACT SSN WITH MASK;").PolicyJson;
        Assert.NotNull(policy["identifiers"]!["ssn"]);
    }

    [Theory]
    [InlineData("1.5")]
    [InlineData("-0.1")]
    [InlineData("2")]
    [InlineData("'half'")]
    [InlineData("TRUE")]
    public void RejectsSamplingRateOutOfRange(string rate)
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "REDACT SSN WITH MASK;\nCONFIGURE REVIEW (samplingRate = " + rate + ");"));
        Assert.Contains("samplingRate must be a number from 0.0 to 1.0", ex.Message);
    }

    [Fact]
    public void AcceptsIntegerSamplingRate()
    {
        var review = new Compiler().Compile("REDACT SSN WITH MASK;\nCONFIGURE REVIEW (samplingRate = 1);")
            .PolicyJson["config"]!["review"]!;
        Assert.Equal(1, review["samplingRate"]!.GetValue<long>());
    }

    [Fact]
    public void RejectsUnknownConfigBlock()
    {
        var ex = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "REDACT SSN WITH MASK;\nCONFIGURE AUDIT (samplingRate = 0.1);"));
        Assert.Contains("Unknown config block: AUDIT", ex.Message);
    }
}
