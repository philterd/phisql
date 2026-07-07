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
}
