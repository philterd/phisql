// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>
/// Verifies the policy-naming rule from spec/v1.0/catalog/policy.yaml: POLICY is
/// optional; when a filename and POLICY are both present they must match after
/// hyphen/underscore normalization; otherwise the basename names the policy.
/// </summary>
public class PolicyNamingTests : IDisposable
{
    private readonly Compiler _compiler = new();
    private readonly string _dir = Path.Combine(Path.GetTempPath(), "phisql-" + Guid.NewGuid().ToString("N"));

    public PolicyNamingTests() => Directory.CreateDirectory(_dir);

    public void Dispose() => Directory.Delete(_dir, recursive: true);

    private string Write(string filename, string contents)
    {
        string path = Path.Combine(_dir, filename);
        File.WriteAllText(path, contents);
        return path;
    }

    [Fact]
    public void FilenameProvidesNameWhenPolicyOmitted()
    {
        string file = Write("hipaa-safe-harbor.phisql", "REDACT SSN WITH MASK;");
        Assert.Equal("hipaa-safe-harbor", _compiler.CompileFile(file).PolicyName);
    }

    [Fact]
    public void MatchingPolicyDeclarationCompiles()
    {
        string file = Write("ssn_only.phisql", "POLICY ssn_only; REDACT SSN WITH MASK;");
        Assert.Equal("ssn_only", _compiler.CompileFile(file).PolicyName);
    }

    [Fact]
    public void MismatchedPolicyDeclarationThrows()
    {
        string file = Write("whatever.phisql", "POLICY hipaa_safe_harbor; REDACT SSN WITH MASK;");
        Assert.Throws<CompileException>(() => _compiler.CompileFile(file));
    }

    [Fact]
    public void HyphenUnderscoreNormalization()
    {
        string file = Write("hipaa-safe-harbor.phisql", "POLICY hipaa_safe_harbor; REDACT SSN WITH MASK;");
        Assert.Equal("hipaa-safe-harbor", _compiler.CompileFile(file).PolicyName);
    }

    [Fact]
    public void StringOnlyWithoutPolicyIsNull() =>
        Assert.Null(_compiler.Compile("REDACT SSN WITH MASK;").PolicyName);

    [Fact]
    public void StringOnlyWithPolicyUsesDeclaredName() =>
        Assert.Equal("foo", _compiler.Compile("POLICY foo; REDACT SSN WITH MASK;").PolicyName);

    [Fact]
    public void ExplicitExpectedNameOverridesNullDeclaration() =>
        Assert.Equal("ssn_only", _compiler.Compile("REDACT SSN WITH MASK;", "ssn_only").PolicyName);

    [Fact]
    public void ExplicitExpectedNameMustMatchDeclaration()
    {
        var ex = Assert.Throws<CompileException>(
            () => _compiler.Compile("POLICY hipaa_safe_harbor; REDACT SSN WITH MASK;", "different_name"));
        Assert.Contains("hipaa_safe_harbor", ex.Message);
    }

    [Fact]
    public void DescriptionIsExtracted()
    {
        string file = Write("test_policy.phisql",
            "POLICY test_policy DESCRIPTION 'A policy for X.'; REDACT SSN WITH MASK;");
        Assert.Equal("A policy for X.", _compiler.CompileFile(file).Description);
    }
}
