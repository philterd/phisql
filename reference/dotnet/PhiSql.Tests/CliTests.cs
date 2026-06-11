// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using System.Text.Json.Nodes;
using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>
/// Verifies the CLI adapter contract: stdout carries the compiled JSON and the
/// exit code distinguishes success, parse failure, and compile failure.
/// </summary>
public class CliTests : IDisposable
{
    private readonly string _dir = Path.Combine(Path.GetTempPath(), "phisql-cli-" + Guid.NewGuid().ToString("N"));

    public CliTests() => Directory.CreateDirectory(_dir);

    public void Dispose() => Directory.Delete(_dir, recursive: true);

    private string Write(string name, string body)
    {
        string path = Path.Combine(_dir, name);
        File.WriteAllText(path, body);
        return path;
    }

    private static (int Code, string Out, string Err) Invoke(params string[] args)
    {
        var outw = new StringWriter();
        var errw = new StringWriter();
        int code = Cli.Run(args, outw, errw);
        return (code, outw.ToString(), errw.ToString());
    }

    [Fact]
    public void CompilesValidPolicyToJsonOnStdout()
    {
        string file = Write("ssn.phisql", "REDACT SSN WITH MASK;\n");
        var (code, output, err) = Invoke(file);
        Assert.Equal(Cli.ExitOk, code);
        Assert.True(string.IsNullOrEmpty(err), err);
        JsonNode json = JsonNode.Parse(output)!;
        Assert.Equal("MASK", json["identifiers"]!["ssn"]!["ssnFilterStrategies"]![0]!["strategy"]!.GetValue<string>());
    }

    [Fact]
    public void ParseErrorExitsWithParseCode()
    {
        string file = Write("bad.phisql", "POLICY x\nREDACT SSN WITH MASK;\n");
        var (code, _, err) = Invoke(file);
        Assert.Equal(Cli.ExitParseError, code);
        Assert.Contains("parse error", err);
    }

    [Fact]
    public void UnknownEntityExitsWithCompileCode()
    {
        string file = Write("sem.phisql", "REDACT NOT_AN_ENTITY WITH MASK;\n");
        var (code, _, err) = Invoke(file);
        Assert.Equal(Cli.ExitCompileError, code);
        Assert.Contains("compile error", err);
    }

    [Fact]
    public void PolicyNameMismatchExitsWithCompileCode()
    {
        string file = Write("mismatch.phisql", "POLICY something_else;\nREDACT SSN WITH MASK;\n");
        var (code, _, _) = Invoke(file);
        Assert.Equal(Cli.ExitCompileError, code);
    }

    [Fact]
    public void MissingArgumentIsUsageError()
    {
        var (code, _, err) = Invoke();
        Assert.Equal(Cli.ExitUsage, code);
        Assert.Contains("usage", err);
    }

    [Fact]
    public void MissingFileIsUsageError()
    {
        var (code, _, _) = Invoke(Path.Combine(_dir, "does-not-exist.phisql"));
        Assert.Equal(Cli.ExitUsage, code);
    }
}
