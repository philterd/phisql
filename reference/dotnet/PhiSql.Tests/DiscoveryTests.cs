// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>
/// Verifies how the compiler reports discovery statements, which it does not
/// compile yet (#71): each one is skipped with a warning naming it and its line,
/// and a script with nothing else is a compile error rather than an empty policy.
/// </summary>
public class DiscoveryTests
{
    [Fact]
    public void DiscoveryOnlyScriptIsACompileError()
    {
        var e = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "FIND PII IN 's3://prod-data/customers/'\n"
            + "  WHERE entity_type IN ('SSN', 'CREDIT_CARD');\n"
            + "SCAN IN 'file:///mnt/exports/';\n"));
        Assert.Equal("The script has only discovery statements (FIND PII at line 1, SCAN at line 3), "
            + "and discovery statements are not compiled to a redaction policy yet.", e.Message);
    }

    [Fact]
    public void PolicyDeclarationAloneDoesNotMakeADiscoveryScriptCompile()
    {
        var e = Assert.Throws<CompileException>(() => new Compiler().Compile(
            "POLICY findings_report;\n"
            + "SELECT path, entity_type, COUNT(*) FROM phinder.findings GROUP BY path, entity_type;\n"));
        Assert.Equal("The script has only discovery statements (SELECT ... FROM findings at line 2), "
            + "and discovery statements are not compiled to a redaction policy yet.", e.Message);
    }

    [Fact]
    public void MixedScriptCompilesTheRedactionStatementsAndWarnsForEachDiscoveryStatement()
    {
        CompileResult r = new Compiler().Compile(
            "FIND PII IN 's3://prod-data/customers/';\n"
            + "REDACT SSN WITH MASK WHERE CONFIDENCE < 0.2 OR CONFIDENCE > 0.9;\n"
            + "\n"
            + "DISCOVER ENTITIES IN 'gs://archive/';\n");
        Assert.Equal("MASK",
            r.PolicyJson["identifiers"]!["ssn"]!["ssnFilterStrategies"]![0]!["strategy"]!.GetValue<string>());
        Assert.Equal(new[]
        {
            "FIND PII at line 1 was skipped: " + Compiler.DiscoveryWarning,
            "DISCOVER ENTITIES at line 4 was skipped: " + Compiler.DiscoveryWarning,
            Compiler.OrWarning,
        }, r.Warnings);
    }
}
