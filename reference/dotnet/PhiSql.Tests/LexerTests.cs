// Copyright 2026 Philterd, LLC.
//
// Licensed under the Apache License, Version 2.0 (the "License").
// See ../../../LICENSE.

using System.Text.RegularExpressions;
using Xunit;

namespace Philterd.PhiSql.Tests;

/// <summary>
/// Unit tests for the hand-written lexer (the part the ANTLR-generated Java
/// lexer does not exercise directly): keyword case-folding, maximal munch,
/// comments, string/number forms, operators, and lexical error reporting.
/// </summary>
public class LexerTests
{
    private static string[] Types(string s) =>
        Lexer.Tokenize(s).Where(t => t.Type != "EOF").Select(t => t.Type).ToArray();

    private static string[] Texts(string s) =>
        Lexer.Tokenize(s).Where(t => t.Type != "EOF").Select(t => t.Text).ToArray();

    [Fact]
    public void KeywordsAreCaseInsensitive()
    {
        Assert.Equal(new[] { "REDACT", "REDACT", "REDACT" }, Types("REDACT redact ReDaCt"));
        Assert.Equal(new[] { "MASK", "MASK", "MASK" }, Types("mask MASK Mask"));
    }

    [Fact]
    public void IdentifiersPreserveCase() =>
        Assert.Equal(new[] { "SSN", "email_Address" }, Texts("SSN email_Address"));

    [Fact]
    public void MaximalMunchDistinguishesKeywordFromIdentifier()
    {
        Assert.Equal(new[] { "MASK", "ID" }, Types("MASK MASKED"));
        Assert.Equal(new[] { "TRUNCATE_TO_YEAR", "TRUNCATE" }, Types("TRUNCATE_TO_YEAR TRUNCATE"));
    }

    [Fact]
    public void BooleanLiterals() =>
        Assert.Equal(new[] { "BOOLEAN_LITERAL", "BOOLEAN_LITERAL", "BOOLEAN_LITERAL" }, Types("TRUE false True"));

    [Fact]
    public void IdentifierKeywordToken() => Assert.Equal(new[] { "IDENTIFIER" }, Types("IDENTIFIER"));

    [Fact]
    public void LineCommentSkipped() => Assert.Equal(new[] { "REDACT", "ID" }, Types("REDACT -- a comment\nSSN"));

    [Fact]
    public void BlockCommentSkipped() => Assert.Equal(new[] { "REDACT", "ID" }, Types("REDACT /* multi\nline */ SSN"));

    [Fact]
    public void StringLiteralKeepsQuotesAndEscapesRaw() => Assert.Equal(new[] { @"'O\'Brien'" }, Texts(@"'O\'Brien'"));

    [Fact]
    public void IntegerAndDecimalLiterals() => Assert.Equal(new[] { "30", "0.85" }, Texts("30 0.85"));

    [Fact]
    public void NegativeNumericLiteral() => Assert.Equal(new[] { "=", "-30" }, Texts("=-30"));

    [Fact]
    public void TwoCharOperatorsBeatSingle() =>
        Assert.Equal(new[] { ">=", "<=", ">", "<", "=" }, Types(">= <= > < ="));

    [Fact]
    public void PunctuationTokens() =>
        Assert.Equal(new[] { "(", ")", ",", ";", "[", "]", ".", "*" }, Types("( ) , ; [ ] . *"));

    [Fact]
    public void UnterminatedStringIsError() => AssertLineCol(Assert.Throws<ParseException>(() => Lexer.Tokenize("'oops")));

    [Fact]
    public void RawNewlineInStringIsError() => AssertLineCol(Assert.Throws<ParseException>(() => Lexer.Tokenize("'a\nb'")));

    [Fact]
    public void UnterminatedBlockCommentIsError() => AssertLineCol(Assert.Throws<ParseException>(() => Lexer.Tokenize("/* never closed")));

    [Fact]
    public void UnrecognizedCharacterIsError() => AssertLineCol(Assert.Throws<ParseException>(() => Lexer.Tokenize("REDACT SSN @ MASK;")));

    [Fact]
    public void ErrorReportsCorrectLineAndColumn()
    {
        var ex = Assert.Throws<ParseException>(() => Lexer.Tokenize("REDACT\nSSN @"));
        Assert.Contains("line 2:4", ex.Message);
    }

    private static void AssertLineCol(ParseException ex) =>
        Assert.True(Regex.IsMatch(ex.Message, @"^line \d+:\d+"), ex.Message);
}
