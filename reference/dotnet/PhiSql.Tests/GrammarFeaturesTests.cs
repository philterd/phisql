// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using System.Text.Json.Nodes;
using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>
/// Compiler/parser coverage for grammar features the spec examples do not
/// exercise: string escapes, negative/decimal numbers, every predicate operator
/// and shape, DETECT ... ENDPOINT, multi-statement accumulation, and the
/// scoped-IGNORE error paths.
/// </summary>
public class GrammarFeaturesTests
{
    private static JsonNode Strategy(string src, string field, string strategiesField, int index = 0)
    {
        JsonNode ids = new Compiler().Compile(src).PolicyJson["identifiers"]!;
        return ids[field]![strategiesField]![index]!;
    }

    [Fact]
    public void LowercaseKeywordsCompile()
    {
        JsonNode s = Strategy("redact ssn with mask;", "ssn", "ssnFilterStrategies");
        Assert.Equal("MASK", s["strategy"]!.GetValue<string>());
    }

    [Fact]
    public void EscapedSingleQuoteIsUnquoted()
    {
        JsonNode s = Strategy(@"REDACT SSN WITH STATIC_REPLACE(value='O\'Brien');", "ssn", "ssnFilterStrategies");
        Assert.Equal("O'Brien", s["staticReplacement"]!.GetValue<string>());
    }

    [Fact]
    public void EscapedNewlineIsUnquoted()
    {
        JsonNode s = Strategy(@"REDACT SSN WITH STATIC_REPLACE(value='a\nb');", "ssn", "ssnFilterStrategies");
        Assert.Equal("a\nb", s["staticReplacement"]!.GetValue<string>());
    }

    [Fact]
    public void EscapedBackslashIsCollapsed()
    {
        JsonNode s = Strategy(@"REDACT SSN WITH STATIC_REPLACE(value='a\\b');", "ssn", "ssnFilterStrategies");
        Assert.Equal(@"a\b", s["staticReplacement"]!.GetValue<string>());
    }

    [Fact]
    public void NegativeIntegerArgument()
    {
        JsonNode s = Strategy("REDACT DATE WITH SHIFT(days=-30);", "date", "dateFilterStrategies");
        Assert.Equal(-30, s["shiftDays"]!.GetValue<long>());
    }

    [Fact]
    public void DecimalPassthroughArgument()
    {
        JsonNode s = Strategy("REDACT SSN WITH MASK(weight=0.25);", "ssn", "ssnFilterStrategies");
        Assert.Equal(0.25, s["weight"]!.GetValue<double>());
    }

    [Fact]
    public void EqualsComparisonOperator()
    {
        JsonNode s = Strategy("REDACT SSN WITH MASK WHERE CONFIDENCE = 0.5;", "ssn", "ssnFilterStrategies");
        Assert.Equal("confidence = 0.5", s["condition"]!.GetValue<string>());
    }

    [Fact]
    public void ParenthesisedAndPredicate()
    {
        JsonNode s = Strategy("REDACT SSN WITH MASK WHERE (CONFIDENCE > 0.5) AND CONFIDENCE < 0.9;",
            "ssn", "ssnFilterStrategies");
        Assert.Equal("( confidence > 0.5 ) and confidence < 0.9", s["condition"]!.GetValue<string>());
    }

    [Fact]
    public void OrPredicate()
    {
        JsonNode s = Strategy("REDACT SSN WITH MASK WHERE CONFIDENCE > 0.9 OR CONFIDENCE < 0.1;",
            "ssn", "ssnFilterStrategies");
        Assert.Equal("confidence > 0.9 or confidence < 0.1", s["condition"]!.GetValue<string>());
    }

    [Fact]
    public void DetectEndpointAndLabels()
    {
        JsonNode pheye = new Compiler()
            .Compile("DETECT PHEYE LABELS ('PER') ENDPOINT 'http://pheye:8080' WITH REDACT;")
            .PolicyJson["identifiers"]!["pheyes"]![0]!;
        JsonNode config = pheye["phEyeConfiguration"]!;
        Assert.Equal("http://pheye:8080", config["endpoint"]!.GetValue<string>());
        Assert.Equal("PER", config["labels"]![0]!.GetValue<string>());
    }

    [Fact]
    public void StrategiesAccumulateAcrossStatements()
    {
        JsonNode strategies = new Compiler()
            .Compile("REDACT EMAIL_ADDRESS WITH HASH_SHA256;\nREDACT EMAIL_ADDRESS WITH MASK;")
            .PolicyJson["identifiers"]!["emailAddress"]!["emailAddressFilterStrategies"]!;
        Assert.Equal(2, strategies.AsArray().Count);
        Assert.Equal("HASH_SHA256_REPLACE", strategies[0]!["strategy"]!.GetValue<string>());
        Assert.Equal("MASK", strategies[1]!["strategy"]!.GetValue<string>());
    }

    [Fact]
    public void CustomIdentifierReusesEntryByClassification()
    {
        JsonNode identifiers = new Compiler()
            .Compile("REDACT IDENTIFIER('acct') WITH LAST_4;\nREDACT IDENTIFIER('acct') WITH MASK;")
            .PolicyJson["identifiers"]!["identifiers"]!;
        Assert.Single(identifiers.AsArray());
        Assert.Equal("acct", identifiers[0]!["classification"]!.GetValue<string>());
        Assert.Equal(2, identifiers[0]!["identifierFilterStrategies"]!.AsArray().Count);
    }

    [Fact]
    public void ScopedIgnoreWithOptionsIsRejected()
    {
        var ex = Assert.Throws<CompileException>(
            () => new Compiler().Compile("IGNORE TERMS ('x') FOR SSN OPTIONS (name='n');"));
        Assert.Contains("OPTIONS is not supported on a scoped IGNORE", ex.Message);
    }

    [Fact]
    public void IgnoreScopedToCustomIdentifierIsRejected() =>
        Assert.Throws<CompileException>(() => new Compiler().Compile(
            "DEFINE IDENTIFIER 'acct' MATCHING '[0-9]+' WITH MASK;\nIGNORE TERMS ('x') FOR IDENTIFIER('acct');"));

    [Fact]
    public void ScopelessIgnoreTermsGoesToTopLevel()
    {
        JsonNode policy = new Compiler().Compile("IGNORE TERMS ('a', 'b');").PolicyJson;
        Assert.Equal("a", policy["ignored"]![0]!["terms"]![0]!.GetValue<string>());
        Assert.Equal("b", policy["ignored"]![0]!["terms"]![1]!.GetValue<string>());
    }

    [Fact]
    public void ScopelessIgnorePatternGoesToTopLevel()
    {
        JsonNode policy = new Compiler().Compile("IGNORE PATTERN '[0-9]+';").PolicyJson;
        Assert.Equal("[0-9]+", policy["ignoredPatterns"]![0]!["pattern"]!.GetValue<string>());
    }
}
