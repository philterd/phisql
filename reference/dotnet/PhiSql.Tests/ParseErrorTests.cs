// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using System.Text.RegularExpressions;
using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>Verifies that malformed PhiSQL throws ParseException with line:column.</summary>
public class ParseErrorTests
{
    private static void AssertHasLineAndColumn(ParseException ex) =>
        Assert.True(Regex.IsMatch(ex.Message, @"^line \d+:\d+"),
            $"Expected 'line N:M' format, got: {ex.Message}");

    [Fact]
    public void RejectsUnknownStatementKeyword() =>
        AssertHasLineAndColumn(Assert.Throws<ParseException>(() => Parser.Parse("REDAKT SSN WITH MASK;")));

    [Fact]
    public void RejectsUnknownStrategyName() =>
        AssertHasLineAndColumn(Assert.Throws<ParseException>(() => Parser.Parse("REDACT SSN WITH NOTASTRATEGY;")));

    [Fact]
    public void RejectsMissingSemicolon() =>
        AssertHasLineAndColumn(Assert.Throws<ParseException>(() => Parser.Parse("REDACT SSN WITH MASK")));

    [Fact]
    public void RejectsMalformedNamedArg() =>
        AssertHasLineAndColumn(Assert.Throws<ParseException>(() => Parser.Parse("REDACT SSN WITH MASK(=value);")));

    [Fact]
    public void RejectsCustomIdentifierWithoutClassification() =>
        AssertHasLineAndColumn(Assert.Throws<ParseException>(() => Parser.Parse("REDACT IDENTIFIER WITH MASK;")));

    [Fact]
    public void ErrorMessageReportsCorrectLineNumber()
    {
        const string source = "POLICY support_tickets;\nREDACT SSN WITH MASK;\nREDAKT EMAIL_ADDRESS WITH MASK;\n";
        var ex = Assert.Throws<ParseException>(() => Parser.Parse(source));
        Assert.Contains("line 3:", ex.Message);
    }
}
