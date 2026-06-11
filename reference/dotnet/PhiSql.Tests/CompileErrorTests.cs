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
}
