// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

namespace Philterd.PhiSql.Tests;

/// <summary>Locates the spec example pairs under spec/v1.0/examples relative to the test assembly.</summary>
internal static class TestPaths
{
    /// <summary>spec/v1.0/examples, found by walking up from the test output directory.</summary>
    public static string ExamplesDir { get; } = FindExamplesDir();

    /// <summary>
    /// Discovery examples parse but do not compile to a Phileas redaction policy;
    /// compilation/schema tests skip them (they are still parsed).
    /// </summary>
    public static readonly HashSet<string> Discovery = new()
    {
        "15-find-pii-s3", "16-discover-entities-gcs", "17-scan-azure-blob",
        "18-find-pii-local-filesystem", "19-select-findings-groupby",
    };

    public static IEnumerable<object[]> PhisqlFiles() =>
        Directory.GetFiles(ExamplesDir, "*.phisql").OrderBy(f => f).Select(f => new object[] { f });

    public static IEnumerable<object[]> JsonFiles() =>
        Directory.GetFiles(ExamplesDir, "*.json").OrderBy(f => f).Select(f => new object[] { f });

    public static IEnumerable<object[]> RedactionFiles() =>
        Directory.GetFiles(ExamplesDir, "*.phisql")
            .Where(f => !Discovery.Contains(Path.GetFileNameWithoutExtension(f)))
            .OrderBy(f => f).Select(f => new object[] { f });

    public static IEnumerable<object[]> DiscoveryFiles() =>
        Directory.GetFiles(ExamplesDir, "*.phisql")
            .Where(f => Discovery.Contains(Path.GetFileNameWithoutExtension(f)))
            .OrderBy(f => f).Select(f => new object[] { f });

    private static string FindExamplesDir()
    {
        DirectoryInfo? dir = new(AppContext.BaseDirectory);
        while (dir is not null)
        {
            string candidate = Path.Combine(dir.FullName, "spec", "v1.0", "examples");
            if (Directory.Exists(candidate)) return candidate;
            dir = dir.Parent;
        }
        throw new DirectoryNotFoundException(
            "Could not locate spec/v1.0/examples above " + AppContext.BaseDirectory);
    }
}
