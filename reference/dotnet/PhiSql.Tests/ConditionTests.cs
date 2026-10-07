// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>
/// Verifies how WHERE predicates compile to Phileas conditions (RFC #58): `=` is
/// emitted as `==`, and OR and parentheses produce a compile warning.
/// </summary>
public class ConditionTests
{
    private static string Condition(CompileResult result) =>
        result.PolicyJson["identifiers"]!["ssn"]!["ssnFilterStrategies"]![0]!["condition"]!.GetValue<string>();

    [Fact]
    public void EqualsCompilesToDoubleEquals()
    {
        CompileResult r = new Compiler().Compile("REDACT SSN WITH MASK WHERE CONFIDENCE = 0.75;");
        Assert.Equal("confidence == 0.75", Condition(r));
        Assert.Empty(r.Warnings);
    }

    [Theory]
    [InlineData(">")]
    [InlineData(">=")]
    [InlineData("<")]
    [InlineData("<=")]
    public void OtherOperatorsAreUnchanged(string op)
    {
        CompileResult r = new Compiler().Compile($"REDACT SSN WITH MASK WHERE CONFIDENCE {op} 0.5;");
        Assert.Equal($"confidence {op} 0.5", Condition(r));
    }

    [Fact]
    public void AndDoesNotWarn()
    {
        CompileResult r = new Compiler().Compile("REDACT SSN WITH MASK WHERE CONFIDENCE > 0.5 AND CONFIDENCE < 0.9;");
        Assert.Equal("confidence > 0.5 and confidence < 0.9", Condition(r));
        Assert.Empty(r.Warnings);
    }

    [Fact]
    public void OrWarns()
    {
        CompileResult r = new Compiler().Compile("REDACT SSN WITH MASK WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;");
        Assert.Equal(new[] { Compiler.OrWarning }, r.Warnings);
    }

    [Fact]
    public void ParenthesesAndOrWarnOnceEachPerDocument()
    {
        CompileResult r = new Compiler().Compile(
            "REDACT SSN WITH MASK WHERE (CONFIDENCE > 0.5 AND CONFIDENCE < 0.9) OR CONFIDENCE = 1.0;\n"
            + "REDACT EIN WITH MASK WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;");
        Assert.Equal(new[] { Compiler.OrWarning, Compiler.ParenWarning }, r.Warnings);
    }

    [Fact]
    public void DetectAndDefineIdentifierPredicatesAreScanned()
    {
        CompileResult detect = new Compiler().Compile("DETECT PHEYE WITH REDACT WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;");
        Assert.Equal(new[] { Compiler.OrWarning }, detect.Warnings);
        CompileResult identifier = new Compiler().Compile(
            "DEFINE IDENTIFIER 'acct' MATCHING '\\d{6}' WITH REDACT WHERE (CONFIDENCE > 0.5);");
        Assert.Equal(new[] { Compiler.ParenWarning }, identifier.Warnings);
    }
}
