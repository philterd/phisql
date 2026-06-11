// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using System.Text.Json.Nodes;
using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>
/// Verifies the bundled schema is readable and that the reported version, the
/// schema's own <c>version</c>, and its <c>$id</c> agree — the assertion that
/// PolicySchema and the embedded resource cannot drift.
/// </summary>
public class PolicySchemaTests
{
    [Fact]
    public void VersionIsNonEmpty() =>
        Assert.False(string.IsNullOrWhiteSpace(PolicySchema.GetSupportedSchemaVersion()));

    [Fact]
    public void SchemaMatchesReportedVersion()
    {
        string schema = PolicySchema.GetSchema();
        Assert.False(string.IsNullOrWhiteSpace(schema));

        JsonNode root = JsonNode.Parse(schema)!;
        string version = PolicySchema.GetSupportedSchemaVersion();

        Assert.Equal(version, root["version"]!.GetValue<string>());
        Assert.Contains($"/{version}/", root["$id"]!.GetValue<string>());
    }

    [Fact]
    public void GetSchemaJsonMatchesString()
    {
        JsonNode fromJson = PolicySchema.GetSchemaJson();
        JsonNode fromString = JsonNode.Parse(PolicySchema.GetSchema())!;
        Assert.True(JsonNode.DeepEquals(fromJson, fromString));
    }
}
