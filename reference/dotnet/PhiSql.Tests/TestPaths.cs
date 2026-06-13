// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

namespace Philterd.PhiSql.Tests;

/// <summary>Locates the spec example pairs under spec/v1.0/examples and spec/v1.1.0/examples relative to the test assembly.</summary>
internal static class TestPaths
{
    /// <summary>spec/v1.0/examples, found by walking up from the test output directory.</summary>
    public static string ExamplesDir { get; } = FindExamplesDir("v1.0")
        ?? throw new DirectoryNotFoundException("Could not locate spec/v1.0/examples above " + AppContext.BaseDirectory);

    /// <summary>Every spec-version examples directory the tests scan.</summary>
    private static readonly string[] AllExamplesDirs =
        new[] { FindExamplesDir("v1.0"), FindExamplesDir("v1.1.0") }
            .Where(d => d is not null).Select(d => d!).ToArray();

    /// <summary>
    /// Discovery examples parse but do not compile to a Phileas redaction policy;
    /// compilation/schema tests skip them (they are still parsed).
    /// </summary>
    public static readonly HashSet<string> Discovery = new()
    {
        "15-find-pii-s3", "16-discover-entities-gcs", "17-scan-azure-blob",
        "18-find-pii-local-filesystem", "19-select-findings-groupby",
    };

    private static IEnumerable<string> AllFiles(string pattern) =>
        AllExamplesDirs.SelectMany(d => Directory.GetFiles(d, pattern)).OrderBy(f => f);

    public static IEnumerable<object[]> PhisqlFiles() =>
        AllFiles("*.phisql").Select(f => new object[] { f });

    public static IEnumerable<object[]> JsonFiles() =>
        AllFiles("*.json").Select(f => new object[] { f });

    public static IEnumerable<object[]> RedactionFiles() =>
        AllFiles("*.phisql")
            .Where(f => !Discovery.Contains(Path.GetFileNameWithoutExtension(f)))
            .Select(f => new object[] { f });

    public static IEnumerable<object[]> DiscoveryFiles() =>
        AllFiles("*.phisql")
            .Where(f => Discovery.Contains(Path.GetFileNameWithoutExtension(f)))
            .Select(f => new object[] { f });

    private static string? FindExamplesDir(string version)
    {
        DirectoryInfo? dir = new(AppContext.BaseDirectory);
        while (dir is not null)
        {
            string candidate = Path.Combine(dir.FullName, "spec", version, "examples");
            if (Directory.Exists(candidate)) return candidate;
            dir = dir.Parent;
        }
        return null;
    }
}
